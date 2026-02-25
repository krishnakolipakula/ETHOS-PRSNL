"""
Decode and display sample sequences from UF .bin files
"""
import numpy as np
import pandas as pd
from pathlib import Path

# Path to UF data (update if running on HyperGator)
data_path = Path("/orange/yonghui.wu/chenziyi/Note_Structure/Delphi_0515/data/mimic")

# Load vocabulary mapping
print("Loading vocabulary mapping...")
mapping_df = pd.read_csv(data_path / "mimic_map.csv", header=None)
token_to_text = dict(zip(mapping_df[0], mapping_df[1]))

print(f"Loaded {len(token_to_text)} vocabulary mappings\n")
print("=" * 80)

def decode_sequence(tokens, mapping, max_tokens=50):
    """Decode a sequence of tokens to readable text"""
    decoded = []
    for i, token in enumerate(tokens[:max_tokens]):
        if token == 0:
            decoded.append("SEP")
        elif token in mapping:
            decoded.append(mapping[token])
        else:
            decoded.append(f"<ID:{token}>")
    return decoded

def show_samples(split_name, bin_file, num_samples=3, tokens_per_sample=100):
    """Show sample sequences from a .bin file"""
    print(f"\n{'='*80}")
    print(f"SAMPLES FROM {split_name.upper()} SPLIT")
    print(f"{'='*80}\n")
    
    # Load data
    data = np.fromfile(bin_file, dtype=np.uint16)
    print(f"Total tokens in {split_name}: {len(data):,}")
    print(f"File size: {bin_file.stat().st_size / (1024*1024):.2f} MB\n")
    
    # Find sequence boundaries (looking for patterns of non-zero followed by zeros)
    # Sequences appear to be separated by multiple zeros
    zero_positions = np.where(data == 0)[0]
    
    # Show first few samples
    for sample_idx in range(num_samples):
        start_pos = sample_idx * 500  # Approximate spacing
        end_pos = start_pos + tokens_per_sample
        
        sample_tokens = data[start_pos:end_pos]
        decoded = decode_sequence(sample_tokens, token_to_text, max_tokens=tokens_per_sample)
        
        print(f"Sample {sample_idx + 1} (starting at position {start_pos:,}):")
        print("-" * 80)
        
        # Group by separator for better readability
        current_group = []
        for token in decoded:
            if token == "SEP":
                if current_group:
                    print("  " + ", ".join(current_group))
                    current_group = []
            else:
                current_group.append(token)
        
        if current_group:
            print("  " + ", ".join(current_group))
        
        print()

    # Show some statistics
    print("\nStatistics:")
    unique_tokens = np.unique(data)
    print(f"  Unique tokens: {len(unique_tokens):,}")
    print(f"  Token range: {unique_tokens.min()} to {unique_tokens.max()}")
    print(f"  Number of zeros (separators): {np.sum(data == 0):,} ({np.sum(data == 0)/len(data)*100:.1f}%)")
    print(f"  Number of non-zero tokens: {np.sum(data != 0):,}")
    
    # Count outcomes
    healthy_count = np.sum(data == 1)
    death_count = np.sum(data == 28572)
    print(f"  'Healthy' labels: {healthy_count:,}")
    print(f"  'Death' labels: {death_count:,}")
    
    # Show token frequency for mapped tokens
    mapped_tokens = data[(data > 0) & (data <= 28572)]
    if len(mapped_tokens) > 0:
        print(f"  Mapped medical codes: {len(mapped_tokens):,}")
        
    # Show high ID counts (patient/visit IDs)
    high_ids = data[data > 28572]
    if len(high_ids) > 0:
        print(f"  Patient/Visit IDs (>28572): {len(high_ids):,}")
        print(f"  Unique patient/visit IDs: {len(np.unique(high_ids)):,}")

# Process each split
for split, filename in [("train", "train.bin"), ("val", "val.bin"), ("test", "test.bin")]:
    bin_file = data_path / filename
    if bin_file.exists():
        show_samples(split, bin_file, num_samples=3, tokens_per_sample=100)
    else:
        print(f"\n{split.upper()} file not found: {bin_file}")

print("\n" + "=" * 80)
print("VOCABULARY SAMPLE (First 20 mappings)")
print("=" * 80)
for token_id in sorted(token_to_text.keys())[:20]:
    print(f"  {token_id:6d}: {token_to_text[token_id]}")

print("\n" + "=" * 80)
print("VOCABULARY SAMPLE (Last 20 mappings)")
print("=" * 80)
for token_id in sorted(token_to_text.keys())[-20:]:
    print(f"  {token_id:6d}: {token_to_text[token_id]}")
