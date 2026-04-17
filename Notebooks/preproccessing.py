"""
Phase 2: Preprocessing Script
Branch: phase-2-preprocessing
Purpose: Clean and reshape the raw merged dataset into an
         analysis-ready CSV for the Streamlit dashboard.

Input : Raw Data/Life_expectancy.csv, Raw Data/metadata_countries.csv
Output: Proccessed/life_expectancy_clean.csv  (long format)

Transformations (justified by Phase 1 audit findings):
    1. Merge life expectancy data with country metadata on Country Code
    2. Filter to 2013-2023 window (audit: only 11 nulls in this window;
       2024/2025 columns largely empty)
    3. Drop aggregate entities that lack Region metadata
       (audit: 49 such rows - e.g. "World", "OECD members")
    4. Forward-fill missing IncomeGroup per country where possible,
       then drop any remaining rows with missing IncomeGroup
    5. Melt wide (year-per-column) -> long (single Year column)
    6. Cast Year to int, drop any Life Expectancy NaNs
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
print("[1/6] Loading raw data...")
df_life = pd.read_csv(RAW_DIR / "C://Users//User//Desktop//data science//Individual//DSPL_ICW//Raw Data//Life_expectancy.csv", skiprows=3)
df_meta = pd.read_csv(RAW_DIR / "C://Users//User//Desktop//data science//Individual//DSPL_ICW//Raw Data//metadata_countries.csv")

df_life.columns = df_life.columns.str.strip()
df_meta.columns = df_meta.columns.str.strip()
print(f"       Life: {df_life.shape}, Meta: {df_meta.shape}")

# --- Merge ---
print("[2/6] Merging life expectancy with metadata...")
df = df_life.merge(
    df_meta[['Country Code', 'Region', 'IncomeGroup']],
    on='Country Code',
    how='left'
)
print(f"       Merged shape: {df.shape}")

# --- Filter to 2013-2023 year window ---
print("[3/6] Filtering to 2013-2023 window...")
id_cols = ['Country Name', 'Country Code', 'Region', 'IncomeGroup']
year_cols = [str(y) for y in range(2013, 2024)]
df = df[id_cols + year_cols]
print(f"       After filter: {df.shape}")

# --- Drop aggregate entities (no Region) ---
before = len(df)
df = df.dropna(subset=['Region'])
print(f"[4/6] Dropped {before - len(df)} aggregate rows (no Region metadata)")
print(f"       Remaining: {len(df)} countries")

# --- Handle missing IncomeGroup ---
missing_income = df['IncomeGroup'].isnull().sum()
if missing_income > 0:
    print(f"[5/6] {missing_income} rows still missing IncomeGroup - dropping them")
    df = df.dropna(subset=['IncomeGroup'])
else:
    print("[5/6] No missing IncomeGroup values")
print(f"       Remaining: {len(df)} countries")

# --- Melt wide -> long ---
print("[6/6] Melting wide -> long format...")
df_long = df.melt(
    id_vars=id_cols,
    value_vars=year_cols,
    var_name='Year',
    value_name='Life Expectancy'
)
df_long['Year'] = df_long['Year'].astype(int)
df_long = df_long.dropna(subset=['Life Expectancy'])
df_long = df_long.sort_values(['Country Name', 'Year']).reset_index(drop=True)

print(f"       Final long-format shape: {df_long.shape}")
print(f"       Year range: {df_long['Year'].min()} - {df_long['Year'].max()}")
print(f"       Regions: {df_long['Region'].nunique()}")
print(f"       Countries: {df_long['Country Name'].nunique()}")

# --- Save ---
df_long.to_csv(OUTPUT_FILE, index=False)
print(f"\nSaved clean dataset: {OUTPUT_FILE}")
print("=" * 60)
print("PREPROCESSING COMPLETE")
print("=" * 60)