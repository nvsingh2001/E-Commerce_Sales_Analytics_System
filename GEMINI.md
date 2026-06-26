  
**DATA ENGINEERING FELLOWSHIP**

**Project Simulation Booklet**

**E-Commerce Sales Analytics Pipeline**

| AWS GROUP 1 Platform: AWS Team: Ayush Singh  •  Naman Vinay Singh |
| :---: |

BridgeLabz Data Engineering Fellowship Program

*Raw Data → Cloud Storage → ETL/PySpark → Database → Analytics → Dashboard → Documentation*

# **Essential Reference — Program Standards**

This booklet is your team's complete guide for the Data Engineering Fellowship capstone. It follows the same pipeline pattern as every other team's project — Raw Data → Cloud Storage → ETL / PySpark → Database → Analytics → Dashboard → Documentation — and is evaluated by your instructor. Read this section once before starting, then turn to Section 1 of your project.

| Core Pipeline Pattern (every project) Raw Data  →  Cloud Storage  →  ETL / PySpark  →  Database  →  Analytics  →  Dashboard  →  Documentation |
| :---- |

## **GitHub Repository Standards**

Maintain a single repository for your project. Repository structure, commit hygiene, and clarity are evaluated alongside the code.

| your-project-name/ ├── README.md ├── documentation/ │   └── Project\_Documentation.docx ├── architecture/ │   └── architecture\_diagram.png ├── datasets/ │   ├── raw/ │   └── sample/ ├── sql/ │   ├── schema/ │   └── analysis\_queries/ ├── pyspark/ │   ├── extraction/ │   ├── transformation/ │   └── loading/ ├── screenshots/ ├── testing/ │   └── test\_cases.xlsx └── visualizations/ |
| :---- |

* Use descriptive commit messages (e.g., 'add PySpark deduplication for order line items'), not 'update' or 'fix'.

* Commit incrementally as the pipeline is built — not in a single final upload.

* Never commit credentials, access keys, or connection strings. Use environment variables.

* Every team member should have visible commits reflecting their individual contribution.

## **Documentation Standards**

Produce ONE consolidated documentation file (Word or PDF) covering the entire project. Documentation is graded with equal weight to the pipeline — a pipeline nobody can understand has limited business value. Include the following sections in this order:

1. Project Overview

2. Dataset Details

3. Architecture Diagram

4. Cloud Resources

5. Database Design

6. ETL Flow

7. SQL Analysis

8. Visualizations

9. Testing

10. Challenges

11. Learnings

12. Conclusion

* Write in clear, professional English. Structure with headings that mirror this booklet.

* Include actual screenshots from your own implementation — not placeholder or stock images.

* Explain WHY a decision was made, not just WHAT was done.

* Keep the Challenges & Learnings section honest and specific.

## **Final Submission Checklist**

* ✓ Working end-to-end pipeline (ingestion → storage → ETL → database → visualization)

* ✓ GitHub repository following the standard structure above

* ✓ Consolidated documentation file

* ✓ All SQL scripts (including views and window functions)

* ✓ All PySpark transformation scripts

* ✓ Dashboard outputs/screenshots

* ✓ Completed test case log (15 test cases with evidence)

* ✓ Architecture diagram

**AWS GROUP 1**

# **E-Commerce Sales Analytics Pipeline**

**Platform:** AWS    **Team:** Ayush Singh, Naman Vinay Singh

## **Section 1 — Project Overview**

### **Project Name**

E-Commerce Sales Analytics Pipeline

### **Team Members**

Ayush Singh, Naman Vinay Singh

### **Business Domain**

E-Commerce / Online Retail

### **Business Problem**

A UK-based online retailer sells unique all-occasion gift-ware to retail and wholesale customers across many countries, but its raw transaction export is a single flat file with no analytics layer on top of it. The business has no reliable way to answer basic questions such as which products drive the most revenue, which customers are most valuable, or how sales trend month over month.

### **Business Objective**

Build a cloud-based analytics pipeline that ingests the raw transaction export, splits and cleans it using PySpark, loads it into a relational database, and exposes the results through dashboards so that business stakeholders can self-serve answers to recurring sales questions.

### **Expected Outcome**

A working pipeline that takes the raw transaction export and produces a curated, query-ready database plus a set of dashboards covering revenue trends, customer value, and product performance.

### **Business Value**

* Enables data-driven decisions on which products to promote or discontinue.

* Identifies high-value customers for retention and loyalty initiatives.

* Surfaces revenue trends early enough to act on seasonal or regional dips.

* Removes manual spreadsheet reconciliation currently performed by the operations team.

### **Success Criteria**

* Pipeline runs end-to-end from raw export to dashboard without manual intervention.

* All three Business Use Cases produce correct, validated output tables.

* Dashboards clearly answer the business question each use case was designed for.

* All 15 test cases pass and are logged with evidence.

## **Section 2 — Dataset Details**

Unlike a multi-file export, the real source for this project is a single transactional file. During the Extraction step of your ETL pipeline (Section 6), this one file is split into three working extracts — customers.csv, products.csv, and orders.csv — which are then carried through the rest of the pipeline. The tables below describe both the real raw source and the derived working extracts your team will produce.

| Recommended Public Dataset Online Retail II Data Set  —  [https://archive.ics.uci.edu/dataset/502/online+retail+ii](https://archive.ics.uci.edu/dataset/502/online+retail+ii) Provider: UCI Machine Learning Repository This is a real transactional dataset of 1,067,371 line items from a UK-based, non-store online retailer, covering all transactions between December 2009 and December 2011\. It ships as a single file (online\_retail\_II.xlsx, with two sheets covering 2009–10 and 2010–11) containing exactly eight columns: InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, and Country. There is no separate products or customers file — splitting this single export into working extracts is itself the first real ETL task in Section 6\. Invoice numbers beginning with 'C' indicate cancellations and should be handled explicitly in your data quality rules. The dataset can be downloaded directly from the UCI page or pulled programmatically with \`pip install ucimlrepo\` and \`fetch\_ucirepo(id=502)\`. It is licensed CC BY 4.0. |
| :---- |

### **online\_retail\_II.csv (raw source)**

The single real source file. One row per product line within a transaction; this is the only file you will actually download.

| Attribute | Detail |
| :---- | :---- |
| Approximate Row Count | 1,067,371 rows |
| Important Columns | InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country |
| Source Type | CSV file (batch upload) |

### **customers.csv (derived working extract)**

Produced during Extraction by selecting the distinct CustomerID/Country pairs from the raw source.

| Attribute | Detail |
| :---- | :---- |
| Approximate Row Count | \~5,900 distinct customers |
| Important Columns | customer\_id (← CustomerID), country (← Country) |
| Source Type | CSV file (batch upload) |

### **products.csv (derived working extract)**

Produced during Extraction by selecting the distinct StockCode/Description pairs from the raw source.

| Attribute | Detail |
| :---- | :---- |
| Approximate Row Count | \~4,600 distinct products |
| Important Columns | product\_id (← StockCode), product\_name (← Description) |
| Source Type | CSV file (batch upload) |

### **orders.csv (derived working extract)**

Produced during Extraction as a near-direct carry-over of the raw source's transaction rows, foreign-keyed to the two extracts above.

| Attribute | Detail |
| :---- | :---- |
| Approximate Row Count | 1,067,371 rows |
| Important Columns | order\_id (← InvoiceNo), customer\_id (← CustomerID), product\_id (← StockCode), order\_date (← InvoiceDate), quantity (← Quantity), unit\_price (← UnitPrice) |
| Source Type | CSV file (batch upload) |

### **Data Relationships**

* orders.customer\_id references customers.customer\_id (many orders per customer); rows with a null CustomerID in the source remain a known, documented gap — see Missing Value Handling in Section 6\.

* orders.product\_id references products.product\_id (many orders per product).

* Each row in orders.csv represents a single product line within an invoice, so multiple rows can share the same order\_id.

## **Section 3 — Architecture Design**

The architecture follows a simple, linear flow appropriate for a beginner-to-intermediate AWS pipeline. There is no streaming requirement — all ingestion is batch-based. AWS Lambda is a required component of this architecture: it is the trigger that starts the ETL job automatically whenever a new export lands in the raw zone, rather than relying on a team member to kick off the pipeline by hand.

| online\_retail\_II.csv (raw source export)         |         v    Amazon S3 (raw zone)         |         v   (S3 PUT event)    AWS Lambda (triggers ETL job)         |         v    PySpark ETL (split, clean, join, aggregate)         |         v    Amazon S3 (curated zone)         |         v    AWS RDS (PostgreSQL)         |         v    Matplotlib / Seaborn / Streamlit         |         v    Business Dashboard |
| :---- |

### **Layer-by-Layer Explanation**

**Raw Zone (S3):** The single raw export file is uploaded as-is into an S3 bucket under a /raw prefix. No transformation happens here — this is the immutable source of truth for the pipeline.

**AWS Lambda (required trigger):** An S3 PUT event on the /raw prefix invokes a Lambda function, which starts the PySpark ETL job (for example, by submitting an AWS Glue job or an EMR step). This removes the need for a person to manually trigger the pipeline every time a new export arrives, and is a required part of this architecture, not an optional add-on.

**PySpark ETL:** A PySpark job reads the raw file from S3, splits it into the customers/products/orders working extracts described in Section 2, applies cleaning and validation rules, computes derived fields (e.g., line\_total, customer\_segment), and writes curated output back to S3 under a /curated prefix in Parquet format.

**Curated Zone (S3):** Holds the cleaned, split, and validated datasets that are ready to be loaded into the relational database. Keeping a curated zone in S3 (rather than loading directly from raw) makes the pipeline easier to debug and re-run.

**AWS RDS (PostgreSQL):** The curated data is loaded into a PostgreSQL database hosted on RDS, modeled using the schema in Section 5\. This becomes the queryable reporting layer for SQL analysis and dashboards.

**Visualization Layer:** Matplotlib and Seaborn are used for static analytical charts; an optional Streamlit app can be layered on top of RDS for an interactive dashboard experience.

## **Section 4 — Cloud Services Used**

This project intentionally limits scope to the following AWS services. No additional managed services should be introduced without instructor approval.

| Service | Role in Pipeline | Why This Service |
| :---- | :---- | :---- |
| Amazon S3 | Raw and curated data storage (zone-based) | Low-cost, durable object storage that cleanly separates the raw source export from transformed output, and is the natural landing zone for batch CSV ingestion. |
| AWS RDS (PostgreSQL) | Relational reporting database | Provides a managed, SQL-queryable store for curated data, supporting the joins, aggregations, and window functions required in Section 8\. |
| AWS Lambda (required) | Triggers the ETL job automatically whenever a new file lands in the S3 raw zone | This is a required part of the architecture: it removes manual pipeline kick-off and demonstrates event-driven automation, a pattern you will be expected to explain and defend. |
| CloudWatch (optional) | Basic logging and monitoring of the Lambda trigger and ETL job | Gives visibility into pipeline runs and failures without introducing a dedicated observability stack. |

## **Section 5 — Database Design**

The schema below is the suggested target structure your ETL pipeline should produce once the single raw export has been split, cleaned, and enriched. Every dimension and fact column is either a direct carry-over from the real source columns (InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country) or a clearly-labeled derived column computed during ETL — there are no invented source fields.

### **Table: dim\_customers**

| Column | Type | Key | Notes |
| :---- | :---- | :---- | :---- |
| customer\_id | INT | PK | ← CustomerID |
| country | VARCHAR(80) | — | ← Country |
| customer\_segment | VARCHAR(40) | — | Derived: RFM (Recency/Frequency/Monetary) scoring computed during ETL |

### 

### 

### **Table: dim\_products**

| Column | Type | Key | Notes |
| :---- | :---- | :---- | :---- |
| product\_id | VARCHAR(20) | PK | ← StockCode |
| product\_name | VARCHAR(150) | — | ← Description |
| avg\_unit\_price | DECIMAL(10,2) | — | Derived: average UnitPrice for this StockCode across all transactions |

### **Table: fact\_orders**

| Column | Type | Key | Notes |
| :---- | :---- | :---- | :---- |
| order\_line\_id | BIGINT | PK | Surrogate key generated during ETL |
| order\_id | VARCHAR(20) | — | ← InvoiceNo; can repeat across line items |
| customer\_id | INT | FK → dim\_customers |  |
| product\_id | VARCHAR(20) | FK → dim\_products |  |
| order\_date | TIMESTAMP | — | ← InvoiceDate |
| quantity | INT | — | ← Quantity |
| unit\_price | DECIMAL(10,2) | — | ← UnitPrice |
| line\_total | DECIMAL(12,2) | — | Derived: quantity × unit\_price |
| order\_status | VARCHAR(20) | — | Derived: 'Cancelled' if InvoiceNo starts with 'C', else 'Completed' |

### **Table: analytics.revenue\_summary**

| Column | Type | Key | Notes |
| :---- | :---- | :---- | :---- |
| summary\_id | BIGINT | PK | Surrogate key generated during ETL |
| country | VARCHAR(80) | — |  |
| month | DATE | — | First day of the calendar month being summarized |
| total\_revenue | DECIMAL(14,2) | — |  |
| total\_orders | INT | — |  |
| average\_order\_value | DECIMAL(10,2) | — |  |

### **Table: analytics.customer\_retention**

| Column | Type | Key | Notes |
| :---- | :---- | :---- | :---- |
| retention\_id | BIGINT | PK | Surrogate key generated during ETL |
| customer\_id | INT | FK → dim\_customers |  |
| total\_orders | INT | — |  |
| lifetime\_spend | DECIMAL(14,2) | — |  |
| first\_order\_date | DATE | — |  |
| last\_order\_date | DATE | — |  |
| customer\_status | VARCHAR(30) | — | New, Repeat, or Lapsed |

### **Table: analytics.product\_performance**

| Column | Type | Key | Notes |
| :---- | :---- | :---- | :---- |
| performance\_id | BIGINT | PK | Surrogate key generated during ETL |
| product\_id | VARCHAR(20) | FK → dim\_products |  |
| month | DATE | — | First day of the calendar month being summarized |
| units\_sold | INT | — |  |
| total\_revenue | DECIMAL(14,2) | — |  |
| overall\_rank | INT | — | Rank of this product by total revenue across the whole catalog, computed via window function |

### **Relationships**

* fact\_orders.customer\_id → dim\_customers.customer\_id (many-to-one)

* fact\_orders.product\_id → dim\_products.product\_id (many-to-one)

* analytics.customer\_retention.customer\_id → dim\_customers.customer\_id (many-to-one)

* analytics.product\_performance.product\_id → dim\_products.product\_id (many-to-one)

* analytics.revenue\_summary and analytics.product\_performance are both aggregated from fact\_orders during the ETL transformation stage described in Section 6\.

### **ER Diagram Description**

dim\_customers and dim\_products sit on either side of fact\_orders in a classic star schema. fact\_orders holds one row per order line item and carries foreign keys to both dimension tables, plus the computed line\_total used across all revenue-related use cases. The three analytics.\* tables are derived reporting tables built during ETL directly from fact\_orders (and, where relevant, the dimension tables); they are written into the same AWS RDS PostgreSQL database as separate physical tables so that dashboards and SQL analysis can query pre-aggregated results instead of recomputing aggregates on every read.

## **Section 6 — ETL Pipeline**

### **Extraction**

* Read the single raw export (online\_retail\_II.csv) from the S3 raw zone using PySpark's reader with an explicit schema (do not rely on schema inference for production-style runs).

* Split the raw export into three working extracts: select distinct CustomerID/Country pairs into customers.csv, distinct StockCode/Description pairs into products.csv, and the full transaction rows (with foreign keys) into orders.csv.

* Log row counts immediately after read and after the split to compare against post-transformation counts.

### **Transformation**

* Trim whitespace and standardize casing in text fields (Description, Country).

* Parse InvoiceDate into a proper timestamp type.

* Join orders with dim\_customers and dim\_products to validate referential integrity.

* Compute line\_total \= quantity × unit\_price.

* Derive order\_status from the InvoiceNo prefix: rows where InvoiceNo starts with 'C' are classified as 'Cancelled'; all others as 'Completed'.

* Compute customer\_segment per customer using RFM (Recency, Frequency, Monetary) scoring over order\_date, order count, and lifetime spend.

* Compute avg\_unit\_price per product as the mean UnitPrice observed for that StockCode across all transactions.

### **Loading**

* Write curated DataFrames to the S3 curated zone in Parquet format.

* Load curated tables into AWS RDS PostgreSQL using JDBC, mapping to the schema in Section 5\.

* Use upsert/overwrite logic (not blind append) so repeated pipeline runs do not create duplicate rows.

### **Data Quality Checks**

* Row-count reconciliation between the raw file and the curated layer, with discrepancies logged.

* Null checks on all primary and foreign key columns prior to load.

* Range checks on quantity (non-zero; negative values are valid only for documented return/adjustment rows) and unit\_price (\>= 0).

### **Deduplication Strategy**

Exact duplicate rows (identical InvoiceNo, StockCode, Quantity, and InvoiceDate appearing more than once) are identified using a window function partitioned by these keys; only the first occurrence is retained, and duplicates are logged to a separate rejected-records output for traceability.

### **Missing Value Handling**

* Rows with a null CustomerID in the source (a known, documented characteristic of this dataset) are retained in orders.csv but excluded from customer-level fact joins and from analytics.customer\_retention, since they cannot be attributed to a specific customer.

* Rows with a missing or unresolvable StockCode are routed to a rejected-records file and excluded from fact\_orders.

* Missing or blank Description values default to 'Unknown Product' rather than being dropped, since the row may still carry valid revenue information.

### **Validation Rules**

* InvoiceDate must fall within the dataset's known operating window (December 2009 – December 2011); rows outside this window are flagged.

* Quantity must be a non-zero integer; rows with Quantity \= 0 are rejected as likely data entry errors.

* UnitPrice must be non-negative; negative-price rows are flagged for review rather than silently accepted.

## **Section 7 — Business Use Cases**

Each use case below follows the Nagendra-style format: a clear topic, business goal, step-by-step ETL flow, output table, dashboard output, and the business insight the use case is designed to surface.

### **Use Case 1: Revenue Analysis**

**Business Goal:** Help merchandising and finance teams understand which countries, products, and time periods drive the most revenue.

**ETL Flow:**

1. PySpark reads fact\_orders and computes line\_total per order line.

2. Aggregate revenue by country and calendar month.

3. Write results into a dedicated reporting table in RDS.

**Output Table:** [analytics.revenue\_summary](#bookmark=id.vu5rhosfvcyy)  *(see Section 5 — Database Design)*

**Dashboard Output:** A monthly revenue trend line chart alongside a bar chart of revenue by country, plus KPI cards for total revenue and average order value.

**Expected Business Insight:** Identifies the top revenue-driving countries and reveals month-over-month growth or decline, enabling promotional and logistics decisions.

### **Use Case 2: Customer Retention**

**Business Goal:** Help the marketing team identify loyal, high-value customers and flag customers at risk of churn.

**ETL Flow:**

1. PySpark joins fact\_orders with dim\_customers and computes order frequency and total spend per customer.

2. Classify customers into segments (e.g., New, Repeat, Lapsed) based on order recency and frequency.

3. Write the classified customer table into RDS.

**Output Table:** [analytics.customer\_retention](#bookmark=id.3luvd8wt2nf1)  *(see Section 5 — Database Design)*

**Dashboard Output:** A customer segment distribution pie chart, a bar chart of top 10 customers by lifetime value, and a KPI card for repeat purchase rate.

**Expected Business Insight:** Surfaces which customer segments contribute most to revenue and highlights lapsed high-value customers worth re-engaging.

### **Use Case 3: Product Performance**

**Business Goal:** Help the product team understand which items are top sellers and which are underperforming.

**ETL Flow:**

1. PySpark aggregates fact\_orders by product\_id to compute total units sold and total revenue per product.

2. Rank products across the whole catalog using a window function.

3. Write the ranked product performance table into RDS.

**Output Table:** [analytics.product\_performance](#bookmark=id.z7p75m7892kg)  *(see Section 5 — Database Design)*

**Dashboard Output:** A line chart of revenue trend for the top 5 products, a bar chart of top and bottom 5 products by units sold, and a table of overall rankings.

**Expected Business Insight:** Reveals which products to restock or promote, and which underperforming products may be candidates for discontinuation.

## **Section 8 — SQL Requirements**

Complete the following 10 SQL tasks against your curated database. Save all scripts under sql/analysis\_queries/ in your repository.

| \# | Task | SQL Concept(s) |
| :---- | :---- | :---- |
| 1 | Write a query to return total revenue per country, sorted descending. | Joins, Group By, Aggregation |
| 2 | Write a query to return the top 10 customers by total lifetime spend. | Joins, Group By, Order By, Limit |
| 3 | Create a view that exposes monthly revenue trends across all countries. | Views, Date Functions, Aggregation |
| 4 | Write a query to rank products across the catalog by total revenue using a window function. | Window Functions (RANK/DENSE\_RANK) |
| 5 | Write a query to find customers who placed orders in two consecutive months. | Subqueries, Self-Join or Window Functions |
| 6 | Write a query to compute the running total of revenue by month. | Window Functions (SUM OVER) |
| 7 | Write a query to identify products with zero sales in the last 60 days of the dataset window. | Subqueries, Date Filtering, Anti-Join |
| 8 | Write a query to compute average order value per customer segment. | Joins, Group By, Aggregation |
| 9 | Create a view summarizing order status distribution (Completed vs. Cancelled). | Views, Group By |
| 10 | Write a query to find the top-selling product in each country. | Joins, Window Functions, Partitioning |

## **Section 9 — PySpark Requirements**

Complete the following 10 PySpark tasks as part of your transformation layer. Save all scripts under pyspark/transformation/ in your repository.

| \# | Task | PySpark Concept(s) |
| :---- | :---- | :---- |
| 1 | Read the raw export with an explicitly defined schema and split it into the three working extracts. | Schema Definition, DataFrame Reader, Transformations |
| 2 | Filter out order line items with zero quantity. | Filtering |
| 3 | Join orders with customers and products to build a denormalized working DataFrame. | Joins |
| 4 | Compute line\_total as a new derived column. | Column Transformations |
| 5 | Deduplicate order line items using a window function partitioned by InvoiceNo, StockCode, and InvoiceDate. | Window Functions, Deduplication |
| 6 | Aggregate total revenue and order count per customer. | Aggregation, GroupBy |
| 7 | Rank products across the catalog by total revenue. | Window Functions (rank/dense\_rank) |
| 8 | Standardize and clean text fields (trim, title-case Description and Country values). | Data Cleaning, String Functions |
| 9 | Derive order\_status from the InvoiceNo prefix. | Conditional Column Logic |
| 10 | Write the final curated DataFrames to S3 in Parquet format, partitioned by order year-month. | Partitioned Writes, Output Formats |

## **Section 10 — Data Visualization Requirements**

AWS projects use Matplotlib and Seaborn for core analytical charts, with an optional Streamlit app for an interactive dashboard experience layered directly on top of the RDS reporting tables.

### **Required Charts**

| Chart Type | Used For |
| :---- | :---- |
| Line Chart | Monthly revenue trend over the dataset's two-year window. |
| Bar Chart | Revenue by country and top/bottom 5 products by units sold. |
| Pie Chart | Customer segment distribution (New, Repeat, Lapsed). |
| Histogram | Distribution of order values across all completed orders. |
| Heatmap | Country-by-month revenue intensity. |
| KPI Cards | Total revenue, average order value, repeat purchase rate. |

## **Section 11 — Test Cases**

Execute and log all 15 test cases below before final submission. Record actual results in testing/test\_cases.xlsx.

| TC ID | Scenario | Expected Result |
| :---- | :---- | :---- |
| TC-01 | Exact duplicate transaction row in the raw export | Duplicates removed during PySpark transformation; only first occurrence retained. |
| TC-02 | Order row with a null CustomerID | Retained in orders.csv but excluded from customer-level joins and analytics.customer\_retention. |
| TC-03 | Order line with zero quantity | Row rejected during transformation and logged. |
| TC-04 | InvoiceDate outside the known dataset window | Row flagged for review; not silently loaded. |
| TC-05 | Negative UnitPrice on a row | Row flagged for manual review rather than auto-corrected. |
| TC-06 | Missing or blank Description value | Defaulted to 'Unknown Product' during transformation. |
| TC-07 | Re-running the ETL pipeline twice on the same raw data | No duplicate rows created in fact\_orders (idempotent load). |
| TC-08 | Customer with zero non-cancelled orders in the dataset | Customer still appears in dim\_customers but excluded from revenue aggregates. |
| TC-09 | Product with zero sales in the period | Product appears in dim\_products and is correctly surfaced in the 'underperforming products' use case. |
| TC-10 | Cancelled invoice (InvoiceNo starting with 'C') included in raw data | Order is loaded but excluded from revenue totals unless explicitly included in a cancellation-analysis query. |
| TC-11 | SQL revenue-by-country query | Sum of country revenues equals total revenue in fact\_orders for completed orders. |
| TC-12 | Window function ranking query for top products | Ranks are correctly computed across the catalog with no ties mishandled. |
| TC-13 | Lambda trigger fires on new file upload to the raw zone | ETL job starts automatically without manual intervention, and a CloudWatch log entry is recorded. |
| TC-14 | RDS connection failure during load step | Pipeline fails gracefully with a clear error message; no partial/corrupt writes. |
| TC-15 | Dashboard refresh after new data load | KPI cards and charts reflect updated totals without manual recalculation. |

## **Section 12 — Documentation Requirements**

Your team must produce ONE consolidated documentation file (Word or PDF) covering the entire project. It must include the following sections, in this order:

1. Project Overview

2. Dataset Details

3. Architecture Diagram

4. Cloud Resources

5. Database Design

6. ETL Flow

7. SQL Analysis

8. Visualizations

9. Testing

10. Challenges

11. Learnings

12. Conclusion

| Tip Use this handbook's section structure as your documentation outline — each section in your final write-up should map directly to a section in this handbook so reviewers can cross-check your work quickly. |
| :---- |

## **Section 13 — GitHub Repository Structure**

Use the following structure for the ecommerce-sales-analytics-pipeline repository. This mirrors the standard defined in the handbook front matter, applied to your specific project.

| ecommerce-sales-analytics-pipeline/ ├── README.md ├── documentation/ │   └── Project\_Documentation.docx ├── architecture/ │   └── architecture\_diagram.png ├── datasets/ │   ├── online\_retail\_II.csv (raw source) │   ├── customers.csv (derived working extract) │   ├── products.csv (derived working extract) │   ├── orders.csv (derived working extract) ├── sql/ │   ├── schema/ │   └── analysis\_queries/ ├── pyspark/ │   ├── extraction/ │   ├── transformation/ │   └── loading/ ├── screenshots/ ├── testing/ │   └── test\_cases.xlsx └── visualizations/ |
| :---- |

## **Section 14 — Expected Screenshots**

Capture and store the following screenshots under screenshots/ in your repository, and reference them inside your consolidated documentation:

* S3 bucket structure showing raw and curated zones

* AWS Lambda function configuration and a successful trigger execution log

* AWS RDS instance and connected database tables

* PySpark job execution output/logs

* SQL query results for at least 3 analysis tasks

* Matplotlib/Seaborn dashboard charts (or Streamlit app screenshot)

* GitHub repository structure

* Test case execution log

