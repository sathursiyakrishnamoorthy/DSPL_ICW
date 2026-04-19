"""
Phase 2: Preprocessing Script (v2 - with GDP integration)
Branch: phase-2b-add-gdp

Purpose:
    Clean and reshape the raw datasets into an analysis-ready CSV
    for the Streamlit dashboard, combining life expectancy with
    GDP per capita to enable multi-indicator analysis.

Inputs:
    - Raw Data/Life_expectancy.csv
    - Raw Data/GDP_Data for extra feature.csv
    - Raw Data/metadata_countries.csv

Output:
    - Proccessed/life_expectancy_clean.csv (long format)

Transformations:
    1. Merge life expectancy + GDP on Country Code + Year
    2. Join country metadata (Region, IncomeGroup)
    3. Filter to 2013-2023 window
    4. Drop aggregate entities (no Region)
    5. Drop countries with no IncomeGroup
    6. Forward-fill missing GDP within each country
    7. Drop any remaining country-years with no Life Expectancy
    8. Output long-format CSV (one row per country-year)
"""

import pandas as pd
from pathlib import Path

# --- Paths ---
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "Raw Data"
OUT_DIR = PROJECT_ROOT / "Proccessed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUT_DIR / "life_expectancy_clean.csv"

# --- Load ---
print("[1/8] Loading raw data...")
df_life = pd.read_csv(RAW_DIR / "Life_expectancy.csv", skiprows=3)
df_gdp = pd.read_csv(RAW_DIR / "GDP_Data for extra feature.csv", skiprows=3)
df_meta = pd.read_csv(RAW_DIR / "metadata_countries.csv")

for d in (df_life, df_gdp, df_meta):
    d.columns = d.columns.str.strip()

print(f"       Life: {df_life.shape}, GDP: {df_gdp.shape}, Meta: {df_meta.shape}")

# --- Filter to 2013-2023 window (before melting) ---
id_cols = ['Country Name', 'Country Code']
year_cols = [str(y) for y in range(2013, 2024)]

df_life = df_life[id_cols + year_cols]
df_gdp = df_gdp[id_cols + year_cols]

# --- Melt both to long format ---
print("[2/8] Melting life expectancy + GDP to long format...")
df_life_long = df_life.melt(
    id_vars=id_cols, value_vars=year_cols,
    var_name='Year', value_name='Life Expectancy'
)
df_gdp_long = df_gdp.melt(
    id_vars=id_cols, value_vars=year_cols,
    var_name='Year', value_name='GDP per Capita'
)
df_life_long['Year'] = df_life_long['Year'].astype(int)
df_gdp_long['Year'] = df_gdp_long['Year'].astype(int)

# --- Merge life + gdp on country + year ---
print("[3/8] Merging life expectancy with GDP...")
df = df_life_long.merge(df_gdp_long, on=['Country Name', 'Country Code', 'Year'], how='left')
print(f"       After indicator merge: {df.shape}")

# --- Join metadata (Region, IncomeGroup) ---
print("[4/8] Joining country metadata...")
df = df.merge(
    df_meta[['Country Code', 'Region', 'IncomeGroup']],
    on='Country Code', how='left'
)
print(f"       After metadata join: {df.shape}")

# --- Drop aggregates ---
before = len(df)
df = df.dropna(subset=['Region'])
print(f"[5/8] Dropped {before - len(df)} rows from aggregate entities")

# --- Drop rows missing IncomeGroup ---
before = len(df)
df = df.dropna(subset=['IncomeGroup'])
print(f"[6/8] Dropped {before - len(df)} rows with missing IncomeGroup")

# --- Forward-fill missing GDP within each country ---
gdp_missing_before = df['GDP per Capita'].isnull().sum()
df = df.sort_values(['Country Code', 'Year'])
df['GDP per Capita'] = df.groupby('Country Code')['GDP per Capita'].ffill().bfill()
gdp_missing_after = df['GDP per Capita'].isnull().sum()
print(f"[7/8] GDP forward-fill: {gdp_missing_before} -> {gdp_missing_after} missing")

# --- Drop any rows still missing Life Expectancy or GDP ---
before = len(df)
df = df.dropna(subset=['Life Expectancy', 'GDP per Capita'])
print(f"[8/8] Final drop (Life Exp / GDP nulls): {before - len(df)} rows")

# --- Final sort & save ---
df = df.sort_values(['Country Name', 'Year']).reset_index(drop=True)

print(f"\n       Final dataset shape : {df.shape}")
print(f"       Columns             : {df.columns.tolist()}")
print(f"       Year range          : {df['Year'].min()} - {df['Year'].max()}")
print(f"       Countries           : {df['Country Name'].nunique()}")
print(f"       Regions             : {df['Region'].nunique()}")
print(f"       Income groups       : {df['IncomeGroup'].nunique()}")

df.to_csv(OUTPUT_FILE, index=False)
print(f"\nSaved: {OUTPUT_FILE}")
print("=" * 60)
print("PREPROCESSING COMPLETE (v2 with GDP)")
print("=" * 60)