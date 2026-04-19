"""
Compatibility check between Life Expectancy and GDP datasets.
Verifies that country codes match and the merge will work cleanly.
"""

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "Raw Data"

df_life = pd.read_csv(RAW_DIR / "Life_expectancy.csv", skiprows=3)
df_gdp = pd.read_csv(RAW_DIR / "GDP_Data for extra feature.csv", skiprows=3)

df_life.columns = df_life.columns.str.strip()
df_gdp.columns = df_gdp.columns.str.strip()

print("=" * 60)
print("COMPATIBILITY CHECK: Life Expectancy vs GDP")
print("=" * 60)

life_codes = set(df_life['Country Code'])
gdp_codes = set(df_gdp['Country Code'])

print(f"\nLife Expectancy - unique country codes : {len(life_codes)}")
print(f"GDP              - unique country codes : {len(gdp_codes)}")
print(f"Codes in BOTH datasets                  : {len(life_codes & gdp_codes)}")
print(f"Codes in Life but NOT GDP               : {len(life_codes - gdp_codes)}")
print(f"Codes in GDP but NOT Life               : {len(gdp_codes - life_codes)}")

only_life = life_codes - gdp_codes
only_gdp = gdp_codes - life_codes

if only_life:
    print(f"\n  Countries in Life Expectancy only: {sorted(only_life)}")
if only_gdp:
    print(f"\n  Countries in GDP only: {sorted(only_gdp)}")

print(f"\nFirst 5 country codes in each:")
print(f"  Life: {df_life['Country Code'].head().tolist()}")
print(f"  GDP : {df_gdp['Country Code'].head().tolist()}")

# Sanity check: USA in 2020
print(f"\nSpot check for USA in 2020:")
usa_life = df_life[df_life['Country Code'] == 'USA'][['Country Name', '2020']]
usa_gdp = df_gdp[df_gdp['Country Code'] == 'USA'][['Country Name', '2020']]
print(f"  Life Expectancy: {usa_life.iloc[0]['2020']:.2f} years")
print(f"  GDP per Capita : ${usa_gdp.iloc[0]['2020']:,.2f}")

print("\n" + "=" * 60)
if len(life_codes & gdp_codes) == len(life_codes) == len(gdp_codes):
    print("PERFECT MATCH - safe to merge on Country Code")
else:
    print("PARTIAL MATCH - review differences before merging")
print("=" * 60)