import os
import streamlit as st
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from abc import ABC, abstractmethod
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from repositories.database_connector import DatabaseConnector

# Set page config
st.set_page_config(
    page_title="E-Commerce Sales Analytics Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

def load_sql_query(filename):
    """Utility to load external SQL query files."""
    sql_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sql', 'analysis_queries', filename)
    with open(sql_path, 'r') as f:
        return f.read()


@st.cache_data
def get_order_values_cached():
    """Fetches all order values once and caches them to speed up interactive filtering."""
    db_connector = DatabaseConnector()
    conn_local = db_connector.get_connection()
    if conn_local is None:
        return pd.DataFrame()
    try:
        query = load_sql_query("order_value_distribution.sql")
        df = pd.read_sql_query(query, conn_local)
        conn_local.close()
        return df
    except Exception as e:
        st.error(f"Failed to fetch order values for histogram: {e}")
        return pd.DataFrame()


class DashboardTab(ABC):
    """
    Abstract Component class representing a Tab in the interactive Dashboard.
    """
    def __init__(self, name: str, icon_label: str):
        self.name = name
        self.icon_label = icon_label

    @abstractmethod
    def render(self, conn) -> None:
        """Renders the components within the Streamlit tab."""
        pass

    def run_query(self, query: str, conn) -> pd.DataFrame:
        """Executes database queries."""
        try:
            return pd.read_sql_query(query, conn)
        except Exception as e:
            st.error(f"Error executing query for {self.name}: {e}")
            return pd.DataFrame()


class RevenueTrendsTab(DashboardTab):
    """Renders revenue trend charts and heatmaps."""
    def __init__(self):
        super().__init__("Revenue Trends", "📈 Revenue Trends")

    def render(self, conn) -> None:
        col_t1, col_t2 = st.columns(2)

        with col_t1:
            st.subheader("Monthly Revenue Trend")
            trend_query = load_sql_query("running_total_revenue.sql")
            trend_df = self.run_query(trend_query, conn)
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
            country_df_all = self.run_query(country_query, conn)
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
        heatmap_raw = self.run_query(heatmap_query, conn)
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


class ProductPerformanceTab(DashboardTab):
    """Renders product-specific rankings and sales metrics."""
    def __init__(self):
        super().__init__("Product Performance", "📦 Product Performance")

    def render(self, conn) -> None:
        st.subheader("Top and Bottom 5 Products by Units Sold")
        col_p1, col_p2 = st.columns(2)

        prod_perf_query = load_sql_query("product_units_sold.sql")
        prod_perf_df = self.run_query(prod_perf_query, conn)

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
        rank_df_all = self.run_query(rank_query, conn)
        if not rank_df_all.empty:
            rank_df = rank_df_all.head(50)
            rank_df = rank_df.rename(columns={"revenue_rank": "rank"})
            st.dataframe(rank_df, use_container_width=True)


class CustomerAnalysisTab(DashboardTab):
    """Renders customer segments, LTV, and order value distributions."""
    def __init__(self):
        super().__init__("Customer Analysis", "👥 Customer Analysis")

    def render(self, conn) -> None:
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            st.subheader("Customer Segment Distribution")
            segment_query = load_sql_query("customer_segment_distribution.sql")
            segment_df = self.run_query(segment_query, conn)
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
            top_cust_df = self.run_query(top_cust_query, conn)
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


class PlatformManagerTab(DashboardTab):
    """Renders the administrative control panel for orchestrating operations."""
    def __init__(self):
        super().__init__("Platform Manager", "🎛️ Platform Manager")

    def render(self, conn) -> None:
        st.subheader("🎛️ Data Platform Control Panel")
        st.markdown("Manage and monitor the E-Commerce analytics pipeline and RDS data layer.")
        
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            st.markdown("### 📊 Database Table Overview")
            table_to_preview = st.selectbox(
                "Select Table to Preview",
                [
                    "dim_customers", 
                    "dim_products", 
                    "fact_orders", 
                    "analytics.revenue_summary", 
                    "analytics.customer_retention", 
                    "analytics.product_performance"
                ]
            )
            preview_limit = st.slider("Rows to Preview", min_value=5, max_value=50, value=10)
            
            if st.button("Preview Table Data"):
                preview_df = self.run_query(f"SELECT * FROM {table_to_preview} LIMIT {preview_limit}", conn)
                if not preview_df.empty:
                    st.dataframe(preview_df, use_container_width=True)
                else:
                    st.warning("Table is empty or could not be queried.")
                    
        with col_p2:
            st.markdown("### ⚙️ Pipeline Control Operations")
            st.info("Initiate pipeline runs or regenerate analytical visual reporting assets.")
            
            if st.button("🚀 Trigger PySpark ETL Pipeline Run"):
                with st.spinner("Executing ETL Pipeline (Extract -> Transform -> Load)... This may take several minutes."):
                    try:
                        st.cache_data.clear()
                        from etl.pipeline import EcommerceSalesAnalyticsPipeline
                        pipeline = EcommerceSalesAnalyticsPipeline()
                        pipeline.run()
                        st.success("ETL Pipeline completed successfully! RDS tables updated.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"ETL Pipeline execution failed: {e}")
                        
            if st.button("🎨 Regenerate Static Report Charts"):
                with st.spinner("Generating static charts (Matplotlib/Seaborn)..."):
                    try:
                        from visualizations.generate_charts import main as generate_main
                        generate_main()
                        st.success("All static charts generated successfully in 'visualizations/static/'!")
                    except Exception as e:
                        st.error(f"Failed to generate static charts: {e}")


class ECommerceDashboardPortal:
    """
    Main Orchestrator for the Streamlit dashboard application.
    Integrates DB connection and tab routing with constructor-injected components.
    """
    def __init__(self, db_connector: DatabaseConnector, tabs: list):
        self._db_connector = db_connector
        self._tabs = tabs

    def run(self) -> None:
        """Boots the dashboard application."""
        conn = self._db_connector.get_connection()
        if conn is None:
            st.warning("Database connection is offline. Please check your AWS RDS settings.")
            st.stop()

        st.title("🛍️ E-Commerce Sales Analytics Dashboard")
        st.markdown("---")

        # Load KPIs
        kpi_query = load_sql_query("kpi_metrics.sql")
        try:
            kpi_df = pd.read_sql_query(kpi_query, conn)
        except Exception as e:
            st.error(f"Error querying KPIs: {e}")
            kpi_df = pd.DataFrame()

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

        # Routing tabs
        tab_names = [tab.icon_label for tab in self._tabs]
        rendered_tabs = st.tabs(tab_names)

        for rendered_tab, tab_obj in zip(rendered_tabs, self._tabs):
            with rendered_tab:
                tab_obj.render(conn)

        # Close database connection when stream completes
        conn.close()


def main():
    db_connector = DatabaseConnector()
    tabs = [
        RevenueTrendsTab(),
        ProductPerformanceTab(),
        CustomerAnalysisTab(),
        PlatformManagerTab()
    ]
    portal = ECommerceDashboardPortal(db_connector, tabs)
    portal.run()


if __name__ == '__main__':
    main()
