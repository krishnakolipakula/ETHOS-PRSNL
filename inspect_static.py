"""Inspect static data structure."""
import pickle
from pathlib import Path

static_data_path = Path("data/tokenized/mimic/static_data.pickle")
with open(static_data_path, "rb") as f:
    static_data = pickle.load(f)

print(f"Type: {type(static_data)}")
print(f"Length: {len(static_data)}")

# Show first few entries
for i, (key, value) in enumerate(list(static_data.items())[:3]):
    print(f"\nEntry {i+1}:")
    print(f"  Key: {key} (type: {type(key)})")
    print(f"  Value: {value}")
    print(f"  Value type: {type(value)}")
    if hasattr(value, '__iter__') and not isinstance(value, str):
        print(f"  Value length: {len(value)}")
        if len(value) > 0:
            print(f"  First item: {value[0]}")
            print(f"  First item type: {type(value[0])}")
