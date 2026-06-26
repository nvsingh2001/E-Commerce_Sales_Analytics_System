# E-Commerce Sales Analytics Pipeline

This repository contains the source code, SQL queries, database schema definitions, and automated test runners for the E-Commerce Sales Analytics Pipeline project.

## Project Structure
- `sql/`: Database schema and analytical query scripts.
- `pyspark/`: PySpark ETL pipeline implementation.
- `testing/`: Modular unit test suites.
- `visualizations/`: Dashboard and static visualization scripts.
- `documentation/`: Developer guidelines and plans.

## Team & Roles
- **Ayush Singh:** Lead Platform & Visuals (AWS Infrastructure, database schema, SQL queries, Streamlit dashboard, Word document generator).
- **Naman Vinay Singh (Primary User):** Lead Data Pipelines & Quality (OOP PySpark ETL code structure, strategy rules, modular testing suites).

## Branching Workflow
1. `main`: Contains clean, tested releases.
2. `dev`: Active integration branch.
3. Feature branches: Checked out of `dev` and merged back to `dev` upon code verification:
   - `feature/01-infrastructure`
   - `feature/02-database-schema`
   - `feature/03-pyspark-etl`
   - `feature/04-visualizations`
   - `feature/05-testing`

## Full Project Documentation
The final project report, architectural diagrams, and analysis results are available in the **[Project Documentation](documentation/Project_Documentation.md)**.

*Note: Raw datasets, virtual environments, configuration secrets (`.env`), and test logs are kept local and excluded from version control.*
