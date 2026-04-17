"""
Phase 1: Data Audit Script
Branch: phase-1-data-audit
Purpose: Audit raw datasets for quality issues before preprocessing
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

# Strip any hidden whitespace in column names
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
print("  - Countries missing Region (aggregate/non-sovereign entries)")
print("  - Countries missing IncomeGroup (same cause)")
print("  - Year 2024/2025 columns largely empty - filter to 2013-2023")
print("  - Dataset is in WIDE format - melt required for visualisation")
print("=" * 60)