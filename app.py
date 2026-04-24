"""
Life Expectancy & GDP Dashboard
Author:  Sathursiya Krishnamoorthy | w2120524 | 20241113

This dashboard visualises the relationship between life expectancy and
GDP per capita across 215 countries (2013-2023), using World Bank data.

Traceability: implements functional requirements FR-01 to FR-11 and
non-functional requirements NFR-01 to NFR-04 as documented in
requirements.md at the repository root.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# Configuration

DATA_PATH = Path(__file__).parent / "Proccessed" / "life_expectancy_clean.csv"

# Order matters for the income-group legend (poorest to richest).
INCOME_ORDER = [
    "Low income",
    "Lower middle income",
    "Upper middle income",
    "High income",
]

# Colourblind-safe palette. Region colours deliberately cover warm and
# cool hues so that no two adjacent regions are hard to distinguish.
REGION_COLORS = {
    "East Asia & Pacific":        "#00847A",
    "Europe & Central Asia":      "#F39C12",
    "Latin America & Caribbean":  "#E74C3C",
    "Middle East & North Africa": "#8E44AD",
    "North America":              "#2980B9",
    "South Asia":                 "#D35400",
    "Sub-Saharan Africa":         "#27AE60",
}

INCOME_COLORS = {
    "Low income":          "#E74C3C",
    "Lower middle income": "#F39C12",
    "Upper middle income": "#2980B9",
    "High income":         "#00847A",
}

# Shared Plotly layout so every chart looks consistent.
CHART_LAYOUT = dict(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(family="sans-serif", size=12, color="#1A2B3C"),
    xaxis=dict(gridcolor="#EDF0F3"),
    yaxis=dict(gridcolor="#EDF0F3"),
    margin=dict(l=20, r=20, t=40, b=20),
)


# Data loading (FR-01)

@st.cache_data
def load_data() -> pd.DataFrame:
    """Load the preprocessed long-format dataset produced by Phase 2b."""
    return pd.read_csv(DATA_PATH)


# Helpers

def apply_filters(data, regions, income_groups, year_range):
    """Return rows matching the sidebar filters."""
    mask = (
        data["Region"].isin(regions)
        & data["IncomeGroup"].isin(income_groups)
        & data["Year"].between(year_range[0], year_range[1])
    )
    return data.loc[mask]


def mean_delta(data, column, year_range):
    """Change in the column's mean between the first and last year."""
    if year_range[0] == year_range[1]:
        return None
    first = data.loc[data["Year"] == year_range[0], column].mean()
    last = data.loc[data["Year"] == year_range[1], column].mean()
    return last - first


def largest_regional_gain(data):
    """Return (region_name, years_gained) with the biggest change."""
    by_region = data.groupby("Region")["Life Expectancy"].agg(["first", "last"])
    by_region["delta"] = by_region["last"] - by_region["first"]
    by_region = by_region.sort_values("delta", ascending=False)
    return by_region.index[0], by_region.iloc[0]["delta"]


def log_correlation(data):
    """Pearson correlation between log(GDP) and life expectancy."""
    if len(data) < 3:
        return 0.0
    log_gdp = np.log10(data["GDP per Capita"])
    return float(np.corrcoef(log_gdp, data["Life Expectancy"])[0, 1])


# Page setup

st.set_page_config(
    page_title="Life Expectancy & GDP Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

df = load_data()


# Header

title_col, badge_col = st.columns([4, 1])
with title_col:
    st.title("Life Expectancy & GDP Dashboard")
    st.caption(
        "An analytical view of how economic output correlates with longevity "
        "across 215 economies, 2013–2023."
    )
with badge_col:
    st.markdown(
        "<div style='text-align:right; color:#5A6B7D; padding-top:18px;'>"
        "<strong style='color:#00847A;'>2013 – 2023</strong><br>"
        "<span style='font-size:0.85rem;'>World Bank Open Data</span>"
        "</div>",
        unsafe_allow_html=True,
    )

st.divider()


# Sidebar filters (FR-02, FR-03, FR-04)

st.sidebar.header("Filters")
st.sidebar.caption("All views update automatically when filters change.")

selected_regions = st.sidebar.multiselect(
    "Regions",
    options=sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique()),
)

available_incomes = [g for g in INCOME_ORDER if g in df["IncomeGroup"].unique()]
selected_incomes = st.sidebar.multiselect(
    "Income Groups",
    options=available_incomes,
    default=available_incomes,
)

year_min = int(df["Year"].min())
year_max = int(df["Year"].max())
selected_years = st.sidebar.slider(
    "Year Range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
)

filtered = apply_filters(df, selected_regions, selected_incomes, selected_years)

if filtered.empty:
    st.warning("No data matches the current filters. Please broaden your selection.")
    st.stop()

st.sidebar.divider()
st.sidebar.subheader("Current selection")
st.sidebar.markdown(
    f"""
    - **Rows:** {len(filtered):,}
    - **Countries:** {filtered['Country Name'].nunique()}
    - **Regions:** {filtered['Region'].nunique()}
    - **Years:** {selected_years[1] - selected_years[0] + 1}
    """
)

# FR-11 enhancement: allow users to download the filtered view
st.sidebar.download_button(
    label="Download filtered data (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name=f"life_exp_filtered_{selected_years[0]}-{selected_years[1]}.csv",
    mime="text/csv",
)


# KPI metrics (FR-05)

life_change = mean_delta(filtered, "Life Expectancy", selected_years)
gdp_change = mean_delta(filtered, "GDP per Capita", selected_years)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(
    "Avg Life Expectancy",
    f"{filtered['Life Expectancy'].mean():.1f} yrs",
    delta=f"{life_change:+.1f} yrs" if life_change is not None else None,
    help=f"Change from {selected_years[0]} to {selected_years[1]}",
)
kpi2.metric(
    "Avg GDP per Capita",
    f"${filtered['GDP per Capita'].mean():,.0f}",
    delta=f"${gdp_change:+,.0f}" if gdp_change is not None else None,
)
kpi3.metric("Countries", filtered["Country Name"].nunique())
kpi4.metric("Years in View", selected_years[1] - selected_years[0] + 1)

st.write("")


# Tab layout

trends_tab, relationship_tab, timeline_tab, map_tab, compare_tab = st.tabs(
    ["Trends", "GDP vs Life", "Animated Timeline", "Global Map", "Compare Countries"]
)


# Tab 1: Trends (FR-06, FR-07)

with trends_tab:
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Life Expectancy by Region")
        region_avg = (
            filtered.groupby(["Year", "Region"])["Life Expectancy"]
            .mean()
            .reset_index()
        )
        fig = px.line(
            region_avg,
            x="Year",
            y="Life Expectancy",
            color="Region",
            markers=True,
            color_discrete_map=REGION_COLORS,
        )
        fig.update_layout(**CHART_LAYOUT, hovermode="x unified", height=420,
                          yaxis_title="Life Expectancy (years)")
        fig.update_traces(line_width=2.5)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Life Expectancy by Income Group")
        income_avg = (
            filtered.groupby(["Year", "IncomeGroup"])["Life Expectancy"]
            .mean()
            .reset_index()
        )
        fig = px.line(
            income_avg,
            x="Year",
            y="Life Expectancy",
            color="IncomeGroup",
            markers=True,
            color_discrete_map=INCOME_COLORS,
            category_orders={"IncomeGroup": INCOME_ORDER},
        )
        fig.update_layout(**CHART_LAYOUT, hovermode="x unified", height=420,
                          yaxis_title="Life Expectancy (years)")
        fig.update_traces(line_width=2.5)
        st.plotly_chart(fig, use_container_width=True)

    # Key figures row
    top_region, top_gain = largest_regional_gain(filtered)
    high_income_avg = (
        filtered.loc[filtered["IncomeGroup"] == "High income", "Life Expectancy"]
        .mean()
    )
    low_income_avg = (
        filtered.loc[filtered["IncomeGroup"] == "Low income", "Life Expectancy"]
        .mean()
    )
    income_gap = (high_income_avg - low_income_avg
                  if pd.notna(high_income_avg) and pd.notna(low_income_avg)
                  else None)

    f1, f2, f3 = st.columns(3)
    f1.metric("Regional gain leader", top_region, f"{top_gain:+.1f} yrs")
    f2.metric(
        "High-income average",
        f"{high_income_avg:.1f} yrs" if pd.notna(high_income_avg) else "—",
    )
    f3.metric(
        "High–Low income gap",
        f"{income_gap:.1f} yrs" if income_gap is not None else "—",
    )


# Tab 2: GDP vs Life relationship (FR-08)

with relationship_tab:
    st.subheader("GDP per Capita vs Life Expectancy")

    scatter_year = st.slider(
        "Select year",
        min_value=selected_years[0],
        max_value=selected_years[1],
        value=selected_years[1],
        key="scatter_year",
    )
    scatter_data = filtered[filtered["Year"] == scatter_year]
    correlation = log_correlation(scatter_data)

    fig = px.scatter(
        scatter_data,
        x="GDP per Capita",
        y="Life Expectancy",
        color="Region",
        size="GDP per Capita",
        hover_name="Country Name",
        log_x=True,
        color_discrete_map=REGION_COLORS,
        trendline="ols",
        trendline_scope="overall",
        trendline_color_override="#1A2B3C",
        labels={
            "GDP per Capita": "GDP per Capita (USD, log scale)",
            "Life Expectancy": "Life Expectancy (years)",
        },
    )
    fig.update_layout(**CHART_LAYOUT, height=560)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("##### Correlation analysis")
    stat1, stat2, stat3 = st.columns(3)
    stat1.metric("Pearson r  (log GDP, life exp)", f"{correlation:.3f}")
    stat2.metric(
        "Highest life expectancy",
        scatter_data.loc[scatter_data["Life Expectancy"].idxmax(), "Country Name"],
        f"{scatter_data['Life Expectancy'].max():.1f} yrs",
    )
    stat3.metric(
        "Lowest life expectancy",
        scatter_data.loc[scatter_data["Life Expectancy"].idxmin(), "Country Name"],
        f"{scatter_data['Life Expectancy'].min():.1f} yrs",
    )

    st.caption(
        "Pearson correlation computed on log-transformed GDP. Trendline shown is "
        "ordinary least squares (OLS) across all visible countries."
    )


# Tab 3: Animated timeline

with timeline_tab:
    st.subheader("Trajectories over time — GDP per Capita vs Life Expectancy")
    st.caption(
        "Press play to advance through years. Use this view to identify "
        "acceleration, stagnation, or regression in specific economies."
    )

    fig = px.scatter(
        filtered,
        x="GDP per Capita",
        y="Life Expectancy",
        animation_frame="Year",
        animation_group="Country Name",
        size="GDP per Capita",
        color="Region",
        hover_name="Country Name",
        log_x=True,
        size_max=60,
        color_discrete_map=REGION_COLORS,
        range_x=[filtered["GDP per Capita"].min() * 0.8,
                 filtered["GDP per Capita"].max() * 1.2],
        range_y=[filtered["Life Expectancy"].min() - 2,
                 filtered["Life Expectancy"].max() + 2],
        labels={
            "GDP per Capita": "GDP per Capita (USD, log scale)",
            "Life Expectancy": "Life Expectancy (years)",
        },
    )
    fig.update_layout(**CHART_LAYOUT, height=620,
                      transition={"duration": 300, "easing": "cubic-in-out"})
    st.plotly_chart(fig, use_container_width=True)


# Tab 4: Global map (FR-09)

with map_tab:
    st.subheader("Global distribution of life expectancy")

    map_year = st.slider(
        "Select year",
        min_value=selected_years[0],
        max_value=selected_years[1],
        value=selected_years[1],
        key="map_year",
    )
    map_data = filtered[filtered["Year"] == map_year]

    fig = px.choropleth(
        map_data,
        locations="Country Code",
        color="Life Expectancy",
        hover_name="Country Name",
        hover_data={"Country Code": False,
                    "Life Expectancy": ":.1f",
                    "GDP per Capita": ":,.0f"},
        color_continuous_scale=[[0, "#E74C3C"], [0.5, "#F39C12"], [1, "#00847A"]],
        labels={"Life Expectancy": "Years"},
    )
    fig.update_geos(
        bgcolor="#FFFFFF",
        showcoastlines=True,
        coastlinecolor="#C5CED6",
        showland=True,
        landcolor="#F5F7FA",
    )
    fig.update_layout(**{**CHART_LAYOUT, "margin": dict(l=0, r=0, t=30, b=0)}, height=560)
    st.plotly_chart(fig, use_container_width=True)


# Tab 5: Country comparison

with compare_tab:
    st.subheader("Country comparison")
    st.caption("Select 2 to 5 economies to compare directly.")

    available_countries = sorted(filtered["Country Name"].unique())
    defaults = ["United States", "India", "China", "Japan", "Germany"]
    default_countries = [c for c in defaults if c in available_countries][:4]
    if not default_countries:
        default_countries = available_countries[:4]

    picked = st.multiselect(
        "Countries",
        options=available_countries,
        default=default_countries,
        max_selections=5,
    )

    if len(picked) < 2:
        st.info("Select at least 2 countries to compare.")
    else:
        comparison = filtered[filtered["Country Name"].isin(picked)]

        col_life, col_gdp = st.columns(2)
        with col_life:
            fig = px.line(comparison, x="Year", y="Life Expectancy",
                          color="Country Name", markers=True,
                          title="Life Expectancy")
            fig.update_layout(**CHART_LAYOUT, height=420,
                              yaxis_title="Life Expectancy (years)")
            fig.update_traces(line_width=2.5)
            st.plotly_chart(fig, use_container_width=True)

        with col_gdp:
            fig = px.line(comparison, x="Year", y="GDP per Capita",
                          color="Country Name", markers=True,
                          title="GDP per Capita")
            fig.update_layout(**CHART_LAYOUT, height=420,
                              yaxis_title="GDP per Capita (USD)")
            fig.update_traces(line_width=2.5)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("##### Latest-year summary")
        summary = (
            comparison[comparison["Year"] == selected_years[1]]
            [["Country Name", "Region", "IncomeGroup",
              "Life Expectancy", "GDP per Capita"]]
            .reset_index(drop=True)
        )
        st.dataframe(summary, use_container_width=True, hide_index=True)


# Filtered data expander (FR-11)

st.divider()
with st.expander("View filtered data table"):
    st.write(
        f"Displaying **{len(filtered):,}** rows matching the current filters."
    )
    st.dataframe(
        filtered[["Country Name", "Region", "IncomeGroup", "Year",
                  "Life Expectancy", "GDP per Capita"]].round(2),
        use_container_width=True,
        hide_index=True,
    )


# Footer

st.markdown(
    "<div style='text-align:center; color:#5A6B7D; font-size:0.8rem; "
    "padding:24px 0;'>"
    "Dashboard by Sathursiya Krishnamoorthy | w2120524 | 20241113 "
    "Data: World Bank Open Data"
    "</div>",
    unsafe_allow_html=True,
)