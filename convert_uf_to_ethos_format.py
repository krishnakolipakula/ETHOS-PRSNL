"""
Convert UF binary triplet format to ETHOS-compatible .safetensors format

Input: (N, 3) triplets [patient_id, age_days, icd_code]
Output: ETHOS tokenized sequences with temporal information
"""
import numpy as np
import pandas as pd
from pathlib import Path
from collections import defaultdict
import torch
from safetensors.torch import save_file
from tqdm import tqdm
import argparse

class UFToETHOSConverter:
    def __init__(self, uf_data_dir, output_dir, vocab_map_path):
        self.uf_data_dir = Path(uf_data_dir)
        self.output_dir = Path(output_dir)
        self.vocab_map_path = Path(vocab_map_path)
        
        # Load vocabulary mapping
        print("Loading vocabulary mapping...")
        mapping_df = pd.read_csv(self.vocab_map_path)
        self.token_to_text = dict(zip(
            mapping_df['Mapped Value'].astype(int), 
            mapping_df['Original Value']
        ))
        
        # Create reverse mapping for encoding
        self.text_to_token = {v: k for k, v in self.token_to_text.items()}
        
        # Special tokens for ETHOS
        self.GENDER_TOKENS = {2, 3}  # F, M
        self.RACE_TOKENS = {4, 5, 6, 7, 8, 9}  # race categories
        self.OUTCOME_TOKENS = {1, 28572}  # Healthy, Death
        
        # Time interval bins (in days) - ETHOS-style quantization
        self.TIME_BINS = [
            (0, 1, "TIME_0-1DAY"),
            (1, 7, "TIME_1-7DAY"),
            (7, 30, "TIME_7-30DAY"),
            (30, 365, "TIME_30-365DAY"),
            (365, 730, "TIME_1-2YEAR"),
            (730, float('inf'), "TIME_2+YEAR")
        ]
        
        # Add time interval tokens to vocabulary (starting after max existing token)
        max_token = max(self.token_to_text.keys())
        self.time_tokens = {}
        for i, (_, _, name) in enumerate(self.TIME_BINS):
            token_id = max_token + 1 + i
            self.time_tokens[name] = token_id
            self.token_to_text[token_id] = name
        
        print(f"Loaded {len(self.token_to_text)} vocabulary mappings")
        print(f"Added {len(self.time_tokens)} time interval tokens: {list(self.time_tokens.keys())}")
    
    def quantize_time_delta(self, days_delta):
        """Convert time delta in days to time interval token"""
        for min_days, max_days, name in self.TIME_BINS:
            if min_days <= days_delta < max_days:
                return self.time_tokens[name]
        # Default to longest interval if exceeds bins
        return self.time_tokens["TIME_2+YEAR"]
        
    def load_triplet_data(self, split_name):
        """Load UF binary data in triplet format"""
        bin_file = self.uf_data_dir / f'{split_name}.bin'
        print(f"\nLoading {split_name} split...")
        data = np.memmap(bin_file, dtype=np.uint32, mode='r').reshape(-1, 3)
        print(f"  Total triplets: {len(data):,}")
        return data
    
    def group_by_patient(self, data):
        """Group triplets by patient ID"""
        print("Grouping by patient...")
        patients = defaultdict(list)
        
        for row in tqdm(data, desc="Processing triplets"):
            patient_id = int(row[0])
            age_days = int(row[1])
            code = int(row[2])
            patients[patient_id].append((age_days, code))
        
        print(f"  Unique patients: {len(patients):,}")
        return patients
    
    def create_patient_sequence(self, patient_records):
        """
        Convert patient records to ETHOS sequence format:
        [demographics, time_interval, codes, time_interval, codes, ...]
        """
        # Separate demographics (age_days=0) from medical events
        demographics = []
        events = []
        
        for age_days, code in patient_records:
            if age_days == 0:
                demographics.append(code)
            else:
                events.append((age_days, code))
        
        # Sort events by age (temporal order)
        events.sort(key=lambda x: x[0])
        
        # Build sequence
        sequence = []
        
        # Add demographics first
        for demo_code in demographics:
            sequence.append(demo_code)
        
        # Group events by age (same age = same encounter)
        if events:
            encounters = defaultdict(list)
            for age_days, code in events:
                encounters[age_days].append(code)
            
            # Add encounters in temporal order
            prev_age = 0
            for age_days in sorted(encounters.keys()):
                # Calculate time interval (days since last event)
                time_delta = age_days - prev_age
                
                # Add time interval token (quantized using ETHOS bins)
                time_token = self.quantize_time_delta(time_delta)
                sequence.append(time_token)
                
                # Add all codes from this encounter
                for code in encounters[age_days]:
                    sequence.append(code)
                
                prev_age = age_days
        
        return sequence
    
    def convert_split(self, split_name, max_seq_length=2048, shard_size=10000):
        """Convert one split (train/val/test) to ETHOS format"""
        print(f"\n{'='*80}")
        print(f"Converting {split_name.upper()} split")
        print(f"{'='*80}")
        
        # Load data
        data = self.load_triplet_data(split_name)
        
        # Group by patient
        patients = self.group_by_patient(data)
        
        # Create output directory
        output_split_dir = self.output_dir / split_name
        output_split_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert each patient to sequence
        print("\nCreating ETHOS sequences...")
        sequences = []
        patient_ids_list = []
        static_data = {}  # For static_data.pickle
        
        for patient_id, records in tqdm(patients.items(), desc="Building sequences"):
            sequence = self.create_patient_sequence(records)
            
            # Truncate if too long
            if len(sequence) > max_seq_length:
                sequence = sequence[:max_seq_length]
            
            sequences.append(sequence)
            patient_ids_list.append(patient_id)
            
            # Add dummy static data entry (ETHOS requires this)
            # Using a single zero value for each patient
            static_data[patient_id] = [0]  # Minimal static feature
        
        print(f"  Created {len(sequences):,} sequences")
        
        # Compute statistics
        seq_lengths = [len(seq) for seq in sequences]
        print(f"\nSequence length statistics:")
        print(f"  Min: {min(seq_lengths)}")
        print(f"  Max: {max(seq_lengths)}")
        print(f"  Mean: {np.mean(seq_lengths):.1f}")
        print(f"  Median: {np.median(seq_lengths):.1f}")
        
        # Save as sharded .safetensors files
        print(f"\nSaving to .safetensors (shard size: {shard_size})...")
        num_shards = (len(sequences) + shard_size - 1) // shard_size
        
        for shard_idx in tqdm(range(num_shards), desc="Writing shards"):
            start_idx = shard_idx * shard_size
            end_idx = min(start_idx + shard_size, len(sequences))
            
            shard_sequences = sequences[start_idx:end_idx]
            shard_patient_ids = patient_ids_list[start_idx:end_idx]
            
            # ETHOS expects flattened 1D arrays, not 2D padded arrays
            # Concatenate all sequences into a single flat array
            flat_tokens = np.concatenate([np.array(seq, dtype=np.int32) for seq in shard_sequences])
            flat_times = np.zeros(len(flat_tokens), dtype=np.int32)  # All zeros for non-temporal
            
            # Create patient_offsets: cumulative sequence lengths
            seq_lengths = np.array([len(seq) for seq in shard_sequences], dtype=np.int32)
            patient_offsets = np.concatenate([[0], np.cumsum(seq_lengths)[:-1]])
            
            # Convert to tensors and save
            tensors = {
                'tokens': torch.from_numpy(flat_tokens),
                'times': torch.from_numpy(flat_times),
                'patient_offsets': torch.from_numpy(patient_offsets),
                'patient_ids': torch.tensor(shard_patient_ids, dtype=torch.int32)
            }
            
            shard_file = output_split_dir / f"{shard_idx}.safetensors"
            save_file(tensors, shard_file)
        
        print(f"\n✓ Saved {num_shards} shards to {output_split_dir}")
        
        # Save metadata
        metadata = {
            'num_sequences': len(sequences),
            'num_shards': num_shards,
            'shard_size': shard_size,
            'max_seq_length': max_seq_length,
            'vocab_size': max(self.token_to_text.keys()) + 1,
            'min_seq_len': int(min(seq_lengths)),
            'max_seq_len': int(max(seq_lengths)),
            'mean_seq_len': float(np.mean(seq_lengths)),
            'median_seq_len': float(np.median(seq_lengths))
        }
        
        import json
        with open(output_split_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Save static_data.pickle for ETHOS
        # Each patient needs a static feature entry (using minimal dummy data)
        import pickle
        with open(output_split_dir / 'static_data.pickle', 'wb') as f:
            pickle.dump(static_data, f)
        
        # Save interval_estimates.json (optional, but avoids warning)
        interval_estimates = {}  # No interval estimates for UF data
        with open(output_split_dir / 'interval_estimates.json', 'w') as f:
            json.dump(interval_estimates, f)
        
        return metadata
    
    def convert_all_splits(self, max_seq_length=2048, shard_size=10000):
        """Convert train, val, and test splits"""
        print(f"\n{'='*80}")
        print("UF TO ETHOS FORMAT CONVERTER")
        print(f"{'='*80}")
        print(f"\nInput directory: {self.uf_data_dir}")
        print(f"Output directory: {self.output_dir}")
        print(f"Max sequence length: {max_seq_length}")
        print(f"Shard size: {shard_size}")
        
        all_metadata = {}
        
        for split in ['train', 'val', 'test']:
            metadata = self.convert_split(split, max_seq_length, shard_size)
            all_metadata[split] = metadata
        
        print(f"\n{'='*80}")
        print("CONVERSION COMPLETE")
        print(f"{'='*80}")
        
        for split, meta in all_metadata.items():
            print(f"\n{split.upper()}:")
            print(f"  Sequences: {meta['num_sequences']:,}")
            print(f"  Shards: {meta['num_shards']}")
            print(f"  Avg seq length: {meta['mean_seq_len']:.1f}")
        
        print(f"\n✓ All data converted to ETHOS format at: {self.output_dir}")
        
        # Save updated vocabulary with time tokens
        self.save_vocabulary()
    
    def save_vocabulary(self):
        """Save updated vocabulary including time interval tokens"""
        # ETHOS expects vocab in train directory named vocab_t*.csv
        train_dir = self.output_dir / "train"
        vocab_file = train_dir / "vocab_tokens.csv"
        
        vocab_data = []
        for token_id, text in sorted(self.token_to_text.items()):
            vocab_data.append({'token_id': token_id, 'text': text})
        
        vocab_df = pd.DataFrame(vocab_data)
        vocab_df.to_csv(vocab_file, index=False)
        
        print(f"\n✓ Saved vocabulary ({len(vocab_data)} tokens) to {vocab_file}")
        print(f"  Original vocab: 28,572 tokens")
        print(f"  Time interval tokens: {len(self.time_tokens)}")
        print(f"  Total vocab size: {len(vocab_data)}")


def main():
    parser = argparse.ArgumentParser(description='Convert UF triplet format to ETHOS sequences')
    parser.add_argument('--input_dir', type=str, 
                       default='/orange/yonghui.wu/chenziyi/Note_Structure/Delphi_0515/data/mimic',
                       help='Input directory with UF .bin files')
    parser.add_argument('--output_dir', type=str,
                       default='/blue/yonghui.wu/kolipakulak/ethos-ares/data/tokenized/uf_converted',
                       help='Output directory for ETHOS .safetensors files')
    parser.add_argument('--vocab_map', type=str,
                       default='/orange/yonghui.wu/chenziyi/Note_Structure/Delphi_0515/data/mimic/mimic_map.csv',
                       help='Path to vocabulary mapping CSV')
    parser.add_argument('--max_seq_length', type=int, default=2048,
                       help='Maximum sequence length')
    parser.add_argument('--shard_size', type=int, default=10000,
                       help='Number of sequences per shard')
    
    args = parser.parse_args()
    
    # Create converter
    converter = UFToETHOSConverter(
        uf_data_dir=args.input_dir,
        output_dir=args.output_dir,
        vocab_map_path=args.vocab_map
    )
    
    # Convert all splits
    converter.convert_all_splits(
        max_seq_length=args.max_seq_length,
        shard_size=args.shard_size
    )


if __name__ == '__main__':
    main()
