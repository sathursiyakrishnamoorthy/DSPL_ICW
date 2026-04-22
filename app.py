"""
Life Expectancy & GDP Dashboard
5DATA004C Individual Coursework - Sathursiya Krishnamoorthy (w2120524)

Implements functional requirements FR-01 through FR-11 and non-functional
requirements NFR-01 through NFR-04 as specified in requirements.md.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

@st.cache_data
def load_data():
    """Load the preprocessed long-format dataset (produced by Phase 2b)."""
    data_path = Path(__file__).parent / "Proccessed" / "life_expectancy_clean.csv"
    df = pd.read_csv(data_path)
    return df


st.set_page_config(
    page_title="Life Expectancy & GDP Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Colourblind-safe palette (NFR-03 - Accessibility)
REGION_COLORS = {
    'East Asia & Pacific':       '#0173B2',
    'Europe & Central Asia':     '#DE8F05',
    'Latin America & Caribbean': '#029E73',
    'Middle East & North Africa':'#CC78BC',
    'North America':             '#CA9161',
    'South Asia':                '#FBAFE4',
    'Sub-Saharan Africa':        '#949494',
}

INCOME_ORDER = ['Low income', 'Lower middle income', 'Upper middle income', 'High income']
INCOME_COLORS = {
    'Low income':          '#CC3311',
    'Lower middle income': '#EE7733',
    'Upper middle income': '#0077BB',
    'High income':         '#009988',
}

df = load_data()

# ======================================================================
# Header
# ======================================================================
st.title("🌍 Global Life Expectancy & GDP Dashboard")
st.caption(
    "Exploring how economic prosperity and regional context shape life expectancy "
    "across 215 countries (2013–2023). Data source: World Bank Open Data."
)


st.sidebar.header("Dashboard Filters")
st.sidebar.caption("Adjust filters to explore the data. All charts update automatically.")

regions = st.sidebar.multiselect(
    "Regions",
    options=sorted(df['Region'].unique()),
    default=sorted(df['Region'].unique()),
    help="Filter countries by World Bank region."
)

income_groups = st.sidebar.multiselect(
    "Income Groups",
    options=[g for g in INCOME_ORDER if g in df['IncomeGroup'].unique()],
    default=[g for g in INCOME_ORDER if g in df['IncomeGroup'].unique()],
    help="Filter countries by World Bank income classification."
)

year_min, year_max = int(df['Year'].min()), int(df['Year'].max())
year_range = st.sidebar.slider(
    "Year range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
    help="Select the years included in the analysis."
)

st.sidebar.divider()
st.sidebar.caption(
    f"**Dataset:** {len(df):,} country-year rows  \n"
    f"**Countries:** {df['Country Name'].nunique()}  \n"
    f"**Years:** {year_min}–{year_max}"
)


filtered_df = df[
    (df['Region'].isin(regions)) &
    (df['IncomeGroup'].isin(income_groups)) &
    (df['Year'].between(year_range[0], year_range[1]))
]

if filtered_df.empty:
    st.warning("No data matches the current filters. Please broaden your selection.")
    st.stop()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Avg Life Expectancy", f"{filtered_df['Life Expectancy'].mean():.1f} yrs")
k2.metric("Avg GDP per Capita", f"${filtered_df['GDP per Capita'].mean():,.0f}")
k3.metric("Countries", filtered_df['Country Name'].nunique())
k4.metric("Years Selected", year_range[1] - year_range[0] + 1)

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Trends", "💰 GDP vs Life Expectancy", "🗺 Global Map", "🏆 Rankings"
])

with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Life Expectancy by Region")
        region_avg = (
            filtered_df.groupby(['Year', 'Region'])['Life Expectancy']
            .mean().reset_index()
        )
        fig_region = px.line(
            region_avg, x='Year', y='Life Expectancy', color='Region',
            markers=True, color_discrete_map=REGION_COLORS,
            labels={'Life Expectancy': 'Life Expectancy (years)'}
        )
        fig_region.update_layout(hovermode='x unified', height=450)
        st.plotly_chart(fig_region, use_container_width=True)

    with c2:
        st.subheader("Life Expectancy by Income Group")
        income_avg = (
            filtered_df.groupby(['Year', 'IncomeGroup'])['Life Expectancy']
            .mean().reset_index()
        )
        fig_income = px.line(
            income_avg, x='Year', y='Life Expectancy', color='IncomeGroup',
            markers=True, color_discrete_map=INCOME_COLORS,
            category_orders={'IncomeGroup': INCOME_ORDER},
            labels={'Life Expectancy': 'Life Expectancy (years)'}
        )
        fig_income.update_layout(hovermode='x unified', height=450)
        st.plotly_chart(fig_income, use_container_width=True)

    st.info(
        "💡 **Insight:** The gap between High-income and Low-income countries "
        "has been narrowing over the decade — but substantial inequality remains."
    )


with tab2:
    st.subheader("GDP per Capita vs Life Expectancy")

    selected_year = st.slider(
        "Select year to display",
        min_value=year_range[0], max_value=year_range[1],
        value=year_range[1], key="scatter_year"
    )

    scatter_df = filtered_df[filtered_df['Year'] == selected_year]
    fig_scatter = px.scatter(
        scatter_df,
        x='GDP per Capita', y='Life Expectancy',
        color='Region', size='GDP per Capita', hover_name='Country Name',
        log_x=True, color_discrete_map=REGION_COLORS,
        labels={
            'GDP per Capita': 'GDP per Capita (USD, log scale)',
            'Life Expectancy': 'Life Expectancy (years)'
        },
        title=f"GDP per Capita vs Life Expectancy ({selected_year})"
    )
    fig_scatter.update_layout(height=600)
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.info(
        "💡 **Insight:** The relationship follows a diminishing-returns curve. "
        "Below ~$10,000 GDP per capita, small economic gains bring large "
        "life-expectancy improvements. Above ~$40,000 the curve flattens — "
        "wealth stops being the primary driver of longevity."
    )


with tab3:
    st.subheader("Global Life Expectancy Map")

    map_year = st.slider(
        "Select year",
        min_value=year_range[0], max_value=year_range[1],
        value=year_range[1], key="map_year"
    )

    map_df = filtered_df[filtered_df['Year'] == map_year]
    fig_map = px.choropleth(
        map_df,
        locations='Country Code',
        color='Life Expectancy',
        hover_name='Country Name',
        hover_data={'Country Code': False, 'Life Expectancy': ':.1f',
                    'GDP per Capita': ':,.0f'},
        color_continuous_scale='Viridis',
        labels={'Life Expectancy': 'Life Expectancy (years)'}
    )
    fig_map.update_layout(height=600, margin={'l': 0, 'r': 0, 't': 30, 'b': 0})
    st.plotly_chart(fig_map, use_container_width=True)


with tab4:
    st.subheader("Top 10 and Bottom 10 Countries by Life Expectancy")

    rank_year = st.slider(
        "Select year",
        min_value=year_range[0], max_value=year_range[1],
        value=year_range[1], key="rank_year"
    )

    year_df = filtered_df[filtered_df['Year'] == rank_year].sort_values(
        'Life Expectancy', ascending=False
    )
    top10 = year_df.head(10).copy()
    top10['Group'] = 'Top 10'
    bottom10 = year_df.tail(10).copy()
    bottom10['Group'] = 'Bottom 10'
    ranking = pd.concat([top10, bottom10])

    fig_rank = px.bar(
        ranking,
        x='Life Expectancy', y='Country Name',
        color='Region', orientation='h',
        color_discrete_map=REGION_COLORS,
        labels={'Life Expectancy': 'Life Expectancy (years)', 'Country Name': ''},
        title=f"Life Expectancy Rankings ({rank_year})",
        facet_col='Group', category_orders={'Group': ['Top 10', 'Bottom 10']}
    )
    fig_rank.update_yaxes(matches=None)
    fig_rank.update_layout(height=600)
    st.plotly_chart(fig_rank, use_container_width=True)


st.divider()
with st.expander("📋 View filtered data table"):
    st.write(f"Displaying **{len(filtered_df):,}** rows matching the current filters.")
    st.dataframe(
        filtered_df[['Country Name', 'Region', 'IncomeGroup', 'Year',
                     'Life Expectancy', 'GDP per Capita']],
        use_container_width=True, hide_index=True
    )

