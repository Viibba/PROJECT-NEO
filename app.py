import streamlit as st
st.title("PROJECT NEO")
def style_dataframe(df):
    return (
        df.style
        .set_table_styles([
            {'selector': 'thead th',
             'props': [('background-color', '#0b3d91'), ('color', 'white'), ('font-weight', 'bold'), ('text-align', 'center')]},
            {'selector': 'tbody td',
             'props': [('text-align', 'center')]},
            {'selector': 'tbody tr:nth-child(even)',
             'props': [('background-color', '#f2f2f2')]},
            {'selector': 'tbody tr:nth-child(odd)',
             'props': [('background-color', 'white')]},
        ])
        .set_properties(**{'border': '1px solid #ccc', 'padding': '6px'})
    )
# asteroid_dashboard.py
import streamlit as st
import pandas as pd
import pymysql

# -----------------------
# DATABASE CONNECTION
# -----------------------
def get_connection():
    return pymysql.connect(
        host="localhost",
    user="root",
    password="Vikram@3ms",
    db="asteroids",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
    )

# -----------------------
# RUN SQL QUERY
# -----------------------
def run_query(query, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    finally:
        conn.close()

# -----------------------
# PREDEFINED QUERIES
# -----------------------
predefined_queries = {
    "All Asteroids": "SELECT * FROM asteroids LIMIT 50;",
    "Potentially Hazardous": "SELECT * FROM asteroids WHERE is_potentially_hazardous_asteroid = 1;",
    "Largest Diameter": "SELECT * FROM asteroids ORDER BY estimated_diameter_max_km DESC LIMIT 10;",
    "Smallest Diameter": "SELECT * FROM asteroids ORDER BY estimated_diameter_min_km ASC LIMIT 10;",
    "Fastest Relative Velocity": """
        SELECT a.name, c.relative_velocity_kmph
        FROM close_approach c
        JOIN asteroids a ON a.id = c.neo_reference_id
        ORDER BY c.relative_velocity_kmph DESC LIMIT 10;
    """,
    # Add more queries here up to 15
}

# -----------------------
# STREAMLIT UI
# -----------------------
st.set_page_config(page_title="🚀 Asteroid Data Explorer", layout="wide")
st.title("🚀 Asteroid Data Explorer")
st.markdown("Explore asteroid close-approach data from NASA's NEO API with dynamic SQL queries.")

# Sidebar: Query selection
st.sidebar.header("🔍 Select a Predefined Query")
query_choice = st.sidebar.selectbox("Choose Query", list(predefined_queries.keys()))
if st.sidebar.button("Run Query"):
    data = run_query(predefined_queries[query_choice])
    st.dataframe(pd.DataFrame(data), use_container_width=True)

st.sidebar.markdown("---")

# -----------------------
# FILTER SECTION
# -----------------------
st.sidebar.header("🎯 Apply Filters")

# Date filter
date_filter = st.sidebar.date_input("Close Approach Date")

# Astronomical Units
au_min, au_max = st.sidebar.slider("Astronomical Units (AU)", 0.0, 5.0, (0.0, 5.0), 0.01)

# Lunar Distances
lunar_min, lunar_max = st.sidebar.slider("Lunar Distances", 0.0, 50.0, (0.0, 50.0), 0.5)

# Relative Velocity
vel_min, vel_max = st.sidebar.slider("Relative Velocity (km/h)", 0.0, 150000.0, (0.0, 150000.0), 100.0)

# Estimated Diameter
diam_min, diam_max = st.sidebar.slider("Estimated Diameter (km)", 0.0, 50.0, (0.0, 50.0), 0.1)

# Hazardous state
hazardous = st.sidebar.selectbox("Potentially Hazardous?", ["All", "Yes", "No"])

# -----------------------
# SQL WITH FILTERS
# -----------------------
query = """
SELECT a.id, a.name, a.estimated_diameter_min_km, a.estimated_diameter_max_km,
       a.is_potentially_hazardous_asteroid, c.close_approach_date,
       c.relative_velocity_kmph, c.astronomical, c.miss_distance_lunar
FROM asteroids a
JOIN close_approach c ON a.id = c.neo_reference_id
WHERE c.close_approach_date = %s
AND c.astronomical BETWEEN %s AND %s
AND c.miss_distance_lunar BETWEEN %s AND %s
AND c.relative_velocity_kmph BETWEEN %s AND %s
AND a.estimated_diameter_min_km >= %s
AND a.estimated_diameter_max_km <= %s
"""

params = [
    date_filter,
    au_min, au_max,
    lunar_min, lunar_max,
    vel_min, vel_max,
    diam_min, diam_max
]

if hazardous == "Yes":
    query += " AND a.is_potentially_hazardous_asteroid = 1"
elif hazardous == "No":
    query += " AND a.is_potentially_hazardous_asteroid = 0"

if st.sidebar.button("Apply Filters"):
    filtered_data = run_query(query, params)
    st.subheader("📊 Filtered Results")
    st.dataframe(
        pd.DataFrame(filtered_data),
        use_container_width=True
    )

# -----------------------
# STYLING
# -----------------------
st.markdown("""
    <style>
    .stDataFrame { font-size: 14px; }
    </style>
""", unsafe_allow_html=True)
