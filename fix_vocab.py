"""Fix vocabulary to include static data codes."""
import pickle
from pathlib import Path
import polars as pl

# Load static data to see what codes it has
static_data_path = Path("data/tokenized/mimic/static_data.pickle")
with open(static_data_path, "rb") as f:
    static_data = pickle.load(f)

# Collect all codes from static data
static_codes = set()
for patient_id, patient_dict in static_data.items():
    for field_name, field_data in patient_dict.items():
        if isinstance(field_data, dict) and 'code' in field_data:
            for code in field_data['code']:
                static_codes.add(code)

print(f"Found {len(static_codes)} unique codes in static_data:")
for code in sorted(static_codes):
    print(f"  {code}")

# Load current vocabulary
vocab_path = list(Path("data/tokenized/mimic").glob("vocab_t*.csv"))[0]
current_vocab = pl.read_csv(vocab_path, has_header=False)
current_codes = set(current_vocab.to_series(0).to_list())

# Find missing codes
missing_codes = static_codes - current_codes
print(f"\nMissing {len(missing_codes)} codes from vocabulary:")
for code in sorted(missing_codes):
    print(f"  {code}")

if missing_codes:
    # Add missing codes and save
    all_codes = sorted(current_codes | missing_codes)
    new_vocab = pl.DataFrame({"code": all_codes})
    
    # Remove old vocab file
    vocab_path.unlink()
    
    # Save new vocab
    new_vocab_path = Path(f"data/tokenized/mimic/vocab_t{len(all_codes)}.csv")
    new_vocab.write_csv(new_vocab_path, include_header=False)
    print(f"\n✓ Updated vocabulary saved to {new_vocab_path}")
    print(f"✓ New vocabulary size: {len(all_codes)}")
else:
    print("\n✓ All static codes already in vocabulary")
