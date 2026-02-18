# Tokenization Fix: ICU Column Error

## Problem Diagnosis
**Error**: `polars.exceptions.ColumnNotFoundError: icustay_id`

**Root Cause**: The MIMIC tokenization pipeline's stage 06 (`preprocessing_with_num_quantiles`) processes ICU SOFA scores and expects an `icustay_id` column from ICU tables. Your extraction only includes 5 non-ICU tables (patients, admissions, diagnoses_icd, prescriptions, drgcodes) per Ziyi's requirements.

## Solution: Skip ICU Processing Stage

### Files Created

1. **src/ethos/configs/dataset/mimic_no_icu.yaml**
   - Modified tokenization config that comments out stage 06 (ICU processing)
   - All other stages remain identical to original MIMIC pipeline
   - Now stages are numbered: 01-05, then 06 becomes 07 (Quantizator), etc.

2. **scripts/run_tokenization_no_icu.sh**
   - New tokenization script using `dataset=mimic_no_icu` parameter
   - Outputs to new directory: `tokenized_datasets/mimic-ziyi-no-icu`
   - Uses 8 workers for train, 2 for test

### Steps to Execute on HyperGator

```bash
# 1. Upload the new config file
scp src/ethos/configs/dataset/mimic_no_icu.yaml kolipakulak@hpg.rc.ufl.edu:/blue/yonghui.wu/kolipakulak/ethos-ares/src/ethos/configs/dataset/

# 2. Upload the new tokenization script
scp scripts/run_tokenization_no_icu.sh kolipakulak@hpg.rc.ufl.edu:/blue/yonghui.wu/kolipakulak/ethos-ares/scripts/

# 3. SSH to HyperGator
ssh kolipakulak@hpg.rc.ufl.edu

# 4. Navigate to scripts directory
cd /blue/yonghui.wu/kolipakulak/ethos-ares/scripts

# 5. Make script executable
chmod +x run_tokenization_no_icu.sh

# 6. Submit the job
sbatch run_tokenization_no_icu.sh

# 7. Monitor progress
squeue -u kolipakulak
tail -f /blue/yonghui.wu/kolipakulak/ethos-ares/logs/tokenize_no_icu_<JOB_ID>.log
```

### What Changed

**Stage 06 removed**: ICU SOFA score processing
- **Original**: `ICUStayData.process` - adds ICU type and SOFA quantile tokens
- **Impact**: Model won't have ICU-specific severity scores, but you don't have ICU data anyway

**All other stages intact**:
- Lab quantiles ✓
- Demographics ✓
- DRG codes ✓
- Diagnoses ICD-9→10 conversion ✓
- Procedures ICD-9→10 conversion ✓
- Medications ATC conversion ✓
- Static data collection ✓
- Time interval injection ✓

### Expected Outcome

- Tokenization completes all 14 stages (with stage 06 skipped)
- Output directory: `/blue/.../tokenized_datasets/mimic-ziyi-no-icu/train/`
- Files produced:
  - `01-05/` directories (existing, will be reused)
  - `06_Quantizator/` (was previously 07)
  - `07-13/` (continue through pipeline)
  - `vocab_t70.csv` (vocabulary file)
  - `static_data.pickle` (patient static features)
  - `interval_estimates.json` (time encoding)
  - `quantiles.json` (numeric quantization)
  - `0.safetensors` (final tokenized data)

### Training Update

After tokenization completes, update training script:

```bash
# In run_training_demo.sh or new script
DATA_PATH="/blue/yonghui.wu/kolipakulak/ethos-ares/data/tokenized_datasets/mimic-ziyi-no-icu/train"
```

### Estimated Time
- **Tokenization**: 2-3 hours with 8 workers on 91K patients
- **Meeting**: 4 PM today
- **Timing**: Submit now (~10:30 AM?) → Complete by 1:30 PM → Have results for meeting ✓

### Alternative: Quick Validation

If you want to test this works before full run:

```bash
# Test on small subset first (worker=0 only)
ethos_tokenize -m \
    worker=0 \
    input_dir=/blue/.../mimic-meds-ziyi/data/train \
    output_dir=/blue/.../test_no_icu \
    out_fn=train \
    dataset=mimic_no_icu
```

Should complete in ~15 minutes and show if stage 06 error is resolved.
