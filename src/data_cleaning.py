"""
data_cleaning.py
----------------
Reusable functions for loading, inspecting, and cleaning
the Olist E-Commerce dataset files.
"""

import pandas as pd
import numpy as np
import os


DATA_RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
DATA_PROCESSED = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


# ─────────────────────────────────────────────
# 1. LOADERS
# ─────────────────────────────────────────────

def load_raw_datasets():
    """Load all Olist CSV files from data/raw/ and return as a dict of DataFrames."""
    files = {
        "orders":       "olist_orders_dataset.csv",
        "order_items":  "olist_order_items_dataset.csv",
        "payments":     "olist_order_payments_dataset.csv",
        "customers":    "olist_customers_dataset.csv",
        "products":     "olist_products_dataset.csv",
        "sellers":      "olist_sellers_dataset.csv",
        "geolocation":  "olist_geolocation_dataset.csv",
        "category_translation": "product_category_name_translation.csv",
    }

    datasets = {}
    for key, filename in files.items():
        path = os.path.join(DATA_RAW, filename)
        try:
            datasets[key] = pd.read_csv(path)
            print(f"✅ Loaded {key}: {datasets[key].shape}")
        except FileNotFoundError:
            print(f"⚠️  File not found: {filename} — skipping.")

    return datasets


# ─────────────────────────────────────────────
# 2. INSPECTION
# ─────────────────────────────────────────────

def inspect_dataset(df, name="DataFrame"):
    """Print shape, dtypes, null counts, and first few rows."""
    print(f"\n{'='*50}")
    print(f"  {name}")
    print(f"{'='*50}")
    print(f"Shape: {df.shape}")
    print(f"\nData Types:\n{df.dtypes}")
    print(f"\nNull Values:\n{df.isnull().sum()}")
    print(f"\nSample:\n{df.head(3)}")


def missing_value_report(datasets: dict):
    """Print a summary of missing values across all datasets."""
    print("\n📋 Missing Value Report")
    print("=" * 50)
    for name, df in datasets.items():
        nulls = df.isnull().sum().sum()
        pct = (nulls / df.size) * 100
        print(f"  {name:<25} {nulls:>6} nulls  ({pct:.2f}%)")


# ─────────────────────────────────────────────
# 3. CLEANING
# ─────────────────────────────────────────────

def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the orders DataFrame:
    - Parse all timestamp columns to datetime
    - Keep only 'delivered' orders for revenue analysis
    - Drop rows with missing delivery timestamps
    """
    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Filter to delivered orders only
    df = df[df["order_status"] == "delivered"].copy()

    # Drop rows missing the key delivery timestamp
    df = df.dropna(subset=["order_delivered_customer_date"])

    # Derive useful time columns
    df["order_year"]  = df["order_purchase_timestamp"].dt.year
    df["order_month"] = df["order_purchase_timestamp"].dt.month
    df["order_yearmonth"] = df["order_purchase_timestamp"].dt.to_period("M")

    print(f"✅ clean_orders: {df.shape[0]:,} delivered orders retained.")
    return df


def clean_payments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the payments DataFrame:
    - Remove rows with zero payment value
    - Aggregate multi-installment payments per order
    """
    df = df[df["payment_value"] > 0].copy()

    # Aggregate: sum payment_value per order, keep dominant payment_type
    agg = df.groupby("order_id").agg(
        payment_value=("payment_value", "sum"),
        payment_installments=("payment_installments", "max"),
        payment_type=("payment_type", lambda x: x.value_counts().index[0]),
    ).reset_index()

    print(f"✅ clean_payments: {agg.shape[0]:,} orders with payment data.")
    return agg


def clean_products(df: pd.DataFrame, translations: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the products DataFrame:
    - Fill missing category names with 'unknown'
    - Merge English category translations
    """
    df = df.copy()
    df["product_category_name"] = df["product_category_name"].fillna("unknown")
    df = df.merge(translations, on="product_category_name", how="left")
    df["category_en"] = df["product_category_name_english"].fillna(
        df["product_category_name"]
    )
    print(f"✅ clean_products: {df.shape[0]:,} products.")
    return df


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicate customers (keep one record per customer_unique_id)."""
    df = df.drop_duplicates(subset="customer_unique_id").copy()
    print(f"✅ clean_customers: {df.shape[0]:,} unique customers.")
    return df


# ─────────────────────────────────────────────
# 4. MASTER MERGE
# ─────────────────────────────────────────────

def build_master_df(datasets: dict) -> pd.DataFrame:
    """
    Merge all cleaned datasets into one master analytical DataFrame.

    Returns a DataFrame with one row per order_item, enriched with
    customer, payment, product, and category information.
    """
    orders   = clean_orders(datasets["orders"])
    payments = clean_payments(datasets["payments"])
    products = clean_products(datasets["products"], datasets["category_translation"])
    customers = clean_customers(datasets["customers"])

    order_items = datasets["order_items"].copy()

    # Build the master join
    master = (
        order_items
        .merge(orders,    on="order_id",    how="inner")
        .merge(payments,  on="order_id",    how="left")
        .merge(products,  on="product_id",  how="left")
        .merge(customers, on="customer_id", how="left")
    )

    print(f"\n✅ Master DataFrame shape: {master.shape}")
    return master


def save_processed(df: pd.DataFrame, filename: str):
    """Save a cleaned DataFrame to data/processed/."""
    os.makedirs(DATA_PROCESSED, exist_ok=True)
    path = os.path.join(DATA_PROCESSED, filename)
    df.to_csv(path, index=False)
    print(f"💾 Saved → {path}")
