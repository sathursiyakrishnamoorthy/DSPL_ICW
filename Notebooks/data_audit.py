"""
Phase 1: Data Audit Script
Branch: phase-1-data-audit
Purpose: Audit raw datasets for quality issues before preprocessing

================================================================
AUDIT FINDINGS SUMMARY (run date: see Git commit)
================================================================

Dataset sources (World Bank Open Data):
    - Life_expectancy.csv      : Life expectancy at birth, total (years)
    - metadata_countries.csv   : Country classifications (Region, IncomeGroup)

DATASET DIMENSIONS
    Life expectancy : 266 rows x 70 columns (years 1960 - 2025)
    Metadata        : 265 rows x 5 columns

NULL VALUES
    Life expectancy total nulls : 365
    Worst year for nulls        : 2025 (266 nulls - column is empty)
    Nulls in 2013-2023 window   : 11 (acceptable for analysis)
    Metadata Region nulls       : 48
    Metadata IncomeGroup nulls  : 50

FORMATTING / STRUCTURAL ISSUES
    - Dataset is in WIDE format (year-per-column) -> melt required
    - Year columns are stored as strings -> cast to int in Phase 2
    - 49 rows remain unmatched after merge (aggregate entities
      such as "World", "OECD members", "European Union") - these
      lack sovereign country metadata by design.

DECISIONS CARRIED INTO PHASE 2 (preprocessing)
    1. Filter dataset to a 10-year window (2013-2023) to minimise
       nulls and keep analysis focused on modern trends.
    2. Drop the 2025 column (entirely empty) and 2024 (sparse).
    3. Drop rows with no Region (aggregate entities) to ensure
       geographic visualisations remain meaningful.
    4. Melt wide -> long format (Year, Life Expectancy).
    5. Impute missing IncomeGroup where possible; drop otherwise.

================================================================
"""

import pandas as pd
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "Raw Data"
OUT_DIR = PROJECT_ROOT / "Proccessed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --- LOAD RAW DATA ---
df_life = pd.read_csv(RAW_DIR / "Life_expectancy.csv", skiprows=3)
df_meta = pd.read_csv(RAW_DIR / "metadata_countries.csv")

df_life.columns = df_life.columns.str.strip()
df_meta.columns = df_meta.columns.str.strip()

print("=" * 60)
print("PHASE 1: DATA AUDIT REPORT")
print("=" * 60)

# --- LIFE EXPECTANCY DATASET ---
print("\n[1] Life Expectancy Dataset")
print(f"    Shape        : {df_life.shape[0]} rows x {df_life.shape[1]} columns")
print(f"    Countries    : {df_life['Country Code'].nunique()}")
print(f"    Total nulls  : {df_life.isnull().sum().sum()}")

year_cols = [c for c in df_life.columns if c.isdigit()]
null_by_year = df_life[year_cols].isnull().sum()
print(f"    Year range   : {min(year_cols)} - {max(year_cols)}")
print(f"    Worst year for nulls: {null_by_year.idxmax()} ({null_by_year.max()} nulls)")
print(f"    Years 2013-2023 nulls: {df_life[[c for c in year_cols if 2013 <= int(c) <= 2023]].isnull().sum().sum()}")

# --- METADATA DATASET ---
print("\n[2] Metadata (Countries) Dataset")
print(f"    Shape        : {df_meta.shape[0]} rows x {df_meta.shape[1]} columns")
print(f"    Null Region  : {df_meta['Region'].isnull().sum()}")
print(f"    Null Income  : {df_meta['IncomeGroup'].isnull().sum()}")
print(f"    Regions      : {df_meta['Region'].dropna().unique().tolist()}")
print(f"    Income Groups: {df_meta['IncomeGroup'].dropna().unique().tolist()}")

# --- MERGE TEST ---
print("\n[3] Merge Test (Life Expectancy + Metadata)")
df_merged = pd.merge(
    df_life,
    df_meta[['Country Code', 'Region', 'IncomeGroup']],
    on='Country Code',
    how='left'
)
print(f"    Merged shape : {df_merged.shape}")
print(f"    Unmatched codes: {df_merged['Region'].isnull().sum()} rows with no Region after merge")

# Export raw merged snapshot for audit evidence
df_merged.to_csv(OUT_DIR / "audit_raw_merge.csv", index=False)
print(f"\n[4] Exported: {OUT_DIR / 'audit_raw_merge.csv'}")

print("\n" + "=" * 60)
print("AUDIT COMPLETE - Issues identified for Phase 2:")
print("  - 49 unmatched country codes (aggregate/non-sovereign entries)")
print("  - 50 metadata rows missing IncomeGroup")
print("  - Year 2024/2025 columns largely empty - filter to 2013-2023")
print("  - Dataset is in WIDE format - melt required for visualisation")
print("=" * 60)