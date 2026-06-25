DROP TABLE IF EXISTS analytics.product_performance CASCADE;
DROP TABLE IF EXISTS analytics.customer_retention CASCADE;
DROP TABLE IF EXISTS analytics.revenue_summary CASCADE;
DROP TABLE IF EXISTS fact_orders CASCADE;
DROP TABLE IF EXISTS dim_products CASCADE;
DROP TABLE IF EXISTS dim_customers CASCADE;

DROP SCHEMA IF EXISTS analytics CASCADE;
CREATE SCHEMA analytics;

CREATE TABLE dim_customers (
    customer_id INT PRIMARY KEY,
    country VARCHAR(80) NOT NULL,
    customer_segment VARCHAR(40)
);

CREATE TABLE dim_products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    avg_unit_price DECIMAL(10,2) NOT NULL
);

CREATE TABLE fact_orders (
    order_line_id BIGSERIAL PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL,
    customer_id INT, -- Nullable to support rows with missing CustomerID (known data gap)
    product_id VARCHAR(20) NOT NULL,
    order_date TIMESTAMP NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    line_total DECIMAL(12,2) NOT NULL,
    order_status VARCHAR(20) NOT NULL,
    CONSTRAINT fk_customer
        FOREIGN KEY (customer_id)
        REFERENCES dim_customers(customer_id),
    CONSTRAINT fk_product
        FOREIGN KEY (product_id)
        REFERENCES dim_products(product_id)
);

CREATE TABLE analytics.revenue_summary (
    summary_id BIGSERIAL PRIMARY KEY,
    country VARCHAR(80) NOT NULL,
    month DATE NOT NULL,
    total_revenue DECIMAL(14,2) NOT NULL,
    total_orders INT NOT NULL,
    average_order_value DECIMAL(10,2) NOT NULL
);

CREATE TABLE analytics.customer_retention (
    retention_id BIGSERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    total_orders INT NOT NULL,
    lifetime_spend DECIMAL(14,2) NOT NULL,
    first_order_date DATE NOT NULL,
    last_order_date DATE NOT NULL,
    customer_status VARCHAR(30) NOT NULL,
    CONSTRAINT fk_retention_customer
        FOREIGN KEY (customer_id)
        REFERENCES dim_customers(customer_id)
);

CREATE TABLE analytics.product_performance (
    performance_id BIGSERIAL PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL,
    month DATE NOT NULL,
    units_sold INT NOT NULL,
    total_revenue DECIMAL(14,2) NOT NULL,
    overall_rank INT NOT NULL,
    CONSTRAINT fk_performance_product
        FOREIGN KEY (product_id)
        REFERENCES dim_products(product_id)
);