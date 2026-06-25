DROP TABLE IF EXISTS fact_orders CASCADE;
DROP TABLE IF EXISTS dim_products CASCADE;
DROP TABLE IF EXISTS dim_customers CASCADE;

DROP TABLE IF EXISTS analytics.revenue_summary CASCADE;
DROP TABLE IF EXISTS analytics.customer_retention CASCADE;
DROP TABLE IF EXISTS analytics.product_performance CASCADE;

DROP SCHEMA IF EXISTS analytics CASCADE;

CREATE SCHEMA analytics;

CREATE TABLE dim_customers (

    customer_key SERIAL PRIMARY KEY,

    customer_id INTEGER UNIQUE NOT NULL,

    country VARCHAR(100) NOT NULL,

    customer_segment VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dim_products (

    product_key SERIAL PRIMARY KEY,

    stock_code VARCHAR(30) UNIQUE NOT NULL,

    description VARCHAR(255) NOT NULL,

    unit_price DECIMAL(10,2) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fact_orders (

    order_key SERIAL PRIMARY KEY,

    invoice_no VARCHAR(30) NOT NULL,

    customer_key INTEGER NOT NULL,

    product_key INTEGER NOT NULL,

    quantity INTEGER NOT NULL,

    unit_price DECIMAL(10,2) NOT NULL,

    revenue DECIMAL(12,2) NOT NULL,

    order_status VARCHAR(30) NOT NULL,

    order_date TIMESTAMP NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_customer
        FOREIGN KEY (customer_key)
        REFERENCES dim_customers(customer_key),

    CONSTRAINT fk_product
        FOREIGN KEY (product_key)
        REFERENCES dim_products(product_key)
);

CREATE TABLE analytics.revenue_summary (

    summary_id SERIAL PRIMARY KEY,

    country VARCHAR(100),

    revenue_month INTEGER,

    revenue_year INTEGER,

    total_orders INTEGER,

    total_revenue DECIMAL(15,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE analytics.customer_retention (

    retention_id SERIAL PRIMARY KEY,

    customer_key INTEGER,

    first_purchase DATE,

    last_purchase DATE,

    total_orders INTEGER,

    repeat_customer BOOLEAN,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_retention_customer
        FOREIGN KEY (customer_key)
        REFERENCES dim_customers(customer_key)
);

CREATE TABLE analytics.product_performance (

    performance_id SERIAL PRIMARY KEY,

    product_key INTEGER,

    total_quantity INTEGER,

    total_revenue DECIMAL(15,2),

    product_rank INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_performance_product
        FOREIGN KEY (product_key)
        REFERENCES dim_products(product_key)
);