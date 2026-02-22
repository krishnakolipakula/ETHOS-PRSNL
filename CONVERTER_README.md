# UF to ETHOS Converter

This script converts UF triplet format data to ETHOS-compatible sequences for training.

## Format Transformation

### Input (UF Triplet Format)
```
Binary files: train.bin, val.bin, test.bin
Format: uint32 array reshaped to (-1, 3)
Columns: [patient_id, age_in_days, icd_code]
```

### Output (ETHOS Sequence Format)
```
Sharded .safetensors files
One sequence per patient: [demographics, TIME_TOKEN, codes, TIME_TOKEN, codes, ...]
```

## Time Interval Bins

The converter quantizes time deltas between encounters into ETHOS-style bins:

| Time Delta (days) | Token Name | Example |
|-------------------|------------|---------|
| 0-1 days | TIME_0-1DAY | Same day follow-up |
| 1-7 days | TIME_1-7DAY | Weekly follow-up |
| 7-30 days | TIME_7-30DAY | Monthly follow-up |
| 30-365 days | TIME_30-365DAY | Annual follow-up |
| 365-730 days | TIME_1-2YEAR | 1-2 year gap |
| 730+ days | TIME_2+YEAR | Long-term follow-up |

## Example

**Patient 11 Triplets:**
```
[11, 0, Healthy]        # Demographics
[11, 0, M]              # Demographics
[11, 31594, Z20822]     # Age 86.5 years
[11, 31594, 4280]       # Same encounter
[11, 31670, 3899]       # 76 days later (age 86.7)
[11, 32169, 41401]      # 499 days later (age 88.1)
```

**Converted Sequence:**
```
[Healthy, M, TIME_2+YEAR, Z20822, 4280, TIME_30-365DAY, 3899, TIME_1-2YEAR, 41401]
 └─demo─┘  └─31594 days from age 0─┘         └─76 days later─┘       └─499 days later─┘
```

## Vocabulary

- **Original UF vocab:** 28,572 tokens (demographics + ICD-9/10 + outcomes)
- **Added time tokens:** 6 time interval tokens
- **Total vocab size:** 28,578 tokens

The converter saves an updated vocabulary.csv with all tokens including the new time interval tokens.

## Usage

### On HyperGator:
```bash
python convert_uf_to_ethos_format.py \
    --input_dir /orange/yonghui.wu/chenziyi/Note_Structure/Delphi_0515/data/mimic \
    --output_dir /blue/yonghui.wu/kolipakulak/ethos-ares/data/tokenized/uf_converted \
    --vocab_map mimic_map.csv \
    --max_seq_length 2048 \
    --shard_size 10000
```

### On Mac (for testing):
```bash
python convert_uf_to_ethos_format.py \
    --input_dir data/uf_sample \
    --output_dir data/tokenized/uf_converted \
    --vocab_map data/uf_sample/mimic_map.csv
```

## Output Structure

```
output_dir/
├── train/
│   ├── 0.safetensors
│   ├── 1.safetensors
│   └── ...
├── val/
│   └── 0.safetensors
├── test/
│   └── 0.safetensors
├── metadata.json
└── vocabulary.csv
```

## Key Features

1. **Time Quantization:** Converts raw ages to time interval bins matching ETHOS format
2. **Temporal Ordering:** Preserves chronological order of medical events
3. **Efficient Storage:** Sharded .safetensors files for fast loading
4. **ETHOS Compatible:** Output directly usable with ETHOS training scripts

## Next Steps

After conversion:
1. Update ETHOS config to use new vocab size (28,578)
2. Point training script to converted data path
3. Train model with UF data
4. Run inference on test set
