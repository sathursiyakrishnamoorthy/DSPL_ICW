import streamlit as st
import pandas as pd
import plotly.express as px

# 1. PAGE CONFIG (From your Tutorial Page 6)
st.set_page_config(page_title="Life Expectancy Dashboard", layout="wide")

# 2. DATA LOADING (Data Understanding & Preparation)
@st.cache_data
def load_data():
    # Load main data (skip 3 lines of junk)
    # We use a relative path because the file is in the same folder
    df_life = pd.read_csv('C:\\Users\\User\\Desktop\\data science\\Individual\\DSPL_ICW\\Life_expectancy.csv', skiprows=3)
    
    # Load metadata (NO skiprows here, use encoding fix)
    df_meta = pd.read_csv('C:\\Users\\User\\Desktop\\data science\\Individual\\DSPL_ICW\\metadata_countries.csv')
    
    # MERGE: Add Region and IncomeGroup to our data
    df_combined = pd.merge(df_life, df_meta[['Country Code', 'Region', 'IncomeGroup']], on='Country Code')
    
    # MELT: Turn year columns into a single 'Year' column (Data Transformation)
    id_vars = ['Country Name', 'Country Code', 'Region', 'IncomeGroup']
    df_long = df_combined.melt(id_vars=id_vars, var_name='Year', value_name='Life Expectancy')
    
    # Clean data types
    df_long['Year'] = pd.to_numeric(df_long['Year'], errors='coerce')
    df_long = df_long.dropna(subset=['Life Expectancy', 'Year'])
    return df_long

# Load the data
df = load_data()

# 3. SIDEBAR (From your Tutorial Page 10)
st.sidebar.header("Dashboard Filters")
regions = st.sidebar.multiselect("Select Regions", options=df['Region'].unique(), default=df['Region'].unique())
year_range = st.sidebar.slider("Select Year Range", int(df['Year'].min()), int(df['Year'].max()), (2000, 2023))

# Filter data
filtered_df = df[(df['Region'].isin(regions)) & (df['Year'].between(year_range[0], year_range[1]))]

# 4. VISUALIZATION (From your Tutorial Page 15)
st.title("🌍 Global Life Expectancy Dashboard")

# Show metrics
c1, c2 = st.columns(2)
c1.metric("Average Life Expectancy", f"{filtered_df['Life Expectancy'].mean():.1f} Years")
c2.metric("Countries Count", filtered_df['Country Name'].nunique())

# Line Chart
fig = px.line(filtered_df, x='Year', y='Life Expectancy', color='Region', 
              line_group='Country Name', hover_name='Country Name',
              title="Life Expectancy Trends")
st.plotly_chart(fig, use_container_width=True)

# 5. DATA TABLE (Requirement: Show 100+ rows)
with st.expander("View Filtered Data Table"):
    st.write(f"Displaying {len(filtered_df)} rows")
    st.dataframe(filtered_df)