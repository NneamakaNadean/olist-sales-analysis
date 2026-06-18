# 🛒 Olist E-Commerce Sales Analysis

A comprehensive Business Intelligence project analyzing the Brazilian Olist E-Commerce public dataset.
This project demonstrates end-to-end data analytics — from raw data cleaning to an executive-level dashboard.

---

## 📌 Business Questions Answered

- What is the total revenue, and how has it trended over time?
- Which product categories drive the most sales and profit?
- Who are our most valuable customers (RFM segmentation)?
- Which Brazilian states generate the most revenue?
- What are the preferred payment methods?
- What is the estimated profitability by category and region?

---

## 📂 Dataset

**Source:** [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

| File | Description |
|------|-------------|
| `olist_orders_dataset.csv` | Order status and timestamps |
| `olist_order_items_dataset.csv` | Items per order, price, freight |
| `olist_order_payments_dataset.csv` | Payment methods and values |
| `olist_customers_dataset.csv` | Customer location info |
| `olist_products_dataset.csv` | Product categories and dimensions |
| `olist_sellers_dataset.csv` | Seller location info |
| `olist_geolocation_dataset.csv` | Lat/Long for zip codes |
| `product_category_name_translation.csv` | Portuguese → English category names |

---

## 🛠 Technologies Used

- **Python** — pandas, numpy, matplotlib, seaborn, plotly, folium
- **Jupyter Notebooks** — exploratory analysis and storytelling
- **Power BI** — executive dashboard
- **Git/GitHub** — version control and daily commits

---

## 📁 Project Structure

```
olist-sales-analysis/
│
├── data/
│   ├── raw/                  # Original CSV files from Kaggle
│   └── processed/            # Cleaned, merged datasets
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_revenue_analysis.ipynb
│   ├── 03_customer_segmentation.ipynb
│   ├── 04_product_analysis.ipynb
│   ├── 05_geographic_analysis.ipynb
│   └── 06_profitability_dashboard.ipynb
│
├── dashboards/
│   └── powerbi_dashboard.pbix
│
├── images/                   # Chart exports for README
│
├── src/
│   ├── data_cleaning.py      # Reusable cleaning functions
│   └── analysis.py           # Reusable analysis functions
│
├── requirements.txt
└── README.md
```

---

## 📊 Key Insights

> *(Updated as analysis progresses)*

- 📈 Revenue peaked in **[Month, Year]** at **R$ X**
- 🏆 **[Category]** is the top-selling product category
- 💳 **Credit card** accounts for ~74% of all payments
- 📍 **São Paulo** generates the highest revenue by state
- 👥 VIP customers (top RFM segment) represent **X%** of total revenue

---

## 🗺 Dashboard Preview

*(Screenshots added after Power BI dashboard is complete)*

---

## 🚀 How to Run

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/olist-sales-analysis.git
cd olist-sales-analysis

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add the Olist CSV files to data/raw/

# 4. Open notebooks in order
jupyter notebook notebooks/01_data_cleaning.ipynb
```

---

## 📅 Development Timeline

| Day | Task |
|-----|------|
| 1 | Project setup and repository structure |
| 2 | Initial data exploration (EDA) |
| 3 | Data cleaning and preprocessing |
| 4 | Dataset merging and feature engineering |
| 5–6 | Revenue analysis and visualizations |
| 7–8 | Customer RFM segmentation |
| 9–10 | Product category analysis |
| 11–12 | Geographic analysis and maps |
| 13–14 | Profitability model and Power BI dashboard |
| 15 | README polish, screenshots, LinkedIn post |

---

## 🔮 Future Improvements

- Deploy a live Streamlit dashboard
- Add predictive churn model using scikit-learn
- Integrate delivery delay impact on customer ratings analysis

---

## 👤 Author

**[Your Name]**
[LinkedIn](https://linkedin.com/in/yourprofile) | [GitHub](https://github.com/yourusername)
