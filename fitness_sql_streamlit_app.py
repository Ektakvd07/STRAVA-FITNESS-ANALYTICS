import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Fitness SQL Analytics Dashboard",
    page_icon="🏃",
    layout="wide"
)

DATA_FILE = "fitness_data_cleaned.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    df["ActivityDate"] = pd.to_datetime(df["ActivityDate"], errors="coerce")
    return df

@st.cache_resource
def create_database():
    df = load_data()
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    df.to_sql("fitness", conn, if_exists="replace", index=False)
    return conn

df = load_data()
conn = create_database()

def sql_query(query):
    return pd.read_sql_query(query, conn)

# ---------------- Sidebar ----------------
st.sidebar.title("🏃 Fitness Dashboard")
st.sidebar.subheader("Filters")

min_date = df["ActivityDate"].min().date()
max_date = df["ActivityDate"].max().date()

date_range = st.sidebar.date_input(
    "Activity Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

user_options = sorted(df["Id"].unique())
selected_users = st.sidebar.multiselect(
    "User ID",
    user_options,
    default=[]
)

day_options = sorted(df["DayOfWeek"].dropna().unique())
selected_days = st.sidebar.multiselect(
    "Day of Week",
    day_options,
    default=[]
)

filtered = df.copy()

if isinstance(date_range, tuple) and len(date_range) == 2:
    filtered = filtered[
        (filtered["ActivityDate"].dt.date >= date_range[0]) &
        (filtered["ActivityDate"].dt.date <= date_range[1])
    ]

if selected_users:
    filtered = filtered[filtered["Id"].isin(selected_users)]

if selected_days:
    filtered = filtered[filtered["DayOfWeek"].isin(selected_days)]

# ---------------- Header ----------------
st.title("🏃 Fitness Activity SQL Analytics Dashboard")
st.markdown(
    "Interactive fitness analysis powered by **Python, SQLite SQL, Pandas and Plotly**."
)

st.info(
    "The SQL Analysis section executes SQL queries directly against the SQLite "
    "`fitness` table created from the cleaned CSV."
)

# ---------------- KPIs ----------------
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("👥 Users", f"{filtered['Id'].nunique():,}")
c2.metric("📅 Records", f"{len(filtered):,}")
c3.metric("👟 Avg Steps", f"{filtered['TotalSteps'].mean():,.0f}")
c4.metric("🔥 Avg Calories", f"{filtered['Calories'].mean():,.0f}")
sleep_avg = filtered["TotalMinutesAsleep"].mean()
c5.metric("😴 Avg Sleep", f"{sleep_avg/60:.1f} hrs" if pd.notna(sleep_avg) else "N/A")

st.divider()

# ---------------- Dataset Preview ----------------
st.header("📋 Dataset Preview")
st.dataframe(filtered.head(20), use_container_width=True)

with st.expander("Dataset Information"):
    st.write(f"Rows after filters: **{len(filtered):,}**")
    st.write(f"Columns: **{len(filtered.columns):,}**")
    st.write("Missing values:")
    st.dataframe(filtered.isna().sum().to_frame("Missing Values"))

# ---------------- Activity Overview ----------------
st.header("📊 Activity Analysis")

col1, col2 = st.columns(2)

with col1:
    user_activity = (
        filtered.groupby("Id", as_index=False)["TotalSteps"]
        .mean()
        .sort_values("TotalSteps", ascending=False)
        .head(10)
    )
    fig = px.bar(
        user_activity,
        x="Id",
        y="TotalSteps",
        title="Top 10 Users by Average Steps",
        labels={"TotalSteps": "Average Steps", "Id": "User ID"}
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    day_activity = (
        filtered.groupby("DayOfWeek", as_index=False)["TotalSteps"]
        .mean()
    )
    order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    day_activity["DayOrder"] = day_activity["DayOfWeek"].map(
        {d:i for i,d in enumerate(order)}
    )
    day_activity = day_activity.sort_values("DayOrder")
    fig = px.line(
        day_activity,
        x="DayOfWeek",
        y="TotalSteps",
        markers=True,
        title="Average Steps by Day of Week",
        labels={"TotalSteps": "Average Steps", "DayOfWeek": "Day"}
    )
    st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    fig = px.scatter(
        filtered,
        x="TotalSteps",
        y="Calories",
        size="TotalDistance",
        hover_data=["Id", "ActivityDate"],
        title="Steps vs Calories",
        labels={"TotalSteps": "Total Steps", "Calories": "Calories"}
    )
    st.plotly_chart(fig, use_container_width=True)

with col4:
    sleep_df = filtered.dropna(subset=["TotalMinutesAsleep"])
    if len(sleep_df):
        fig = px.scatter(
            sleep_df,
            x="TotalMinutesAsleep",
            y="TotalSteps",
            size="Calories",
            hover_data=["Id", "ActivityDate"],
            title="Sleep Duration vs Steps",
            labels={
                "TotalMinutesAsleep": "Minutes Asleep",
                "TotalSteps": "Total Steps"
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No sleep records available for the selected filters.")

# ---------------- Activity Bands ----------------
st.header("🏷️ Activity Classification")

band_df = filtered.copy()
band_df["ActivityBand"] = pd.cut(
    band_df["TotalSteps"],
    bins=[-1, 4999, 9999, float("inf")],
    labels=["Low (<5K)", "Moderate (5K–9,999)", "High (10K+)"]
)

band_summary = (
    band_df.groupby("ActivityBand", observed=False)
    .agg(
        Records=("Id", "size"),
        Average_Steps=("TotalSteps", "mean"),
        Average_Calories=("Calories", "mean")
    )
    .reset_index()
)

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        band_summary,
        x="ActivityBand",
        y="Records",
        title="Records by Activity Band",
        text_auto=True
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(
        band_summary,
        x="ActivityBand",
        y="Average_Calories",
        title="Average Calories by Activity Band",
        text_auto=".0f"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Sleep ----------------
st.header("😴 Sleep Analysis")

sleep_available = filtered[filtered["SleepDataAvailable"] == 1].copy()

col1, col2 = st.columns(2)

with col1:
    if len(sleep_available):
        sleep_bins = pd.cut(
            sleep_available["TotalMinutesAsleep"],
            bins=[0, 360, 480, 1440],
            labels=["< 6 Hours", "6–8 Hours", "8+ Hours"]
        )
        sleep_counts = sleep_bins.value_counts().sort_index().reset_index()
        sleep_counts.columns = ["Sleep_Group", "Records"]

        fig = px.bar(
            sleep_counts,
            x="Sleep_Group",
            y="Records",
            title="Sleep Duration Groups",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if len(sleep_available):
        fig = px.histogram(
            sleep_available,
            x="TotalMinutesAsleep",
            nbins=25,
            title="Sleep Duration Distribution",
            labels={"TotalMinutesAsleep": "Minutes Asleep"}
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------- SQL Analysis ----------------
st.header("🧮 SQL Analysis")

st.markdown(
    "Each analysis below uses SQL against the SQLite `fitness` table."
)

queries = {
    "1. Overall KPI Summary": """
        SELECT
            COUNT(*) AS Total_Records,
            COUNT(DISTINCT Id) AS Total_Users,
            ROUND(AVG(TotalSteps), 2) AS Average_Steps,
            ROUND(AVG(Calories), 2) AS Average_Calories,
            ROUND(AVG(TotalDistance), 2) AS Average_Distance
        FROM fitness;
    """,

    "2. Top 10 Users by Average Steps": """
        SELECT
            Id,
            COUNT(*) AS Days_Tracked,
            ROUND(AVG(TotalSteps), 2) AS Average_Steps
        FROM fitness
        GROUP BY Id
        ORDER BY Average_Steps DESC
        LIMIT 10;
    """,

    "3. Activity by Day of Week": """
        SELECT
            DayOfWeek,
            COUNT(*) AS Records,
            ROUND(AVG(TotalSteps), 2) AS Average_Steps,
            ROUND(AVG(Calories), 2) AS Average_Calories
        FROM fitness
        GROUP BY DayOfWeek
        ORDER BY Average_Steps DESC;
    """,

    "4. Activity Band Analysis": """
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
        GROUP BY Activity_Band
        ORDER BY
            CASE Activity_Band
                WHEN 'Low' THEN 1
                WHEN 'Moderate' THEN 2
                ELSE 3
            END;
    """,

    "5. Days With 10,000+ Steps": """
        SELECT COUNT(*) AS Days_Over_10000_Steps
        FROM fitness
        WHERE TotalSteps >= 10000;
    """,

    "6. Days Below 5,000 Steps": """
        SELECT COUNT(*) AS Days_Under_5000_Steps
        FROM fitness
        WHERE TotalSteps < 5000;
    """,

    "7. Activity Intensity Summary": """
        SELECT
            ROUND(AVG(VeryActiveMinutes), 2) AS Avg_VeryActive_Minutes,
            ROUND(AVG(FairlyActiveMinutes), 2) AS Avg_FairlyActive_Minutes,
            ROUND(AVG(LightlyActiveMinutes), 2) AS Avg_LightlyActive_Minutes,
            ROUND(AVG(SedentaryMinutes), 2) AS Avg_Sedentary_Minutes
        FROM fitness;
    """,

    "8. Sleep Summary": """
        SELECT
            COUNT(*) AS Sleep_Records,
            ROUND(AVG(TotalMinutesAsleep), 2) AS Average_Sleep_Minutes,
            ROUND(AVG(TotalTimeInBed), 2) AS Average_Time_In_Bed
        FROM fitness
        WHERE SleepDataAvailable = 1;
    """,

    "9. Sleep Efficiency": """
        SELECT
            ROUND(
                AVG(
                    CASE
                        WHEN TotalTimeInBed > 0
                        THEN TotalMinutesAsleep * 100.0 / TotalTimeInBed
                    END
                ), 2
            ) AS Average_Sleep_Efficiency
        FROM fitness
        WHERE SleepDataAvailable = 1;
    """,

    "10. Most Sedentary Users": """
        SELECT
            Id,
            ROUND(AVG(SedentaryMinutes), 2) AS Average_Sedentary_Minutes
        FROM fitness
        GROUP BY Id
        ORDER BY Average_Sedentary_Minutes DESC
        LIMIT 10;
    """,

    "11. High Activity + High Calories": """
        SELECT
            Id,
            ActivityDate,
            TotalSteps,
            Calories
        FROM fitness
        WHERE TotalSteps >= 10000
          AND Calories >= 2500
        ORDER BY TotalSteps DESC;
    """,

    "12. User Ranking Using Window Function": """
        WITH UserActivity AS (
            SELECT
                Id,
                ROUND(AVG(TotalSteps), 2) AS Average_Steps
            FROM fitness
            GROUP BY Id
        )
        SELECT
            Id,
            Average_Steps,
            RANK() OVER (ORDER BY Average_Steps DESC) AS Activity_Rank
        FROM UserActivity
        ORDER BY Activity_Rank;
    """,

    "13. Users With More Than 20 Tracked Days": """
        SELECT
            Id,
            COUNT(*) AS Days_Tracked,
            ROUND(AVG(TotalSteps), 2) AS Average_Steps
        FROM fitness
        GROUP BY Id
        HAVING COUNT(*) > 20
        ORDER BY Days_Tracked DESC;
    """,

    "14. Distance Consistency": """
        SELECT
            ROUND(AVG(ABS(TotalDistance - TrackerDistance)), 3)
                AS Average_Distance_Gap,
            ROUND(MAX(ABS(TotalDistance - TrackerDistance)), 3)
                AS Maximum_Distance_Gap
        FROM fitness;
    """,

    "15. Monthly Activity": """
        SELECT
            Year,
            Month,
            COUNT(*) AS Records,
            ROUND(AVG(TotalSteps), 2) AS Average_Steps,
            ROUND(AVG(Calories), 2) AS Average_Calories,
            ROUND(AVG(TotalDistance), 2) AS Average_Distance
        FROM fitness
        GROUP BY Year, Month
        ORDER BY Year, Month;
    """
}

selected_query = st.selectbox(
    "Select SQL Analysis",
    list(queries.keys())
)

st.code(queries[selected_query], language="sql")

result = sql_query(queries[selected_query])

st.dataframe(result, use_container_width=True)

csv_result = result.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Download SQL Result",
    data=csv_result,
    file_name="sql_analysis_result.csv",
    mime="text/csv"
)

# ---------------- Custom SQL ----------------
st.header("💻 Run Custom SQL")

st.caption(
    "You can query the SQLite table named `fitness`. "
    "Example: SELECT Id, AVG(TotalSteps) FROM fitness GROUP BY Id;"
)

custom_sql = st.text_area(
    "Enter SQL Query",
    value="SELECT * FROM fitness LIMIT 10;",
    height=150
)

if st.button("▶ Run SQL"):
    try:
        custom_result = sql_query(custom_sql)
        st.success("Query executed successfully!")
        st.dataframe(custom_result, use_container_width=True)
    except Exception as e:
        st.error(f"SQL Error: {e}")

# ---------------- Business Insights ----------------
st.header("💡 Business Insights")

overall = sql_query("""
    SELECT
        ROUND(AVG(TotalSteps), 0) AS AvgSteps,
        ROUND(AVG(Calories), 0) AS AvgCalories,
        ROUND(AVG(TotalDistance), 2) AS AvgDistance
    FROM fitness
""").iloc[0]

over10k = sql_query("""
    SELECT COUNT(*) AS Cnt
    FROM fitness
    WHERE TotalSteps >= 10000
""").iloc[0]["Cnt"]

sleep_avg = sql_query("""
    SELECT AVG(TotalMinutesAsleep) AS Sleep
    FROM fitness
    WHERE SleepDataAvailable = 1
""").iloc[0]["Sleep"]

st.markdown(f"""
- Average daily steps in the dataset are approximately **{overall['AvgSteps']:,.0f}**.
- Average calories burned are approximately **{overall['AvgCalories']:,.0f}**.
- Average recorded distance is approximately **{overall['AvgDistance']:.2f}**.
- **{int(over10k):,} records** meet or exceed the 10,000-step threshold.
- Average recorded sleep is approximately **{sleep_avg/60:.1f} hours** where sleep data is available.
- Sedentary time should be monitored alongside steps because high step counts and long sedentary periods can occur in the same record.
""")

st.caption("Fitness Activity SQL Analytics Dashboard")
