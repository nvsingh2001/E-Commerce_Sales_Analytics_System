import os
import streamlit as st
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from dotenv import load_dotenv

# Set page config
st.set_page_config(
    page_title="E-Commerce Sales Analytics Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
env_path = "/home/ares/projects/BridgeLabz/E-Commerce_Sales_Analytics_System/.env"
load_dotenv(env_path)

@st.cache_resource
def get_db_connection():
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT', '5432')
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_pass
        )
        return conn
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        return None

conn = get_db_connection()

if conn is None:
    st.warning("Database connection is offline. Please check your AWS RDS settings.")
    st.stop()

# Helper to run query
def run_query(query):
    try:
        return pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return pd.DataFrame()

st.title("🛍️ E-Commerce Sales Analytics Dashboard")
st.markdown("---")

# Load KPIs
kpi_query = """
SELECT 
    (SELECT SUM(line_total) FROM fact_orders WHERE order_status = 'Completed') as total_revenue,
    (SELECT COUNT(DISTINCT order_id) FROM fact_orders WHERE order_status = 'Completed') as total_orders,
    (SELECT COUNT(DISTINCT customer_id) FROM dim_customers) as total_customers,
    (SELECT COUNT(*) FROM analytics.customer_retention WHERE total_orders >= 2) as repeat_customers,
    (SELECT COUNT(*) FROM analytics.customer_retention) as total_retention_customers
"""
kpi_df = run_query(kpi_query)

if not kpi_df.empty:
    total_rev = float(kpi_df['total_revenue'].iloc[0] or 0.0)
    total_ord = int(kpi_df['total_orders'].iloc[0] or 0)
    total_cust = int(kpi_df['total_customers'].iloc[0] or 0)
    repeat_cust = int(kpi_df['repeat_customers'].iloc[0] or 0)
    total_ret_cust = int(kpi_df['total_retention_customers'].iloc[0] or 1)
    
    aov = total_rev / total_ord if total_ord > 0 else 0.0
    rpr = (repeat_cust / total_ret_cust) * 100.0 if total_ret_cust > 0 else 0.0
    
    # Display KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Revenue", f"£{total_rev:,.2f}")
    col2.metric("Total Orders", f"{total_ord:,}")
    col3.metric("Total Customers", f"{total_cust:,}")
    col4.metric("Average Order Value (AOV)", f"£{aov:,.2f}")
    col5.metric("Repeat Purchase Rate", f"{rpr:.2f}%")

st.markdown("### ")

# Create Tabs
tab_trends, tab_products, tab_customers = st.tabs(["📈 Revenue Trends", "📦 Product Performance", "👥 Customer Analysis"])

with tab_trends:
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.subheader("Monthly Revenue Trend")
        # Query monthly revenue trend
        trend_df = run_query("""
            SELECT month, SUM(total_revenue) as revenue
            FROM analytics.revenue_summary
            GROUP BY month
            ORDER BY month
        """)
        if not trend_df.empty:
            trend_df['month'] = pd.to_datetime(trend_df['month'])
            fig_trend = px.line(trend_df, x='month', y='revenue', 
                                labels={'month': 'Date', 'revenue': 'Revenue (£)'},
                                title="Revenue Trend over Time",
                                markers=True)
            fig_trend.update_layout(template="plotly_dark")
            st.plotly_chart(fig_trend, use_container_width=True)
            
    with col_t2:
        st.subheader("Revenue by Country")
        country_df = run_query("""
            SELECT country, SUM(total_revenue) as revenue
            FROM analytics.revenue_summary
            GROUP BY country
            ORDER BY revenue DESC
            LIMIT 10
        """)
        if not country_df.empty:
            fig_country = px.bar(country_df, x='country', y='revenue',
                                 labels={'country': 'Country', 'revenue': 'Revenue (£)'},
                                 title="Top 10 Countries by Revenue",
                                 color='revenue',
                                 color_continuous_scale=px.colors.sequential.Viridis)
            fig_country.update_layout(template="plotly_dark")
            st.plotly_chart(fig_country, use_container_width=True)
            
    st.subheader("Country-by-Month Revenue Intensity Heatmap")
    heatmap_raw = run_query("""
        SELECT country, month, SUM(total_revenue) as revenue
        FROM analytics.revenue_summary
        GROUP BY country, month
    """)
    if not heatmap_raw.empty:
        heatmap_raw['month'] = pd.to_datetime(heatmap_raw['month']).dt.strftime('%Y-%m')
        # Pivot table
        heatmap_df = heatmap_raw.pivot(index='country', columns='month', values='revenue').fillna(0)
        
        # Display using Matplotlib/Seaborn
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.heatmap(heatmap_df, cmap="viridis", annot=False, fmt=".0f", ax=ax, cbar_kws={'label': 'Revenue (£)'})
        plt.title("Revenue Intensity Heatmap (Country vs Month)")
        plt.xlabel("Month")
        plt.ylabel("Country")
        plt.tight_layout()
        st.pyplot(fig)

with tab_products:
    st.subheader("Top and Bottom 5 Products by Units Sold")
    col_p1, col_p2 = st.columns(2)
    
    # Query product performance data
    prod_perf_df = run_query("""
        SELECT 
            dp.product_id, 
            dp.product_name, 
            SUM(pp.units_sold) as total_units,
            SUM(pp.total_revenue) as total_revenue
        FROM analytics.product_performance pp
        JOIN dim_products dp ON pp.product_id = dp.product_id
        GROUP BY dp.product_id, dp.product_name
    """)
    
    if not prod_perf_df.empty:
        top_prod = prod_perf_df.sort_values(by='total_units', ascending=False).head(5)
        bottom_prod = prod_perf_df.sort_values(by='total_units', ascending=True).head(5)
        
        with col_p1:
            fig_top = px.bar(top_prod, x='total_units', y='product_name', orientation='h',
                             labels={'total_units': 'Units Sold', 'product_name': 'Product'},
                             title="Top 5 Products by Units Sold",
                             color='total_units',
                             color_continuous_scale=px.colors.sequential.Plotly3)
            fig_top.update_layout(template="plotly_dark", yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_top, use_container_width=True)
            
        with col_p2:
            fig_bottom = px.bar(bottom_prod, x='total_units', y='product_name', orientation='h',
                                 labels={'total_units': 'Units Sold', 'product_name': 'Product'},
                                 title="Bottom 5 Products by Units Sold",
                                 color='total_units',
                                 color_continuous_scale=px.colors.sequential.Electric)
            fig_bottom.update_layout(template="plotly_dark", yaxis={'categoryorder':'total descending'})
            st.plotly_chart(fig_bottom, use_container_width=True)
            
    st.subheader("Overall Product Revenue Rankings (Top 50)")
    rank_df = run_query("""
        SELECT 
            product_id, 
            product_name, 
            total_revenue,
            rank
        FROM (
            SELECT 
                dp.product_id, 
                dp.product_name, 
                SUM(fo.line_total) as total_revenue,
                DENSE_RANK() OVER (ORDER BY SUM(fo.line_total) DESC) as rank
            FROM fact_orders fo
            JOIN dim_products dp ON fo.product_id = dp.product_id
            WHERE fo.order_status = 'Completed'
            GROUP BY dp.product_id, dp.product_name
        ) sub
        ORDER BY total_revenue DESC
        LIMIT 50
    """)
    if not rank_df.empty:
        st.dataframe(rank_df, use_container_width=True)

with tab_customers:
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        st.subheader("Customer Segment Distribution")
        segment_df = run_query("""
            SELECT customer_segment, COUNT(*) as count
            FROM dim_customers
            WHERE customer_segment IS NOT NULL
            GROUP BY customer_segment
        """)
        if not segment_df.empty:
            fig_segment = px.pie(segment_df, values='count', names='customer_segment',
                                 title="RFM Customer Segment Distribution",
                                 hole=0.4,
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_segment.update_layout(template="plotly_dark")
            st.plotly_chart(fig_segment, use_container_width=True)
            
    with col_c2:
        st.subheader("Top 10 Customers by Lifetime Spend")
        top_cust_df = run_query("""
            SELECT cr.customer_id, dc.country, cr.lifetime_spend
            FROM analytics.customer_retention cr
            JOIN dim_customers dc ON cr.customer_id = dc.customer_id
            ORDER BY cr.lifetime_spend DESC
            LIMIT 10
        """)
        if not top_cust_df.empty:
            top_cust_df['customer_id'] = top_cust_df['customer_id'].astype(str)
            fig_cust = px.bar(top_cust_df, x='customer_id', y='lifetime_spend',
                              color='lifetime_spend',
                              labels={'customer_id': 'Customer ID', 'lifetime_spend': 'Lifetime Spend (£)'},
                              title="Top 10 Valuable Customers",
                              color_continuous_scale=px.colors.sequential.Deep)
            fig_cust.update_layout(template="plotly_dark")
            st.plotly_chart(fig_cust, use_container_width=True)
            
    st.subheader("Distribution of Order Values")
    order_val_df = run_query("""
        SELECT order_id, SUM(line_total) as order_value
        FROM fact_orders
        WHERE order_status = 'Completed'
        GROUP BY order_id
        HAVING SUM(line_total) > 0 AND SUM(line_total) < 2000 -- Filter outliers for visibility
    """)
    if not order_val_df.empty:
        fig_hist = px.histogram(order_val_df, x='order_value', nbins=50,
                                labels={'order_value': 'Order Value (£)'},
                                title="Order Value Distribution (Up to £2,000)",
                                color_discrete_sequence=['#4B9CD3'])
        fig_hist.update_layout(template="plotly_dark")
        st.plotly_chart(fig_hist, use_container_width=True)
