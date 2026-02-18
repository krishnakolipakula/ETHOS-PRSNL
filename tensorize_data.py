"""Convert tokenized parquet files to safetensors format for training."""
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ethos.datasets.base import TimelineDataset
from ethos.vocabulary import Vocabulary

# Paths
tokenized_dir = Path("data/tokenized/mimic")
train_dir = tokenized_dir / "train" / "12_inject_time_intervals"
test_dir = tokenized_dir / "test" / "12_inject_time_intervals"
output_dir = tokenized_dir
code_counts_fp = tokenized_dir / "train" / "code_counts.csv"

print("Creating vocabulary from code counts...")
# Read code counts from both train and test, combine them
train_code_counts = pl.read_csv(tokenized_dir / "train" / "code_counts.csv")
test_code_counts = pl.read_csv(tokenized_dir / "test" / "code_counts.csv")

# Combine and get unique codes
all_codes = pl.concat([
    train_code_counts.select("code"),
    test_code_counts.select("code")
]).unique().sort("code")

vocab_tokens = all_codes["code"].to_list()
vocab = Vocabulary(vocab_tokens)
print(f"Vocabulary size: {len(vocab)}")

# Save vocabulary
print(f"Saving vocabulary to {output_dir}/vocab_t{len(vocab)}.csv")
vocab.dump(output_dir)

# Tensorize train data
print("\nTensorizing train data...")
train_fps = sorted(train_dir.glob("*.parquet"))
for fp in train_fps:
    out_fp = output_dir / fp.stem
    print(f"  {fp.name} -> {out_fp.name}.safetensors")
    TimelineDataset.tensorize(fp, out_fp, vocab)

# Tensorize test data
print("\nTensorizing test data...")
test_fps = sorted(test_dir.glob("*.parquet"))
for i, fp in enumerate(test_fps, start=len(train_fps)):
    out_fp = output_dir / str(i)
    print(f"  {fp.name} -> {out_fp.name}.safetensors")
    TimelineDataset.tensorize(fp, out_fp, vocab)

print(f"\n✓ Tensorization complete! Created {len(train_fps) + len(test_fps)} safetensors files in {output_dir}")
print(f"✓ Vocabulary saved with {len(vocab)} tokens")
