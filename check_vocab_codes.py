"""Check vocabulary for discharge and readmission-related codes."""
import polars as pl
from pathlib import Path

vocab_path = list(Path("data/tokenized/mimic").glob("vocab_t*.csv"))[0]
vocab = pl.read_csv(vocab_path, has_header=False)
codes = vocab.to_series(0).to_list()

print(f"Total vocabulary size: {len(codes)}")
print("\nAll codes:")
for code in sorted(codes):
    print(f"  {code}")

print("\nDischarge-related:")
discharge_codes = [c for c in codes if 'DISCHARGE' in c.upper() or 'HOSP' in c.upper()]
for code in discharge_codes:
    print(f"  {code}")

print("\nAdmission-related:")
admission_codes = [c for c in codes if 'ADMISSION' in c.upper() or 'ADMIT' in c.upper()]
for code in admission_codes:
    print(f"  {code}")

print("\nDRG codes:")
drg_codes = [c for c in codes if 'DRG' in c.upper()]
for code in drg_codes:
    print(f"  {code}")
