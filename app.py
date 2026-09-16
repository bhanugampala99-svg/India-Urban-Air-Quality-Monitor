import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="India Urban Air Quality Monitor",
    page_icon="🌿",
    layout="wide"
)

DATA = [
    ["2025-01-05", "Bengaluru", "Karnataka", 92, 48, 82, 31, 10, 0.8, 24],
    ["2025-01-18", "Bengaluru", "Karnataka", 118, 64, 104, 38, 12, 1.0, 28],
    ["2025-02-10", "Bengaluru", "Karnataka", 85, 43, 76, 28, 9, 0.7, 22],
    ["2025-03-08", "Bengaluru", "Karnataka", 104, 57, 95, 34, 11, 0.9, 26],
    ["2025-01-06", "Hyderabad", "Telangana", 112, 60, 98, 42, 13, 1.1, 30],
    ["2025-01-22", "Hyderabad", "Telangana", 136, 75, 121, 49, 15, 1.3, 34],
    ["2025-02-12", "Hyderabad", "Telangana", 101, 54, 90, 37, 12, 0.9, 27],
    ["2025-03-11", "Hyderabad", "Telangana", 126, 68, 112, 45, 14, 1.2, 32],
    ["2025-01-07", "Delhi", "Delhi", 268, 162, 248, 84, 25, 2.1, 46],
    ["2025-01-25", "Delhi", "Delhi", 312, 188, 286, 96, 28, 2.5, 51],
    ["2025-02-14", "Delhi", "Delhi", 224, 130, 210, 72, 22, 1.8, 40],
    ["2025-03-14", "Delhi", "Delhi", 191, 108, 176, 62, 19, 1.5, 35],
    ["2025-01-09", "Mumbai", "Maharashtra", 142, 78, 126, 48, 16, 1.2, 33],
    ["2025-01-28", "Mumbai", "Maharashtra", 165, 92, 148, 55, 18, 1.5, 37],
    ["2025-02-16", "Mumbai", "Maharashtra", 124, 67, 112, 43, 14, 1.0, 29],
    ["2025-03-16", "Mumbai", "Maharashtra", 138, 74, 123, 47, 15, 1.1, 31],
    ["2025-01-10", "Chennai", "Tamil Nadu", 88, 46, 79, 30, 10, 0.8, 23],
    ["2025-01-30", "Chennai", "Tamil Nadu", 107, 58, 96, 37, 12, 1.0, 27],
    ["2025-02-18", "Chennai", "Tamil Nadu", 82, 42, 73, 27, 9, 0.7, 21],
    ["2025-03-18", "Chennai", "Tamil Nadu", 96, 51, 86, 33, 11, 0.9, 25],
    ["2025-01-12", "Pune", "Maharashtra", 116, 63, 101, 41, 13, 1.0, 28],
    ["2025-01-31", "Pune", "Maharashtra", 134, 72, 118, 46, 14, 1.2, 31],
    ["2025-02-20", "Pune", "Maharashtra", 103, 55, 91, 36, 11, 0.9, 25],
    ["2025-03-20", "Pune", "Maharashtra", 121, 65, 107, 42, 13, 1.0, 29],
]

COLUMNS = [
    "date", "city", "state", "aqi", "pm25", "pm10",
    "no2", "so2", "co", "o3"
]

df = pd.DataFrame(DATA, columns=COLUMNS)
df["date"] = pd.to_datetime(df["date"])
df["month"] = df["date"].dt.strftime("%b %Y")

def get_aqi_category(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    return "Severe"

df["aqi_category"] = df["aqi"].apply(get_aqi_category)

st.title("🌿 India Urban Air Quality Monitor")
st.caption(
    "Interactive dashboard for analyzing AQI patterns, city-level pollution risk, "
    "and pollutant trends across selected Indian cities."
)

st.sidebar.header("Dashboard Filters")

selected_cities = st.sidebar.multiselect(
    "Select City",
    options=sorted(df["city"].unique()),
    default=sorted(df["city"].unique())
)

selected_categories = st.sidebar.multiselect(
    "Select AQI Category",
    options=sorted(df["aqi_category"].unique()),
    default=sorted(df["aqi_category"].unique())
)

filtered_df = df[
    (df["city"].isin(selected_cities)) &
    (df["aqi_category"].isin(selected_categories))
].copy()

if filtered_df.empty:
    st.warning("No records match the selected filters. Please choose another option.")
    st.stop()

avg_aqi = filtered_df["aqi"].mean()
max_aqi = filtered_df["aqi"].max()
high_risk_days = (filtered_df["aqi"] > 200).sum()
cities_covered = filtered_df["city"].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Average AQI", f"{avg_aqi:.0f}")
col2.metric("Maximum AQI", f"{max_aqi:.0f}")
col3.metric("High-Risk Days", high_risk_days)
col4.metric("Cities Analyzed", cities_covered)

st.divider()

left, right = st.columns(2)

with left:
    city_avg = (
        filtered_df.groupby("city", as_index=False)["aqi"]
        .mean()
        .sort_values("aqi", ascending=False)
    )
    fig_city = px.bar(
        city_avg,
        x="city",
        y="aqi",
        color="aqi",
        color_continuous_scale="Reds",
        title="Average AQI by City",
        labels={"city": "City", "aqi": "Average AQI"}
    )
    st.plotly_chart(fig_city, use_container_width=True)

with right:
    monthly_city = (
        filtered_df.groupby(["month", "city"], as_index=False)["aqi"]
        .mean()
    )
    month_order = ["Jan 2025", "Feb 2025", "Mar 2025"]
    monthly_city["month"] = pd.Categorical(
        monthly_city["month"],
        categories=month_order,
        ordered=True
    )
    monthly_city = monthly_city.sort_values("month")

    fig_trend = px.line(
        monthly_city,
        x="month",
        y="aqi",
        color="city",
        markers=True,
        title="Monthly AQI Trend by City",
        labels={"month": "Month", "aqi": "Average AQI", "city": "City"}
    )
    st.plotly_chart(fig_trend, use_container_width=True)

left, right = st.columns(2)

with left:
    category_count = (
        filtered_df["aqi_category"]
        .value_counts()
        .reset_index()
    )
    category_count.columns = ["AQI Category", "Days"]

    fig_category = px.pie(
        category_count,
        names="AQI Category",
        values="Days",
        hole=0.45,
        title="AQI Category Distribution",
        color="AQI Category",
        color_discrete_map={
            "Good": "#2E8B57",
            "Satisfactory": "#7CB342",
            "Moderate": "#F9A825",
            "Poor": "#FB8C00",
            "Very Poor": "#E53935",
            "Severe": "#6A1B9A"
        }
    )
    st.plotly_chart(fig_category, use_container_width=True)

with right:
    fig_scatter = px.scatter(
        filtered_df,
        x="pm25",
        y="aqi",
        color="city",
        size="pm10",
        hover_data=["date", "no2", "so2", "co", "o3", "aqi_category"],
        title="PM2.5 vs AQI Relationship",
        labels={"pm25": "PM2.5", "aqi": "AQI", "pm10": "PM10"}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

st.subheader("Pollutant Profile by City")

pollutant_columns = ["pm25", "pm10", "no2", "so2", "co", "o3"]
pollutant_avg = (
    filtered_df.groupby("city")[pollutant_columns]
    .mean()
    .reset_index()
    .melt(id_vars="city", var_name="Pollutant", value_name="Average Level")
)

fig_pollutants = px.bar(
    pollutant_avg,
    x="city",
    y="Average Level",
    color="Pollutant",
    barmode="group",
    title="Average Pollutant Levels by City"
)
st.plotly_chart(fig_pollutants, use_container_width=True)

st.subheader("Risk Monitoring Table")

risk_table = filtered_df[
    ["date", "city", "state", "aqi", "aqi_category", "pm25", "pm10", "no2", "so2", "co", "o3"]
].sort_values(["aqi", "date"], ascending=[False, False])

st.dataframe(risk_table, use_container_width=True, hide_index=True)

st.subheader("Key Takeaways")

highest_city = city_avg.iloc[0]["city"]
highest_city_aqi = city_avg.iloc[0]["aqi"]

st.info(
    f"**{highest_city}** has the highest average AQI in the selected data "
    f"({highest_city_aqi:.0f}). AQI levels above 200 are marked as high-risk "
    f"for monitoring purposes. Use the sidebar filters to compare cities and AQI categories."
)

st.caption(
    "Portfolio project using a compact demonstration dataset. "
    "AQI categories follow commonly used India AQI threshold ranges. "
    "For public-health decisions, consult official CPCB monitoring sources."
)
