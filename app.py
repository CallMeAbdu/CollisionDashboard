import streamlit as st
import pandas as pd
import pydeck as pdk

# -------------------------------------------------
# Load cleaned dataset
# -------------------------------------------------
df = pd.read_csv("collisions_cleaned_streamlit.csv")

st.set_page_config(page_title="Collision Dashboard",
                   layout="wide")

st.title("Montreal Crash Severity Analysis Dashboard")

# -------------------------------------------------
# Sidebar Filters
# -------------------------------------------------

st.sidebar.header("Filters")

# Correct weekday order
weekday_order = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday"
]
available_days = [d for d in weekday_order if d in df["accident_day_of_week"].unique()]

year_filter = st.sidebar.selectbox(
    "Year",
    ["All"] + sorted(df["year"].dropna().unique().tolist())
)

month_filter = st.sidebar.selectbox(
    "Month",
    ["All"] + sorted(df["month"].dropna().unique().tolist())
)

hour_filter = st.sidebar.selectbox(
    "Hour",
    ["All"] + sorted(df["hour"].dropna().unique().tolist())
)

day_filter = st.sidebar.selectbox(
    "Day of Week",
    ["All"] + available_days
)

weather_filter = st.sidebar.selectbox(
    "Weather",
    ["All"] + sorted(df["weather_group"].dropna().unique().tolist())
)

lighting_filter = st.sidebar.selectbox(
    "Lighting",
    ["All"] + sorted(df["lighting_group"].dropna().unique().tolist())
)

surface_filter = st.sidebar.selectbox(
    "Road Surface",
    ["All"] + sorted(df["road_surface_group"].dropna().unique().tolist())
)

severity_filter = st.sidebar.selectbox(
    "Injury Severity (Binary)",
    ["All", "Yes", "No"]
)

# -------------------------------------------------
# Apply filters
# -------------------------------------------------
filtered = df.copy()

if year_filter != "All":
    filtered = filtered[filtered["year"] == year_filter]

if month_filter != "All":
    filtered = filtered[filtered["month"] == month_filter]

if hour_filter != "All":
    filtered = filtered[filtered["hour"] == hour_filter]

if day_filter != "All":
    filtered = filtered[filtered["accident_day_of_week"] == day_filter]

if weather_filter != "All":
    filtered = filtered[filtered["weather_group"] == weather_filter]

if lighting_filter != "All":
    filtered = filtered[filtered["lighting_group"] == lighting_filter]

if surface_filter != "All":
    filtered = filtered[filtered["road_surface_group"] == surface_filter]

if severity_filter != "All":
    filtered = filtered[filtered["accident_severity"] == severity_filter]

# -------------------------------------------------
# Key Metrics
# -------------------------------------------------
st.subheader("Key Metrics")
col1, col2 = st.columns(2)

col1.metric("Total Collisions", len(filtered))
col2.metric("Injury Collisions", (filtered["accident_severity"] == "Yes").sum())

# -------------------------------------------------
# Tabs: Map / Distributions / Statistics
# -------------------------------------------------
tab1, tab2= st.tabs(["Map", "Distributions"])

# -------------------------------------------------
# TAB 1: MAP
# -------------------------------------------------
with tab1:
    st.subheader("Collision Map")

    if len(filtered) == 0:
        st.warning("No data for the selected filters.")
    else:
        filtered["color"] = filtered["accident_severity"].map(
            {"Yes": [255, 0, 0], "No": [0, 100, 255]}
        )

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered,
            get_position=["longitude", "latitude"],
            get_color="color",
            get_radius=40,
            pickable=True,
        )

        view_state = pdk.ViewState(
            latitude=filtered["latitude"].mean(),
            longitude=filtered["longitude"].mean(),
            zoom=10,
            pitch=0,
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            height=900,      # large height
            width="50%",    # takes full width
        )

        st.pydeck_chart(deck)


# -------------------------------------------------
# TAB 2: DISTRIBUTIONS
# -------------------------------------------------
with tab2:
    st.subheader("Distribution of Categories")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.write("### Road Surface Conditions")
        st.bar_chart(filtered["road_surface_group"].value_counts())

    with c2:
        st.write("### Lighting Conditions")
        st.bar_chart(filtered["lighting_group"].value_counts())

    with c3:
        st.write("### Weather Conditions")
        st.bar_chart(filtered["weather_group"].value_counts())

    st.write("---")
    st.write("### Injury vs No Injury")
    st.bar_chart(filtered["accident_severity"].value_counts())
