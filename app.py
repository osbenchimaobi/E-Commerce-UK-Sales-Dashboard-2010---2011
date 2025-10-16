import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="E‑Commerce Revenue & Profit Dashboard", layout="wide")

@st.cache_data
def load_data(path="E-Commerce_UK_DATASET.xlsx"):
    df = pd.read_excel(path, sheet_name="data", parse_dates=["InvoiceDate"])
    # Ensure numeric columns
    for col in ["Quantity", "UnitPrice", "Revenue", "Cost", "Profit"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["Month"] = df["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
    return df

df = load_data("E-Commerce_UK_DATASET.xlsx")

st.title("E‑Commerce — Revenue & Profit Dashboard (Live Demo)")
st.markdown("Interactive dashboard built with Streamlit + Plotly. Use filters on the left to explore revenue and profit.")

# Sidebar filters
st.sidebar.header("Filters")
min_date = df["InvoiceDate"].min().date()
max_date = df["InvoiceDate"].max().date()

date_range = st.sidebar.date_input("Invoice date range", [min_date, max_date])
country_sel = st.sidebar.multiselect("Country (top listed first)", 
                                   options=df["Country"].value_counts().index.tolist(),
                                   default=list(df["Country"].value_counts().index[:3]))
top_n = st.sidebar.slider("Top N items (products/customers)", min_value=5, max_value=20, value=10)

# Apply filters
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
mask = (df["InvoiceDate"] >= start_date) & (df["InvoiceDate"] <= end_date)
if country_sel:
    mask &= df["Country"].isin(country_sel)
df_f = df[mask].copy()

# KPIs
total_revenue = df_f["Revenue"].sum()
total_profit = df_f["Profit"].sum()
total_orders = df_f["InvoiceNo"].nunique()
avg_order_value = (total_revenue / total_orders) if total_orders else 0
profit_margin = (total_profit / total_revenue) if total_revenue else 0

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns([2,2,2,2,2])
kpi1.metric("Total Revenue", f"£{total_revenue:,.2f}")
kpi2.metric("Total Profit", f"£{total_profit:,.2f}")
kpi3.metric("Total Orders", f"{total_orders:,d}")
kpi4.metric("Avg Order Value", f"£{avg_order_value:,.2f}")
kpi5.metric("Profit Margin", f"{profit_margin:.2%}")

st.markdown("---")

# Monthly trend
monthly = df_f.groupby(pd.Grouper(key="InvoiceDate", freq="M")).agg(Revenue=("Revenue","sum"), Profit=("Profit","sum")).reset_index()
monthly["Month"] = monthly["InvoiceDate"].dt.strftime("%Y-%m")
fig_trend = px.line(monthly, x="Month", y=["Revenue","Profit"], markers=True, labels={"value":"Amount (£)","variable":"Metric"})
fig_trend.update_layout(title="Monthly Revenue & Profit", legend_title_text="Metric", hovermode="x unified")
st.plotly_chart(fig_trend, use_container_width=True)

# Top products
st.markdown("### Top products by Revenue")
prod = df_f.groupby(["StockCode","Description"]).agg(Revenue=("Revenue","sum"), Profit=("Profit","sum"), Quantity=("Quantity","sum")).reset_index()
prod = prod.sort_values("Revenue", ascending=False).head(top_n)
fig_prod = px.bar(prod, x="Revenue", y="Description", orientation="h", hover_data=["StockCode","Profit","Quantity"], height=400)
fig_prod.update_layout(yaxis={"categoryorder":"total ascending"})
st.plotly_chart(fig_prod, use_container_width=True)

# Revenue by country
st.markdown("### Revenue by Country")
country = df_f.groupby("Country").agg(Revenue=("Revenue","sum")).reset_index().sort_values("Revenue", ascending=False).head(15)
fig_country = px.bar(country, x="Revenue", y="Country", orientation="h", height=350)
st.plotly_chart(fig_country, use_container_width=True)

# Top customers
st.markdown("### Top customers by Revenue")
cust = df_f.groupby("CustomerID").agg(Revenue=("Revenue","sum"), Orders=("InvoiceNo","nunique")).reset_index().sort_values("Revenue", ascending=False).head(top_n)
fig_cust = px.bar(cust, x="Revenue", y=cust["CustomerID"].astype(str), orientation="h", height=350)
fig_cust.update_layout(yaxis_title="CustomerID", yaxis={"categoryorder":"total ascending"})
st.plotly_chart(fig_cust, use_container_width=True)

# Data table
st.markdown("### Underlying sample data (first 200 rows)")
st.dataframe(df_f.head(200))

st.markdown("---")
st.markdown("**Notes:** This demo includes the source dataset file packaged with the app. To update data, replace the Excel file with a newer file named `E-Commerce_UK_DATASET.xlsx` in the app folder and redeploy / refresh.")