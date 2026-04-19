"""
Audit of the GDP per capita dataset (extra feature).
Checks structure, nulls, and year coverage before integration.
"""

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "Raw Data"

GDP_FILE = RAW_DIR / "GDP_Data for extra feature.csv"

# Load (World Bank format - skiprows=3)
df_gdp = pd.read_csv(GDP_FILE, skiprows=3)
df_gdp.columns = df_gdp.columns.str.strip()

print("=" * 60)
print("GDP PER CAPITA - AUDIT")
print("=" * 60)

print(f"\n[1] Shape: {df_gdp.shape}")
print(f"    Countries: {df_gdp['Country Code'].nunique()}")

year_cols = [c for c in df_gdp.columns if c.isdigit()]
print(f"    Year range: {min(year_cols)} - {max(year_cols)}")
print(f"    Total nulls: {df_gdp.isnull().sum().sum()}")

print(f"\n[2] Nulls in 2013-2023 window")
target_years = [c for c in year_cols if 2013 <= int(c) <= 2023]
null_target = df_gdp[target_years].isnull().sum()
print(null_target.to_string())
print(f"    Total nulls 2013-2023: {null_target.sum()}")

print(f"\n[3] Sample values (row 0, Afghanistan)")
print(df_gdp.iloc[0][['Country Name', 'Country Code'] + target_years])

print(f"\n[4] Countries with ANY null in 2013-2023: "
      f"{df_gdp[target_years].isnull().any(axis=1).sum()} / {len(df_gdp)}")