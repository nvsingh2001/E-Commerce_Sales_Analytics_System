import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from abc import ABC, abstractmethod
from utils.sql_loader import SQLLoader


sns.set_theme(style="whitegrid")
plt.rcParams.update(
    {
        "font.size": 12,
        "axes.labelsize": 14,
        "axes.titlesize": 16,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "figure.titlesize": 18,
        "figure.figsize": (10, 6),
    }
)


class BaseChart(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate(self, conn, output_dir: str) -> None:
        pass

    def run_query(self, query: str, conn) -> pd.DataFrame:
        return pd.read_sql_query(query, conn)


class MonthlyRevenueTrendChart(BaseChart):
    def __init__(self):
        super().__init__("Monthly Revenue Trend")

    def generate(self, conn, output_dir: str) -> None:
        print(f"Generating {self.name} line chart...")
        query = SQLLoader.load_query("running_total_revenue.sql")
        df = self.run_query(query, conn)
        if df.empty:
            print("No revenue data found for monthly trend.")
            return

        df["revenue_month"] = pd.to_datetime(df["revenue_month"])

        plt.figure(figsize=(12, 6))
        plt.plot(
            df["revenue_month"],
            df["monthly_revenue"],
            marker="o",
            linewidth=2.5,
            color="#1f77b4",
            label="Monthly Revenue",
        )
        plt.title("Monthly Revenue Trend (Dec 2009 - Dec 2011)", pad=20)
        plt.xlabel("Month")
        plt.ylabel("Revenue (£)")
        plt.grid(True, linestyle="--", alpha=0.6)

        plt.xticks(rotation=45)
        plt.gca().yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, loc: f"£{x:,.0f}")
        )
        plt.tight_layout()

        output_path = os.path.join(output_dir, "monthly_revenue_trend.png")
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"Saved: {output_path}")


class RevenueByCountryChart(BaseChart):
    def __init__(self):
        super().__init__("Revenue by Country")

    def generate(self, conn, output_dir: str) -> None:
        print(f"Generating {self.name} bar chart...")
        query = SQLLoader.load_query("revenue_per_country.sql")
        df_all = self.run_query(query, conn)
        if df_all.empty:
            print("No revenue data found for country bar chart.")
            return

        df = df_all.head(10)
        plt.figure(figsize=(12, 6))
        sns.barplot(x="total_revenue", y="country", data=df, palette="viridis")
        plt.title("Top 10 Countries by Total Revenue", pad=20)
        plt.xlabel("Revenue (£)")
        plt.ylabel("Country")

        plt.gca().xaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, loc: f"£{x:,.0f}")
        )
        plt.tight_layout()

        output_path = os.path.join(output_dir, "revenue_by_country.png")
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"Saved: {output_path}")


class ProductPerformanceCharts(BaseChart):
    def __init__(self):
        super().__init__("Product Performance")

    def generate(self, conn, output_dir: str) -> None:
        print(f"Generating {self.name} charts...")
        query = SQLLoader.load_query("product_units_sold.sql")
        df = self.run_query(query, conn)
        if df.empty:
            print("No product performance data found.")
            return

        top_5 = df.sort_values(by="total_units", ascending=False).head(5)
        bottom_5 = df.sort_values(by="total_units", ascending=True).head(5)

        plt.figure(figsize=(12, 6))
        sns.barplot(x="total_units", y="product_name", data=top_5, palette="crest")
        plt.title("Top 5 Products by Units Sold", pad=20)
        plt.xlabel("Units Sold")
        plt.ylabel("Product Name")
        plt.tight_layout()
        top_path = os.path.join(output_dir, "top_5_products.png")
        plt.savefig(top_path, dpi=300)
        plt.close()
        print(f"Saved: {top_path}")

        plt.figure(figsize=(12, 6))
        sns.barplot(x="total_units", y="product_name", data=bottom_5, palette="flare")
        plt.title("Bottom 5 Products by Units Sold", pad=20)
        plt.xlabel("Units Sold")
        plt.ylabel("Product Name")
        plt.tight_layout()
        bottom_path = os.path.join(output_dir, "bottom_5_products.png")
        plt.savefig(bottom_path, dpi=300)
        plt.close()
        print(f"Saved: {bottom_path}")


class CustomerSegmentDistributionChart(BaseChart):
    def __init__(self):
        super().__init__("Customer Segment Distribution")

    def generate(self, conn, output_dir: str) -> None:
        print(f"Generating {self.name} pie chart...")
        query = SQLLoader.load_query("customer_segment_distribution.sql")
        df = self.run_query(query, conn)
        if df.empty:
            print("No customer segment data found.")
            return

        plt.figure(figsize=(8, 8))
        colors = sns.color_palette("pastel")[0 : len(df)]
        plt.pie(
            df["count"],
            labels=df["customer_segment"],
            autopct="%1.1f%%",
            startangle=140,
            colors=colors,
            textprops={"fontsize": 14},
            wedgeprops={"edgecolor": "w", "linewidth": 1},
        )
        plt.title("RFM Customer Segment Distribution", pad=20)
        plt.tight_layout()

        output_path = os.path.join(output_dir, "customer_segment_distribution.png")
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"Saved: {output_path}")


class OrderValueDistributionChart(BaseChart):
    def __init__(self):
        super().__init__("Order Value Distribution")

    def generate(self, conn, output_dir: str) -> None:
        print(f"Generating {self.name} histogram...")
        query = SQLLoader.load_query("order_value_distribution.sql")
        df_all = self.run_query(query, conn)
        if df_all.empty:
            print("No order value data found.")
            return

        df = df_all[df_all["order_value"] < 1000]
        if df.empty:
            print("No order value data found within limit.")
            return

        plt.figure(figsize=(10, 6))
        sns.histplot(
            df["order_value"],
            bins=40,
            kde=True,
            color="#00cc96",
            edgecolor="#1a1a1a",
            linewidth=0.8,
        )
        plt.title("Distribution of Order Values (Completed Orders < £1,000)", pad=20)
        plt.xlabel("Order Value (£)")
        plt.ylabel("Frequency")
        plt.gca().xaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, loc: f"£{x:,.0f}")
        )
        plt.tight_layout()

        output_path = os.path.join(output_dir, "order_value_distribution.png")
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"Saved: {output_path}")


class RevenueIntensityHeatmapChart(BaseChart):
    def __init__(self):
        super().__init__("Revenue Intensity Heatmap")

    def generate(self, conn, output_dir: str) -> None:
        print(f"Generating {self.name} heatmap...")
        query = SQLLoader.load_query("heatmap_revenue.sql")
        df = self.run_query(query, conn)
        if df.empty:
            print("No revenue summary data found for heatmap.")
            return

        df["month"] = pd.to_datetime(df["month"]).dt.strftime("%Y-%m")

        top_countries_query = SQLLoader.load_query("revenue_per_country.sql")
        top_countries_df_all = self.run_query(top_countries_query, conn)
        top_countries_df = top_countries_df_all.head(10)
        top_countries = top_countries_df["country"].tolist()

        df_filtered = df[df["country"].isin(top_countries)]

        pivot_df = df_filtered.pivot(
            index="country", columns="month", values="revenue"
        ).fillna(0)
        pivot_df = pivot_df.reindex(top_countries)

        plt.figure(figsize=(14, 8))
        sns.heatmap(
            pivot_df,
            cmap="viridis",
            annot=False,
            fmt=".0f",
            cbar_kws={"label": "Revenue (£)"},
        )
        plt.title(
            "Country-by-Month Revenue Intensity Heatmap (Top 10 Countries)", pad=20
        )
        plt.xlabel("Month")
        plt.ylabel("Country")
        plt.xticks(rotation=45)
        plt.tight_layout()

        output_path = os.path.join(output_dir, "revenue_intensity_heatmap.png")
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"Saved: {output_path}")


class ChartOrchestrator:
    def __init__(self, db_connector, charts: list):
        self._db_connector = db_connector
        self._charts = charts

    def generate_all(self, output_dir: str) -> None:
        os.makedirs(output_dir, exist_ok=True)
        conn = self._db_connector.get_connection()
        if conn is None:
            print("Failed to connect to database for static chart generation.")
            return

        print("Connected to database successfully. Beginning chart generation...")
        try:
            for chart in self._charts:
                chart.generate(conn, output_dir)
            print("Database connection closed. All charts generated successfully!")
        except Exception as e:
            print(f"An error occurred during chart generation: {e}")
        finally:
            conn.close()


def main():
    from repositories.database_connector import DatabaseConnector

    db_connector = DatabaseConnector()
    charts = [
        MonthlyRevenueTrendChart(),
        RevenueByCountryChart(),
        ProductPerformanceCharts(),
        CustomerSegmentDistributionChart(),
        OrderValueDistributionChart(),
        RevenueIntensityHeatmapChart(),
    ]

    output_dir = os.path.join(os.path.dirname(__file__), "static")
    orchestrator = ChartOrchestrator(db_connector, charts)
    orchestrator.generate_all(output_dir)


if __name__ == "__main__":
    main()
