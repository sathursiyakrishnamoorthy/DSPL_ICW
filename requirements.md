# Requirements Specification

**Project:** Life Expectancy & GDP Dashboard  
**Author:** Sathursiya Krishnamoorthy (w2120524)  
**Module:** 5DATA004C Data Science Project Lifecycle

Requirements are classified as **Functional (FR)** or **Non-Functional (NFR)** and prioritised using the **MoSCoW** scheme (Must / Should / Could / Won't).

---

## Functional Requirements

| ID | Title | Description | Priority |
|---|---|---|---|
| FR-01 | Multi-indicator data loading | The system shall load the preprocessed dataset containing Life Expectancy and GDP per capita for 215 countries across 2013–2023. | Must |
| FR-02 | Filter by Region | Users shall be able to filter the displayed data by one or more of the seven World Bank Regions via a sidebar control. | Must |
| FR-03 | Filter by Income Group | Users shall be able to filter the displayed data by one or more of the four World Bank Income Groups (Low, Lower-middle, Upper-middle, High). | Must |
| FR-04 | Filter by Year range | Users shall be able to select a custom year range between 2013 and 2023 using a slider. | Must |
| FR-05 | Display summary KPIs | The system shall display headline metrics (average life expectancy, country count, region count, years selected) that update in response to filters. | Must |
| FR-06 | Time-series visualisation by Region | Users shall see a line chart showing average Life Expectancy over time, with one line per Region. | Must |
| FR-07 | Time-series visualisation by Income Group | Users shall see a line chart showing average Life Expectancy over time, with one line per Income Group. | Must |
| FR-08 | GDP vs Life Expectancy scatter | Users shall see a scatter plot showing the relationship between GDP per capita and Life Expectancy for a selected year, with a logarithmic GDP axis and points coloured by Region. | Must |
| FR-09 | Choropleth map | Users shall see a world map coloured by Life Expectancy for the most recent year in the selected range. | Should |
| FR-10 | Top / Bottom 10 ranking | Users shall see a bar chart showing the ten countries with the highest and ten with the lowest Life Expectancy for the selected year. | Should |
| FR-11 | Inspect filtered data | Users shall be able to expand a data table showing every country-year record currently matching the active filters. | Could |

## Non-Functional Requirements

| ID | Category | Description | Priority |
|---|---|---|---|
| NFR-01 | Performance | The dashboard shall respond to any filter change within 2 seconds on a standard broadband connection (Streamlit Cloud deployment). | Must |
| NFR-02 | Usability | All interactive controls shall be grouped in a single sidebar and labelled in plain English, requiring no training to operate. | Must |
| NFR-03 | Accessibility | All charts shall have descriptive titles, axis labels, and legends, and shall rely on a colour-blind-safe palette so meaning is not encoded by colour alone. | Should |
| NFR-04 | Availability & Reliability | The deployed Streamlit Cloud application shall remain publicly accessible, without authentication, until at least 1st August 2026 per the module's examiner-access requirement. | Must |