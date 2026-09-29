# 🏃 Fitness Activity SQL Analytics Dashboard

## 📌 Project Overview

The **Fitness Activity SQL Analytics Dashboard** is a data analytics project designed to analyze fitness tracker data using **Python, SQL, SQLite, Pandas, and Streamlit**.

The project combines daily activity, calorie, distance, intensity, and sleep information into a cleaned dataset and performs SQL-based analysis to identify user activity patterns, calorie expenditure, sleep behavior, sedentary time, and overall fitness trends.

An interactive **Streamlit dashboard** is developed to present the analysis through KPI cards, filters, interactive charts, SQL query results, and business insights.

---

## 🎯 Project Objective

The main objectives of this project are:

* Clean and prepare fitness activity data for analysis.
* Store the cleaned dataset in a SQLite database.
* Perform SQL analysis using real-world fitness data.
* Analyze user activity and daily step patterns.
* Analyze calorie expenditure.
* Analyze active and sedentary minutes.
* Analyze sleep duration and sleep efficiency.
* Identify highly active and sedentary users.
* Compare activity levels across different days.
* Build an interactive Streamlit dashboard.
* Provide data-driven insights for fitness behavior analysis.

---

## 🛠️ Technologies Used

| Technology   | Purpose                                     |
| ------------ | ------------------------------------------- |
| Python       | Data processing and application development |
| Pandas       | Data cleaning and analysis                  |
| NumPy        | Numerical operations                        |
| SQLite       | SQL database and analysis                   |
| SQL          | Data querying and aggregation               |
| Streamlit    | Interactive dashboard                       |
| Plotly       | Interactive visualizations                  |
| Google Colab | Development and analysis environment        |
| GitHub       | Project version control                     |

---

## 📂 Project Structure

```text
Fitness-Activity-SQL-Analytics/
│
├── fitness_data_cleaned(2).csv
├── fitness_sql_streamlit_app.py
├── fitness_database.db
└── README.md
```

---

# 📊 Dataset

The project uses a merged and cleaned fitness tracker dataset containing information related to:

### Activity

* User ID
* Activity Date
* Total Steps
* Total Distance
* Tracker Distance
* Logged Activity Distance

### Activity Intensity

* Very Active Distance
* Moderately Active Distance
* Light Active Distance
* Sedentary Active Distance
* Very Active Minutes
* Fairly Active Minutes
* Lightly Active Minutes
* Sedentary Minutes

### Calories

* Calories
* Daily Calories

### Sleep

* Total Sleep Records
* Total Minutes Asleep
* Total Time in Bed
* Sleep Data Availability

### Date Features

* Year
* Month
* Day
* Day of Week
* Week

---

# 🧹 Data Cleaning

The raw fitness datasets were merged and cleaned before SQL analysis.

The following cleaning steps were performed:

1. Loaded the merged CSV using Pandas.
2. Inspected rows, columns, and data types.
3. Checked missing values.
4. Checked duplicate records.
5. Standardized column names.
6. Converted date columns into datetime format.
7. Removed redundant columns.
8. Checked for negative and invalid numeric values.
9. Identified columns with excessive missing values.
10. Preserved missing sleep information rather than incorrectly replacing it with zero.
11. Created a `SleepDataAvailable` indicator.
12. Created useful date-based columns.
13. Sorted records by user and activity date.
14. Performed final data-quality validation.
15. Exported the cleaned dataset as CSV.

---

# 🗄️ SQL Database

The cleaned CSV is loaded into an **SQLite database** using Pandas.

```python
import sqlite3

conn = sqlite3.connect("fitness_database.db")

df.to_sql(
    "fitness",
    conn,
    if_exists="replace",
    index=False
)
```

The main SQL table is:

```text
fitness
```

---

# 🧮 SQL Analysis

The project performs multiple SQL analyses.

## 1. Overall KPI Analysis

```sql
SELECT
    COUNT(*) AS Total_Records,
    COUNT(DISTINCT Id) AS Total_Users,
    ROUND(AVG(TotalSteps), 2) AS Average_Steps,
    ROUND(AVG(Calories), 2) AS Average_Calories,
    ROUND(AVG(TotalDistance), 2) AS Average_Distance
FROM fitness;
```

---

## 2. Top 10 Users by Average Steps

```sql
SELECT
    Id,
    COUNT(*) AS Days_Tracked,
    ROUND(AVG(TotalSteps), 2) AS Average_Steps
FROM fitness
GROUP BY Id
ORDER BY Average_Steps DESC
LIMIT 10;
```

---

## 3. Activity by Day of Week

```sql
SELECT
    DayOfWeek,
    COUNT(*) AS Records,
    ROUND(AVG(TotalSteps), 2) AS Average_Steps,
    ROUND(AVG(Calories), 2) AS Average_Calories
FROM fitness
GROUP BY DayOfWeek
ORDER BY Average_Steps DESC;
```

---

## 4. Activity Classification

Users/activity records are classified into three groups:

```text
Low       → Less than 5,000 steps
Moderate  → 5,000–9,999 steps
High      → 10,000+ steps
```

SQL:

```sql
SELECT
    CASE
        WHEN TotalSteps < 5000 THEN 'Low'
        WHEN TotalSteps < 10000 THEN 'Moderate'
        ELSE 'High'
    END AS Activity_Band,
    COUNT(*) AS Records,
    ROUND(AVG(TotalSteps), 2) AS Average_Steps,
    ROUND(AVG(Calories), 2) AS Average_Calories
FROM fitness
GROUP BY Activity_Band;
```

---

## 5. 10,000+ Step Analysis

```sql
SELECT
    COUNT(*) AS Days_Over_10000_Steps
FROM fitness
WHERE TotalSteps >= 10000;
```

---

## 6. Sleep Analysis

```sql
SELECT
    COUNT(*) AS Sleep_Records,
    ROUND(AVG(TotalMinutesAsleep), 2)
        AS Average_Sleep_Minutes,
    ROUND(AVG(TotalTimeInBed), 2)
        AS Average_Time_In_Bed
FROM fitness
WHERE SleepDataAvailable = 1;
```

---

## 7. Sleep Efficiency

```sql
SELECT
    ROUND(
        AVG(
            CASE
                WHEN TotalTimeInBed > 0
                THEN TotalMinutesAsleep * 100.0
                     / TotalTimeInBed
            END
        ),
        2
    ) AS Average_Sleep_Efficiency
FROM fitness
WHERE SleepDataAvailable = 1;
```

---

## 8. Most Sedentary Users

```sql
SELECT
    Id,
    ROUND(
        AVG(SedentaryMinutes), 2
    ) AS Average_Sedentary_Minutes
FROM fitness
GROUP BY Id
ORDER BY Average_Sedentary_Minutes DESC
LIMIT 10;
```

---

## 9. User Ranking

The project also demonstrates SQL window functions.

```sql
WITH UserActivity AS (
    SELECT
        Id,
        ROUND(AVG(TotalSteps), 2)
            AS Average_Steps
    FROM fitness
    GROUP BY Id
)

SELECT
    Id,
    Average_Steps,
    RANK() OVER (
        ORDER BY Average_Steps DESC
    ) AS Activity_Rank
FROM UserActivity
ORDER BY Activity_Rank;
```

---

# 📈 Streamlit Dashboard

The Streamlit application provides an interactive interface for exploring the fitness data.

## Dashboard Features

### 🔍 Filters

Users can filter the dashboard by:

* Activity date range
* User ID
* Day of week

---

## 📌 KPI Cards

The dashboard displays:

* 👥 Total Users
* 📅 Total Records
* 👟 Average Steps
* 🔥 Average Calories
* 😴 Average Sleep

---

# 📊 Interactive Visualizations

The dashboard contains several interactive Plotly charts.

### Activity Analysis

* Top 10 Users by Average Steps
* Average Steps by Day of Week
* Steps vs Calories
* Sleep Duration vs Steps

### Activity Classification

* Records by Activity Band
* Average Calories by Activity Band

### Sleep Analysis

* Sleep Duration Groups
* Sleep Duration Distribution

---

# 🧮 SQL Analysis Section

The dashboard provides a dropdown containing multiple predefined SQL analyses.

Users can select an analysis and view:

1. SQL query
2. Query results
3. Downloadable CSV output

---

# 💻 Custom SQL

The application also provides a custom SQL query interface.

Example:

```sql
SELECT
    Id,
    AVG(TotalSteps) AS Average_Steps
FROM fitness
GROUP BY Id
ORDER BY Average_Steps DESC;
```

Users can execute their own SQL queries directly from the Streamlit dashboard.

---

# 💡 Key Insights

The analysis provides several useful observations:

* The dataset contains activity records from multiple users across multiple dates.
* Average daily steps provide an overall measure of user activity.
* Higher activity bands generally show higher average calorie expenditure in the dataset.
* A substantial portion of activity records fall into moderate and low step ranges.
* Sleep records are available only for a subset of activity records.
* Average recorded sleep can be analyzed independently of days where sleep was not tracked.
* Sedentary minutes provide an additional perspective beyond step counts.
* Comparing activity by day of week helps identify differences in activity patterns.
* Comparing steps and calories helps explore the relationship between physical activity and energy expenditure.
* SQL window functions can be used to rank users based on activity.

> These observations describe patterns in this dataset and should not be interpreted as medical conclusions.

---

# 🚀 How to Run the Project

## Step 1: Clone the Repository

```bash
git clone <your-github-repository-url>
```

```bash
cd Fitness-Activity-SQL-Analytics
```

---

## Step 2: Install Dependencies

Create a `requirements.txt` file containing:

```text
pandas
numpy
streamlit
plotly
```

Install:

```bash
pip install -r requirements.txt
```

---

## Step 3: Verify Dataset

Make sure these files are in the same folder:

```text
fitness_sql_streamlit_app.py
fitness_data_cleaned(2).csv
```

---

## Step 4: Run Streamlit

```bash
streamlit run fitness_sql_streamlit_app.py
```

The application will open in your browser.

---

# ☁️ Running in Google Colab

Install the required packages:

```python
!pip install -q streamlit plotly pyngrok
```

Run the application:

```python
!streamlit run fitness_sql_streamlit_app.py &>/content/logs.txt &
```

Then create a public tunnel using your preferred tunneling service.

---

# 📥 Project Outputs

The project produces:

```text
fitness_data_cleaned.csv
```

and SQL analysis results can be exported from the dashboard as:

```text
sql_analysis_result.csv
```

---

# 🎯 Business Use Cases

This project can be used to:

* Monitor fitness activity
* Identify highly active users
* Analyze sedentary behavior
* Track calorie expenditure
* Analyze sleep patterns
* Compare activity across days
* Identify activity trends
* Build fitness dashboards
* Demonstrate SQL data-analysis skills
* Demonstrate Python and Streamlit skills

---

# 🧠 Skills Demonstrated

This project demonstrates practical knowledge of:

### Python

* Pandas
* NumPy
* Data cleaning
* Data transformation

### SQL

* `SELECT`
* `WHERE`
* `GROUP BY`
* `HAVING`
* `ORDER BY`
* `COUNT`
* `AVG`
* `MAX`
* `CASE`
* Subqueries
* CTEs
* Window functions
* `RANK()`
* Aggregations

### Visualization

* Plotly
* Interactive charts
* KPI dashboards

### Application Development

* Streamlit
* Sidebar filters
* Interactive SQL
* CSV export
* SQLite integration

---

# 🔮 Future Enhancements

Potential improvements include:

* Add user-level drill-down pages.
* Add weekly and monthly trend analysis.
* Add additional activity categories.
* Add correlation analysis.
* Add machine-learning-based activity prediction.
* Add user segmentation.
* Add recommendation functionality.
* Add downloadable PDF reports.
* Deploy the dashboard using Streamlit Community Cloud.
* Add authentication and user access control.

---

# 👩‍💻 Author

**Ekta**

**Data Analytics Project**

Skills demonstrated:

`Python` · `SQL` · `Pandas` · `SQLite` · `Streamlit` · `Plotly` · `Data Visualization` · `Data Cleaning`

---

## ⭐ Project Summary

**Fitness Activity SQL Analytics Dashboard** transforms raw fitness tracker data into an interactive analytical solution. The project demonstrates the complete data analytics workflow—from **data cleaning and SQL analysis to interactive visualization and dashboard development**—using Python, SQLite, SQL, and Streamlit.
