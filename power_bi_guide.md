# Power BI & Snowflake Integration Guide

Follow these steps to connect your GitHub dataset to Power BI for real-time analytics.

## Prerequisites
1.  **Power BI Desktop** installed.
2.  **Snowflake Connector** (usually built into Power BI).

## Connection Steps

### 1. Get Connection Details
Use the following details from your `.env` file:
- **Server**: `gnitsrf-ar75548.snowflakecomputing.com` (Account URL)
- **Warehouse**: `COMPUTE_WH`
- **Database**: `GITSTAR_DB`
- **Schema**: `PUBLIC`

### 2. Connect in Power BI
1.  Open Power BI Desktop.
2.  Click **Get Data** -> **More...** -> **Database** -> **Snowflake**.
3.  **Server**: Enter `gnitsrf-ar75548.snowflakecomputing.com`.
4.  **Warehouse**: Enter `COMPUTE_WH`.
5.  **Data Connectivity Mode**: Select **DirectQuery** (for real-time updates).
6.  Click **OK**.

### 3. Authentication
1.  Select **Database** authentication.
2.  **User name**: `SIDDHESH123`
3.  **Password**: `Siddhesh@123456789`
4.  Click **Connect**.

### 4. Select Views
In the Navigator window, expand `GITSTAR_DB` -> `PUBLIC` and select:
- `DASHBOARD_REPO_SUMMARY`
- `DASHBOARD_COMMIT_TRENDS`
- `DASHBOARD_PR_INSIGHTS`

Click **Load**.

## Suggested Visuals
1.  **Commit Velocity**: Use a Line Chart with `COMMIT_DAY` on the Axis and `COUNT(SHA)` as the Value.
2.  **Language Distribution**: Use a Pie Chart with `LANGUAGE` and `COUNT(REPO_ID)`.
3.  **PR Efficiency**: Use a Table or Gauge for `DAYS_TO_MERGE`.
4.  **Top Contributors**: Use a Bar Chart with `AUTHOR_NAME` and `COUNT(SHA)`.

---
*Note: Your Snowflake account is set to auto-resume the warehouse when queried, ensuring your dashboard stays updated.*
