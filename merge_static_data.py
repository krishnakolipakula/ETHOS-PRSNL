"""Merge train and test static data."""
import pickle
from pathlib import Path

# Load both static data files
train_static = pickle.load(open("data/tokenized/mimic/train/static_data.pickle", "rb"))
test_static = pickle.load(open("data/tokenized/mimic/test/static_data.pickle", "rb"))

print(f"Train static data: {len(train_static)} patients")
print(f"Test static data: {len(test_static)} patients")

# Merge them
merged_static = {**train_static, **test_static}
print(f"Merged static data: {len(merged_static)} patients")

# Save merged
output_path = Path("data/tokenized/mimic/static_data.pickle")
with open(output_path, "wb") as f:
    pickle.dump(merged_static, f)

print(f"✓ Saved merged static data to {output_path}")
