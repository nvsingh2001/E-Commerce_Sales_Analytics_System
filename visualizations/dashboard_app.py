import os
import streamlit as st
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from dotenv import load_dotenv

st.set_page_config(
    page_title="E-Commerce Sales Analytics Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

def load_sql_query(filename):
    sql_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sql', 'analysis_queries', filename)
    with open(sql_path, 'r') as f:
        return f.read()

@st.cache_resource
def get_db_connection():
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD")
    db_port = os.getenv("DB_PORT", "5432")
    try:
        conn = psycopg2.connect(
            host=db_host, port=db_port, database=db_name, user=db_user, password=db_pass
        )
        return conn
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        return None


conn = get_db_connection()

if conn is None:
    st.warning("Database connection is offline. Please check your AWS RDS settings.")
    st.stop()


def run_query(query):
    try:
        return pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return pd.DataFrame()


@st.cache_data
def get_order_values_cached():
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD")
    db_port = os.getenv("DB_PORT", "5432")
    try:
        conn_local = psycopg2.connect(
            host=db_host, port=db_port, database=db_name, user=db_user, password=db_pass
        )
        query = load_sql_query("order_value_distribution.sql")
        df = pd.read_sql_query(query, conn_local)
        conn_local.close()
        return df
    except Exception as e:
        st.error(f"Failed to fetch order values for histogram: {e}")
        return pd.DataFrame()


st.title("🛍️ E-Commerce Sales Analytics Dashboard")
st.markdown("---")

kpi_query = load_sql_query("kpi_metrics.sql")
kpi_df = run_query(kpi_query)

if not kpi_df.empty:
    total_rev = float(kpi_df["total_revenue"].iloc[0] or 0.0)
    total_ord = int(kpi_df["total_orders"].iloc[0] or 0)
    total_cust = int(kpi_df["total_customers"].iloc[0] or 0)
    repeat_cust = int(kpi_df["repeat_customers"].iloc[0] or 0)
    total_ret_cust = int(kpi_df["total_retention_customers"].iloc[0] or 1)

    aov = total_rev / total_ord if total_ord > 0 else 0.0
    rpr = (repeat_cust / total_ret_cust) * 100.0 if total_ret_cust > 0 else 0.0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Revenue", f"£{total_rev:,.2f}")
    col2.metric("Total Orders", f"{total_ord:,}")
    col3.metric("Total Customers", f"{total_cust:,}")
    col4.metric("Average Order Value (AOV)", f"£{aov:,.2f}")
    col5.metric("Repeat Purchase Rate", f"{rpr:.2f}%")

st.markdown("### ")

tab_trends, tab_products, tab_customers = st.tabs(
    ["📈 Revenue Trends", "📦 Product Performance", "👥 Customer Analysis"]
)

with tab_trends:
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.subheader("Monthly Revenue Trend")
        trend_query = load_sql_query("running_total_revenue.sql")
        trend_df = run_query(trend_query)
        if not trend_df.empty:
            trend_df["revenue_month"] = pd.to_datetime(trend_df["revenue_month"])
            fig_trend = px.line(
                trend_df,
                x="revenue_month",
                y="monthly_revenue",
                labels={"revenue_month": "Date", "monthly_revenue": "Revenue (£)"},
                title="Revenue Trend over Time",
                markers=True,
            )
            fig_trend.update_layout(template="plotly_dark")
            st.plotly_chart(fig_trend, use_container_width=True)

    with col_t2:
        st.subheader("Revenue by Country")
        country_query = load_sql_query("revenue_per_country.sql")
        country_df_all = run_query(country_query)
        if not country_df_all.empty:
            country_df = country_df_all.head(10)
            fig_country = px.bar(
                country_df,
                x="country",
                y="total_revenue",
                labels={"country": "Country", "total_revenue": "Revenue (£)"},
                title="Top 10 Countries by Revenue",
                color="total_revenue",
                color_continuous_scale=px.colors.sequential.Viridis,
            )
            fig_country.update_layout(template="plotly_dark")
            st.plotly_chart(fig_country, use_container_width=True)

    st.subheader("Country-by-Month Revenue Intensity Heatmap")
    heatmap_query = load_sql_query("heatmap_revenue.sql")
    heatmap_raw = run_query(heatmap_query)
    if not heatmap_raw.empty:
        heatmap_raw["month"] = pd.to_datetime(heatmap_raw["month"]).dt.strftime("%Y-%m")
        heatmap_raw["revenue"] = heatmap_raw["revenue"].astype(float)

        top_countries = (
            heatmap_raw.groupby("country")["revenue"].sum().nlargest(10).index.tolist()
        )
        heatmap_filtered = heatmap_raw[heatmap_raw["country"].isin(top_countries)]

        heatmap_df = heatmap_filtered.pivot(
            index="country", columns="month", values="revenue"
        ).fillna(0)
        heatmap_df = heatmap_df.reindex(top_countries)

        fig, ax = plt.subplots(figsize=(12, 6))
        sns.heatmap(
            heatmap_df,
            cmap="viridis",
            annot=False,
            fmt=".0f",
            ax=ax,
            cbar_kws={"label": "Revenue (£)"},
        )
        plt.title("Revenue Intensity Heatmap (Top 10 Countries)")
        plt.xlabel("Month")
        plt.ylabel("Country")
        plt.tight_layout()
        st.pyplot(fig)

with tab_products:
    st.subheader("Top and Bottom 5 Products by Units Sold")
    col_p1, col_p2 = st.columns(2)

    # Query product performance data
    prod_perf_query = load_sql_query("product_units_sold.sql")
    prod_perf_df = run_query(prod_perf_query)

    if not prod_perf_df.empty:
        top_prod = prod_perf_df.sort_values(by="total_units", ascending=False).head(5)
        bottom_prod = prod_perf_df.sort_values(by="total_units", ascending=True).head(5)

        with col_p1:
            fig_top = px.bar(
                top_prod,
                x="total_units",
                y="product_name",
                orientation="h",
                labels={"total_units": "Units Sold", "product_name": "Product"},
                title="Top 5 Products by Units Sold",
                color="total_units",
                color_continuous_scale=px.colors.sequential.Plotly3,
            )
            fig_top.update_layout(
                template="plotly_dark", yaxis={"categoryorder": "total ascending"}
            )
            st.plotly_chart(fig_top, use_container_width=True)

        with col_p2:
            fig_bottom = px.bar(
                bottom_prod,
                x="total_units",
                y="product_name",
                orientation="h",
                labels={"total_units": "Units Sold", "product_name": "Product"},
                title="Bottom 5 Products by Units Sold",
                color="total_units",
                color_continuous_scale=px.colors.sequential.Electric,
            )
            fig_bottom.update_layout(
                template="plotly_dark", yaxis={"categoryorder": "total descending"}
            )
            st.plotly_chart(fig_bottom, use_container_width=True)

    st.subheader("Overall Product Revenue Rankings (Top 50)")
    rank_query = load_sql_query("product_revenue_ranking.sql")
    rank_df_all = run_query(rank_query)
    if not rank_df_all.empty:
        rank_df = rank_df_all.head(50)
        # Rename revenue_rank to rank to preserve UI labels
        rank_df = rank_df.rename(columns={"revenue_rank": "rank"})
        st.dataframe(rank_df, use_container_width=True)

with tab_customers:
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.subheader("Customer Segment Distribution")
        segment_query = load_sql_query("customer_segment_distribution.sql")
        segment_df = run_query(segment_query)
        if not segment_df.empty:
            fig_segment = px.pie(
                segment_df,
                values="count",
                names="customer_segment",
                title="RFM Customer Segment Distribution",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig_segment.update_layout(template="plotly_dark")
            st.plotly_chart(fig_segment, use_container_width=True)

    with col_c2:
        st.subheader("Top 10 Customers by Lifetime Spend")
        top_cust_query = load_sql_query("top_10_customers.sql")
        top_cust_df = run_query(top_cust_query)
        if not top_cust_df.empty:
            top_cust_df["customer_id"] = top_cust_df["customer_id"].astype(str)
            fig_cust = px.bar(
                top_cust_df,
                x="customer_id",
                y="lifetime_spend",
                color="lifetime_spend",
                labels={
                    "customer_id": "Customer ID",
                    "lifetime_spend": "Lifetime Spend (£)",
                },
                title="Top 10 Valuable Customers",
                color_continuous_scale=px.colors.sequential.deep,
            )
            fig_cust.update_layout(template="plotly_dark")
            st.plotly_chart(fig_cust, use_container_width=True)

    st.subheader("Distribution of Order Values")
    order_val_df_all = get_order_values_cached()
    if not order_val_df_all.empty:
        max_val = st.slider(
            "Select Maximum Order Value to Display (£)",
            min_value=200,
            max_value=5000,
            value=1000,
            step=100,
        )
        order_val_df = order_val_df_all[order_val_df_all["order_value"] <= max_val]

        fig_hist = px.histogram(
            order_val_df,
            x="order_value",
            nbins=40,
            labels={"order_value": "Order Value (£)"},
            title=f"Order Value Distribution (Up to £{max_val:,})",
            color_discrete_sequence=["#00cc96"],
            marginal="box",
        )
        fig_hist.update_layout(
            template="plotly_dark",
            bargap=0.05,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        fig_hist.update_traces(
            marker_line_color="#1a1a1a", marker_line_width=1.0, opacity=0.85
        )
        st.plotly_chart(fig_hist, use_container_width=True)
