import os
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

# Set style for high-quality, professional visualizations
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'figure.titlesize': 18,
    'figure.figsize': (10, 6)
})

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

def get_db_connection():
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT', '5432')
    
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_pass
    )
    return conn

def run_query(query, conn):
    return pd.read_sql_query(query, conn)

def generate_monthly_revenue_trend(conn, output_dir):
    print("Generating Monthly Revenue Trend line chart...")
    query = """
        SELECT month, SUM(total_revenue) as revenue
        FROM analytics.revenue_summary
        GROUP BY month
        ORDER BY month
    """
    df = run_query(query, conn)
    if df.empty:
        print("No revenue data found for monthly trend.")
        return
    
    df['month'] = pd.to_datetime(df['month'])
    
    plt.figure(figsize=(12, 6))
    plt.plot(df['month'], df['revenue'], marker='o', linewidth=2.5, color='#1f77b4', label='Monthly Revenue')
    plt.title('Monthly Revenue Trend (Dec 2009 - Dec 2011)', pad=20)
    plt.xlabel('Month')
    plt.ylabel('Revenue (£)')
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Format dates on x-axis
    plt.xticks(rotation=45)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"£{x:,.0f}"))
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, 'monthly_revenue_trend.png')
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")

def generate_revenue_by_country(conn, output_dir):
    print("Generating Revenue by Country bar chart...")
    query = """
        SELECT country, SUM(total_revenue) as revenue
        FROM analytics.revenue_summary
        GROUP BY country
        ORDER BY revenue DESC
        LIMIT 10
    """
    df = run_query(query, conn)
    if df.empty:
        print("No revenue data found for country bar chart.")
        return
    
    plt.figure(figsize=(12, 6))
    sns.barplot(x='revenue', y='country', data=df, palette='viridis')
    plt.title('Top 10 Countries by Total Revenue', pad=20)
    plt.xlabel('Revenue (£)')
    plt.ylabel('Country')
    
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"£{x:,.0f}"))
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, 'revenue_by_country.png')
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")

def generate_product_performance(conn, output_dir):
    print("Generating Product Performance charts...")
    # Query product performance
    query = """
        SELECT 
            dp.product_name, 
            SUM(pp.units_sold) as total_units
        FROM analytics.product_performance pp
        JOIN dim_products dp ON pp.product_id = dp.product_id
        GROUP BY dp.product_id, dp.product_name
        ORDER BY total_units DESC
    """
    df = run_query(query, conn)
    if df.empty:
        print("No product performance data found.")
        return
    
    top_5 = df.head(5)
    bottom_5 = df.tail(5)
    
    # Top 5 Products
    plt.figure(figsize=(12, 6))
    sns.barplot(x='total_units', y='product_name', data=top_5, palette='crest')
    plt.title('Top 5 Products by Units Sold', pad=20)
    plt.xlabel('Units Sold')
    plt.ylabel('Product Name')
    plt.tight_layout()
    top_path = os.path.join(output_dir, 'top_5_products.png')
    plt.savefig(top_path, dpi=300)
    plt.close()
    print(f"Saved: {top_path}")
    
    # Bottom 5 Products
    plt.figure(figsize=(12, 6))
    sns.barplot(x='total_units', y='product_name', data=bottom_5, palette='flare')
    plt.title('Bottom 5 Products by Units Sold', pad=20)
    plt.xlabel('Units Sold')
    plt.ylabel('Product Name')
    plt.tight_layout()
    bottom_path = os.path.join(output_dir, 'bottom_5_products.png')
    plt.savefig(bottom_path, dpi=300)
    plt.close()
    print(f"Saved: {bottom_path}")

def generate_customer_segment_distribution(conn, output_dir):
    print("Generating Customer Segment Distribution pie chart...")
    query = """
        SELECT customer_segment, COUNT(*) as count
        FROM dim_customers
        WHERE customer_segment IS NOT NULL
        GROUP BY customer_segment
    """
    df = run_query(query, conn)
    if df.empty:
        print("No customer segment data found.")
        return
    
    plt.figure(figsize=(8, 8))
    colors = sns.color_palette('pastel')[0:len(df)]
    plt.pie(df['count'], labels=df['customer_segment'], autopct='%1.1f%%', startangle=140, colors=colors,
            textprops={'fontsize': 14}, wedgeprops={'edgecolor': 'w', 'linewidth': 1})
    plt.title('RFM Customer Segment Distribution', pad=20)
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, 'customer_segment_distribution.png')
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")

def generate_order_value_distribution(conn, output_dir):
    print("Generating Order Value Distribution histogram...")
    query = """
        SELECT order_id, SUM(line_total) as order_value
        FROM fact_orders
        WHERE order_status = 'Completed'
        GROUP BY order_id
        HAVING SUM(line_total) > 0 AND SUM(line_total) < 1000
    """
    df = run_query(query, conn)
    if df.empty:
        print("No order value data found.")
        return
    
    plt.figure(figsize=(10, 6))
    sns.histplot(df['order_value'], bins=40, kde=True, color='#00cc96', edgecolor='#1a1a1a', linewidth=0.8)
    plt.title('Distribution of Order Values (Completed Orders < £1,000)', pad=20)
    plt.xlabel('Order Value (£)')
    plt.ylabel('Frequency')
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"£{x:,.0f}"))
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, 'order_value_distribution.png')
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")

def generate_revenue_intensity_heatmap(conn, output_dir):
    print("Generating Revenue Intensity Heatmap...")
    query = """
        SELECT country, month, SUM(total_revenue) as revenue
        FROM analytics.revenue_summary
        GROUP BY country, month
    """
    df = run_query(query, conn)
    if df.empty:
        print("No revenue summary data found for heatmap.")
        return
    
    df['month'] = pd.to_datetime(df['month']).dt.strftime('%Y-%m')
    
    # Filter for top countries to keep heatmap clean
    top_countries_query = """
        SELECT country
        FROM analytics.revenue_summary
        GROUP BY country
        ORDER BY SUM(total_revenue) DESC
        LIMIT 10
    """
    top_countries_df = run_query(top_countries_query, conn)
    top_countries = top_countries_df['country'].tolist()
    
    df_filtered = df[df['country'].isin(top_countries)]
    
    # Pivot the data
    pivot_df = df_filtered.pivot(index='country', columns='month', values='revenue').fillna(0)
    
    # Sort countries by total revenue (so the highest is at the top)
    pivot_df = pivot_df.reindex(top_countries)
    
    plt.figure(figsize=(14, 8))
    sns.heatmap(pivot_df, cmap='viridis', annot=False, fmt=".0f", cbar_kws={'label': 'Revenue (£)'})
    plt.title('Country-by-Month Revenue Intensity Heatmap (Top 10 Countries)', pad=20)
    plt.xlabel('Month')
    plt.ylabel('Country')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, 'revenue_intensity_heatmap.png')
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")

def main():
    output_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        conn = get_db_connection()
        print("Connected to database successfully.")
        
        generate_monthly_revenue_trend(conn, output_dir)
        generate_revenue_by_country(conn, output_dir)
        generate_product_performance(conn, output_dir)
        generate_customer_segment_distribution(conn, output_dir)
        generate_order_value_distribution(conn, output_dir)
        generate_revenue_intensity_heatmap(conn, output_dir)
        
        conn.close()
        print("Database connection closed. All charts generated successfully!")
        
    except Exception as e:
        print(f"An error occurred during chart generation: {e}")

if __name__ == '__main__':
    main()
