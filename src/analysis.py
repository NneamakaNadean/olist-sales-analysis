"""
analysis.py
-----------
Reusable analysis and visualization functions for the
Olist E-Commerce Business Intelligence project.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from datetime import datetime


# ─────────────────────────────────────────────
# PLOT STYLE
# ─────────────────────────────────────────────

def set_style():
    """Apply a consistent visual style to all charts."""
    sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor":   "white",
        "axes.spines.top":  False,
        "axes.spines.right": False,
    })


PALETTE = {
    "primary":   "#2563EB",
    "secondary": "#10B981",
    "accent":    "#F59E0B",
    "danger":    "#EF4444",
    "neutral":   "#6B7280",
}


# ─────────────────────────────────────────────
# 1. REVENUE ANALYSIS
# ─────────────────────────────────────────────

def monthly_revenue(master: pd.DataFrame) -> pd.DataFrame:
    """Aggregate revenue and order count by year-month."""
    df = (
        master
        .groupby("order_yearmonth")
        .agg(
            revenue=("payment_value", "sum"),
            orders=("order_id", "nunique"),
            avg_order_value=("payment_value", "mean"),
        )
        .reset_index()
    )
    df["order_yearmonth"] = df["order_yearmonth"].astype(str)
    df["revenue_growth_pct"] = df["revenue"].pct_change() * 100
    return df


def plot_monthly_revenue(monthly: pd.DataFrame, save_path: str = None):
    """Line chart: monthly revenue trend."""
    set_style()
    fig, ax = plt.subplots(figsize=(14, 5))

    ax.plot(monthly["order_yearmonth"], monthly["revenue"],
            marker="o", linewidth=2.5, color=PALETTE["primary"], markersize=4)
    ax.fill_between(monthly["order_yearmonth"], monthly["revenue"],
                    alpha=0.12, color=PALETTE["primary"])

    ax.set_title("Monthly Revenue Trend", fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (R$)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R${x:,.0f}"))
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"💾 Chart saved → {save_path}")
    plt.show()


def plot_payment_methods(master: pd.DataFrame, save_path: str = None):
    """Pie chart: revenue share by payment type."""
    set_style()
    pay_summary = (
        master
        .groupby("payment_type")["payment_value"]
        .sum()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        pay_summary,
        labels=pay_summary.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=sns.color_palette("muted", len(pay_summary)),
    )
    ax.set_title("Revenue by Payment Method", fontsize=15, fontweight="bold")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


# ─────────────────────────────────────────────
# 2. RFM CUSTOMER SEGMENTATION
# ─────────────────────────────────────────────

def build_rfm(master: pd.DataFrame, snapshot_date: datetime = None) -> pd.DataFrame:
    """
    Compute RFM scores for each unique customer.

    Parameters
    ----------
    master : merged master DataFrame
    snapshot_date : reference date (defaults to max order date + 1 day)

    Returns
    -------
    DataFrame with columns: customer_unique_id, recency, frequency,
    monetary, r_score, f_score, m_score, rfm_score, segment
    """
    if snapshot_date is None:
        snapshot_date = master["order_purchase_timestamp"].max() + pd.Timedelta(days=1)

    rfm = (
        master
        .groupby("customer_unique_id")
        .agg(
            last_purchase=("order_purchase_timestamp", "max"),
            frequency=("order_id", "nunique"),
            monetary=("payment_value", "sum"),
        )
        .reset_index()
    )
    rfm["recency"] = (snapshot_date - rfm["last_purchase"]).dt.days

    # Score each dimension 1–4 (4 = best)
    rfm["r_score"] = pd.qcut(rfm["recency"],  q=4, labels=[4, 3, 2, 1])
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=4, labels=[1, 2, 3, 4])
    rfm["m_score"] = pd.qcut(rfm["monetary"],  q=4, labels=[1, 2, 3, 4])

    rfm["rfm_score"] = (
        rfm["r_score"].astype(int)
        + rfm["f_score"].astype(int)
        + rfm["m_score"].astype(int)
    )

    # Assign human-readable segments
    def segment(row):
        r, f, m = int(row["r_score"]), int(row["f_score"]), int(row["m_score"])
        if r >= 4 and f >= 3 and m >= 3:
            return "VIP"
        elif r >= 3 and f >= 3:
            return "Loyal"
        elif r >= 3 and f <= 2:
            return "New"
        elif r <= 2 and f >= 3:
            return "At Risk"
        else:
            return "One-Time"

    rfm["segment"] = rfm.apply(segment, axis=1)
    return rfm


def plot_rfm_segments(rfm: pd.DataFrame, save_path: str = None):
    """Bar chart: customer count and revenue by RFM segment."""
    set_style()
    seg_summary = (
        rfm
        .groupby("segment")
        .agg(customers=("customer_unique_id", "count"), revenue=("monetary", "sum"))
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    sns.barplot(data=seg_summary, x="segment", y="customers",
                palette="Blues_d", ax=ax1)
    ax1.set_title("Customers by Segment", fontweight="bold")
    ax1.set_xlabel("")
    ax1.set_ylabel("Customer Count")

    sns.barplot(data=seg_summary, x="segment", y="revenue",
                palette="Greens_d", ax=ax2)
    ax2.set_title("Revenue by Segment", fontweight="bold")
    ax2.set_xlabel("")
    ax2.set_ylabel("Revenue (R$)")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R${x/1e6:.1f}M"))

    plt.suptitle("RFM Customer Segmentation", fontsize=16, fontweight="bold", y=1.02)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


# ─────────────────────────────────────────────
# 3. PRODUCT ANALYSIS
# ─────────────────────────────────────────────

def top_categories(master: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return top N product categories by total revenue."""
    return (
        master
        .groupby("category_en")
        .agg(
            revenue=("payment_value", "sum"),
            orders=("order_id", "nunique"),
            units_sold=("order_item_id", "count"),
            avg_price=("price", "mean"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
        .head(n)
    )


def plot_top_categories(master: pd.DataFrame, n: int = 10, save_path: str = None):
    """Horizontal bar chart: top N categories by revenue."""
    set_style()
    cats = top_categories(master, n).sort_values("revenue")

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(cats["category_en"], cats["revenue"],
                   color=PALETTE["primary"], alpha=0.85)
    ax.bar_label(bars, labels=[f"R${v/1e3:.0f}k" for v in cats["revenue"]],
                 padding=5, fontsize=9)
    ax.set_title(f"Top {n} Product Categories by Revenue", fontsize=15, fontweight="bold")
    ax.set_xlabel("Revenue (R$)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R${x/1e3:.0f}k"))
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


# ─────────────────────────────────────────────
# 4. GEOGRAPHIC ANALYSIS
# ─────────────────────────────────────────────

def revenue_by_state(master: pd.DataFrame) -> pd.DataFrame:
    """Aggregate revenue and customer count by Brazilian state."""
    return (
        master
        .groupby("customer_state")
        .agg(
            revenue=("payment_value", "sum"),
            orders=("order_id", "nunique"),
            customers=("customer_unique_id", "nunique"),
            avg_order_value=("payment_value", "mean"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )


def plot_revenue_by_state(master: pd.DataFrame, top_n: int = 15, save_path: str = None):
    """Bar chart: revenue by state (top N)."""
    set_style()
    state_df = revenue_by_state(master).head(top_n)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=state_df, x="customer_state", y="revenue",
                palette="Blues_d", ax=ax)
    ax.set_title(f"Revenue by State (Top {top_n})", fontsize=15, fontweight="bold")
    ax.set_xlabel("State")
    ax.set_ylabel("Revenue (R$)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R${x/1e6:.1f}M"))
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


# ─────────────────────────────────────────────
# 5. PROFITABILITY MODEL
# ─────────────────────────────────────────────

# Assumptions (adjust as needed)
COST_ASSUMPTIONS = {
    "product_cost_pct": 0.60,   # 60% of revenue
    "shipping_pct":     0.10,   # 10% of revenue
    "marketing_pct":    0.05,   # 5%  of revenue
}


def estimate_profitability(master: pd.DataFrame) -> pd.DataFrame:
    """
    Add estimated cost and profit columns to master DataFrame.
    Uses configurable percentage assumptions (see COST_ASSUMPTIONS).
    """
    df = master.copy()
    rev = df["payment_value"]
    df["est_product_cost"] = rev * COST_ASSUMPTIONS["product_cost_pct"]
    df["est_shipping_cost"] = rev * COST_ASSUMPTIONS["shipping_pct"]
    df["est_marketing_cost"] = rev * COST_ASSUMPTIONS["marketing_pct"]
    df["est_total_cost"]   = (
        df["est_product_cost"]
        + df["est_shipping_cost"]
        + df["est_marketing_cost"]
    )
    df["est_profit"]        = rev - df["est_total_cost"]
    df["est_profit_margin"] = (df["est_profit"] / rev) * 100
    return df


def kpi_summary(master: pd.DataFrame) -> dict:
    """Return a dict of top-level business KPIs."""
    prof = estimate_profitability(master)
    return {
        "total_revenue":      prof["payment_value"].sum(),
        "total_orders":       prof["order_id"].nunique(),
        "total_customers":    prof["customer_unique_id"].nunique(),
        "avg_order_value":    prof["payment_value"].mean(),
        "est_total_cost":     prof["est_total_cost"].sum(),
        "est_profit":         prof["est_profit"].sum(),
        "est_profit_margin":  prof["est_profit_margin"].mean(),
    }


def print_kpi_summary(master: pd.DataFrame):
    """Pretty-print all KPIs to console."""
    kpis = kpi_summary(master)
    print("\n" + "=" * 45)
    print("  📊  BUSINESS KPI SUMMARY")
    print("=" * 45)
    print(f"  Total Revenue        R$ {kpis['total_revenue']:>12,.2f}")
    print(f"  Total Orders               {kpis['total_orders']:>10,}")
    print(f"  Total Customers            {kpis['total_customers']:>10,}")
    print(f"  Avg Order Value      R$ {kpis['avg_order_value']:>12,.2f}")
    print(f"  Est. Total Cost      R$ {kpis['est_total_cost']:>12,.2f}")
    print(f"  Est. Profit          R$ {kpis['est_profit']:>12,.2f}")
    print(f"  Est. Profit Margin         {kpis['est_profit_margin']:>9.1f}%")
    print("=" * 45)
