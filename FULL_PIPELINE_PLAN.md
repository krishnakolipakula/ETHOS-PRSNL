# Full Pipeline Re-Extraction Timeline & Plan
## February 4, 2026 - Post-Meeting Action Plan

---

## Executive Summary

**Decision:** Include 12 tables (up from 5) based on Ziyi's approval  
**Goal:** Improve model performance on all 4 clinical tasks  
**Timeline:** ~1 week for complete pipeline  
**Current baseline:** 812 iterations, loss 3.51, checkpoint saved ✅

---

## What Changed: 5 Tables → 12 Tables

### Original 5 Tables (Baseline Run)
1. patients - Demographics
2. admissions - Hospital admissions
3. diagnoses_icd - ICD diagnosis codes
4. prescriptions - Medication orders
5. drgcodes - DRG billing codes

### Adding 7 New Tables

**From hosp module (+3):**
6. labevents - Laboratory results (CBC, BMP, Troponin, etc.)
7. procedures_icd - ICD procedure codes  
8. services - Department/service transfers

**From ICU module (+4):**
9. icustays - ICU admissions/discharges
10. chartevents - ICU vitals (heart rate, BP, SpO2, etc.)
11. procedureevents - ICU procedures
12. inputevents - ICU medications/fluids

---

## Expected Impact

### Vocabulary Growth
- **Current:** 39,203 tokens
- **Projected:** 50,000-60,000 tokens
- **Increase:** ~50% larger vocabulary

### Event Volume
- **Current:** 21.4M prescription events
- **Projected:** 50-100M total events (labs + vitals add most)
- **Note:** chartevents filtering critical (300M+ rows if unfiltered)

### Clinical Features
- ✅ Real ICU timestamps (not inferred)
- ✅ Laboratory values for mortality prediction
- ✅ Vital signs for acuity assessment
- ✅ ICU procedures for severity
- ✅ Complete medication picture (hospital + ICU)

### Performance Expectations
- **Hospital Mortality:** Should improve (lab values critical)
- **ICU Mortality:** Major improvement (ICU-specific data)
- **Readmission:** Moderate improvement (procedures, services)
- **ICU Admission:** Major improvement (labs, vitals for triage)

---

## Step-by-Step Timeline

### ✅ COMPLETED (Today - Feb 4)
- [x] Baseline training: 812 iterations, loss 3.51
- [x] Checkpoint saved: iteration 800
- [x] Meeting with Ziyi: Approved expanded data
- [x] Created event_configs_full.yaml (12 tables)
- [x] Created mimic_full.yaml (14-stage pipeline)

---

### Phase 1: Setup & Configuration (4 hours)

**Day 1 - Tonight (Feb 4, Evening)**

**Task 1.1: Upload configs to HyperGator** (15 min)
```bash
# Copy new configs to HyperGator
scp configs/event_configs_full.yaml kolipakulak@hpg.rc.ufl.edu:/blue/yonghui.wu/kolipakulak/MEDS_polars_functions/
scp configs/mimic_full.yaml kolipakulak@hpg.rc.ufl.edu:/blue/yonghui.wu/kolipakulak/ethos-ares/src/ethos/configs/dataset/
```

**Task 1.2: Verify source data availability** (15 min)
```bash
# Check all 12 tables exist in MIMIC-IV
ssh kolipakulak@hpg.rc.ufl.edu
cd /blue/yonghui.wu/kolipakulak/mimiciv/3.1/

# Hosp tables
ls -lh hosp/admissions.csv
ls -lh hosp/diagnoses_icd.csv
ls -lh hosp/prescriptions.csv
ls -lh hosp/drgcodes.csv
ls -lh hosp/labevents.csv
ls -lh hosp/procedures_icd.csv
ls -lh hosp/services.csv

# ICU tables
ls -lh icu/icustays.csv
ls -lh icu/chartevents.csv
ls -lh icu/procedureevents.csv
ls -lh icu/inputevents.csv
```

**Task 1.3: Estimate data volume** (30 min)
```bash
# Get row counts
wc -l hosp/*.csv
wc -l icu/*.csv

# Check chartevents size (this is the big one)
du -h icu/chartevents.csv
# Expected: 30-40GB file

# Plan: Need to filter chartevents to essential vitals only
```

**Task 1.4: Code modifications** (3 hours)

**Modify 1: Revert base.py Q token hardcode**
```python
# File: /blue/yonghui.wu/kolipakulak/ethos-ares/src/ethos/datasets/base.py
# Line 30

# BEFORE (hardcoded):
self._num_quantiles = 10  # Fixed to 10 quantiles for age encoding

# AFTER (use vocab - Quantizator now generates these):
self._num_quantiles = len(self.vocab.quantile_stokens)
```

**Modify 2: Add chartevents filtering to mimic_full.yaml**
```yaml
# Already included in mimic_full.yaml - verify it's there
chart_processing:
  essential_vitals:
    - 220045  # Heart Rate
    - 220050  # Arterial BP systolic
    # etc.
```

**Modify 3: Update inference configs**
```bash
# Update inference configs to handle new vocabulary structure
# Files to check:
# - src/ethos/configs/inference_mortality.yaml
# - src/ethos/configs/inference_readmission.yaml
# etc.
```

---

### Phase 2: Data Extraction (6-8 hours)

**Day 2 (Feb 5)**

**Task 2.1: Launch MEDS extraction** (Setup: 30 min, Run: 6-8 hours)

```bash
#!/bin/bash
#SBATCH --job-name=meds_extract_full
#SBATCH --output=/blue/yonghui.wu/kolipakulak/ethos-ares/logs/meds_extract_full_%j.log
#SBATCH --error=/blue/yonghui.wu/kolipakulak/ethos-ares/logs/meds_extract_full_%j.err
#SBATCH --partition=hpg-default
#SBATCH --qos=yonghui.wu
#SBATCH --cpus-per-task=16
#SBATCH --mem=128gb
#SBATCH --time=12:00:00

module load conda
conda activate ethos-ares

MEDS_extract-convert_to_sharded_events \
    input_dir=/blue/yonghui.wu/kolipakulak/mimiciv/3.1/ \
    MEDS_cohort_dir=/blue/yonghui.wu/kolipakulak/mimic-meds-full \
    event_conversion_config_fp=/blue/yonghui.wu/kolipakulak/MEDS_polars_functions/event_configs_full.yaml \
    num_shards=100
```

**Expected Output:**
```
/blue/yonghui.wu/kolipakulak/mimic-meds-full/data/
├── train/
│   ├── patients.parquet
│   ├── admissions.parquet
│   ├── diagnoses_icd.parquet
│   ├── prescriptions.parquet
│   ├── drgcodes.parquet
│   ├── labevents.parquet         [NEW - ~10-20GB]
│   ├── procedures_icd.parquet     [NEW]
│   ├── services.parquet           [NEW]
│   ├── icustays.parquet           [NEW]
│   ├── chartevents.parquet        [NEW - LARGE, filtered]
│   ├── procedureevents.parquet    [NEW]
│   └── inputevents.parquet        [NEW]
└── test/
    └── (same structure)
```

**Monitoring:**
```bash
# Check extraction progress
tail -f /blue/yonghui.wu/kolipakulak/ethos-ares/logs/meds_extract_full_<JOBID>.err

# Expected time:
# - hosp tables: 2-3 hours
# - ICU tables: 4-5 hours (chartevents is slow)
# - Total: 6-8 hours
```

---

### Phase 3: Tokenization (4-6 hours)

**Day 2-3 (Feb 5, Evening or Feb 6 Morning)**

**Task 3.1: Tokenize training data** (Setup: 15 min, Run: 4-6 hours)

```bash
#!/bin/bash
#SBATCH --job-name=tokenize_full_train
#SBATCH --output=/blue/yonghui.wu/kolipakulak/ethos-ares/logs/tokenize_full_train_%j.log
#SBATCH --error=/blue/yonghui.wu/kolipakulak/ethos-ares/logs/tokenize_full_train_%j.err
#SBATCH --partition=hpg-default
#SBATCH --qos=yonghui.wu
#SBATCH --cpus-per-task=16
#SBATCH --mem=128gb
#SBATCH --time=08:00:00

module load conda
conda activate ethos-ares

MEDS_transform-runner \
    --multirun \
    worker="range(0,16)" \
    hydra/launcher=joblib \
    input_dir=/blue/yonghui.wu/kolipakulak/mimic-meds-full/data/train \
    cohort_dir=/blue/yonghui.wu/kolipakulak/ethos-ares/data/tokenized_datasets/mimic-full/train \
    stage_configs=/blue/yonghui.wu/kolipakulak/ethos-ares/src/ethos/configs/dataset/mimic_full.yaml
```

**Task 3.2: Tokenize test data** (Run: 1-2 hours)
```bash
# Same as above but:
# input_dir=.../mimic-meds-full/data/test
# cohort_dir=.../tokenized_datasets/mimic-full/test
```

**Expected Output:**
```
data/tokenized_datasets/mimic-full/
├── train/
│   ├── 0.safetensors - 16.safetensors  (may be more files)
│   ├── vocab_t50000.csv  (50-60K tokens)
│   ├── static_data.pickle
│   ├── interval_estimates.json
│   └── quantiles.json  [NEW - Quantizator output]
└── test/
    └── (same)
```

---

### Phase 4: Training Setup (1 hour)

**Day 3 (Feb 6)**

**Task 4.1: Verify tokenization output** (15 min)
```bash
# Check vocabulary size
wc -l data/tokenized_datasets/mimic-full/train/vocab_t*.csv
# Expected: 50,000-60,000

# Check safetensors files
ls -lh data/tokenized_datasets/mimic-full/train/*.safetensors

# Verify quantiles.json exists (for Q tokens)
cat data/tokenized_datasets/mimic-full/train/quantiles.json
```

**Task 4.2: Prepare training script** (30 min)

```bash
#!/bin/bash
#SBATCH --job-name=train_full_91k
#SBATCH --output=/blue/yonghui.wu/kolipakulak/ethos-ares/logs/train_full_91k_%j.log
#SBATCH --error=/blue/yonghui.wu/kolipakulak/ethos-ares/logs/train_full_91k_%j.err
#SBATCH --partition=hpg-gpu
#SBATCH --qos=yonghui.wu-b
#SBATCH --gres=gpu:a100:1  # Use A100 for faster training
#SBATCH --cpus-per-task=4
#SBATCH --mem=32gb
#SBATCH --time=24:00:00  # 24 hours for full run

module load conda
conda activate ethos-ares

torchrun --standalone --nproc_per_node=1 ethos_train \
    data_fp=/blue/yonghui.wu/kolipakulak/ethos-ares/data/tokenized_datasets/mimic-full/train \
    out_dir=/blue/yonghui.wu/kolipakulak/ethos-ares/models/full_91k_complete \
    val_size=0.1 \
    batch_size=16 \
    max_iters=10000 \
    eval_interval=100 \
    n_layer=4 \
    n_head=8 \
    n_embd=512 \
    wandb_log=false
```

**Task 4.3: Launch training** (15 min)
```bash
cd /blue/yonghui.wu/kolipakulak/ethos-ares
sbatch scripts/train_full_91k.sh

# Monitor
squeue -u $USER
tail -f logs/train_full_91k_<JOBID>.err
```

---

### Phase 5: Training & Monitoring (24-48 hours)

**Day 3-5 (Feb 6-8)**

**Training expectations:**
- **Iteration time:** 25-35 sec/iter (slightly slower due to larger vocab)
- **10,000 iterations:** ~72-96 hours (3-4 days)
- **Target for initial eval:** 2,000 iterations (~14-18 hours)
- **Checkpoints:** Every 100 iterations (100, 200, 300, ..., 2000)

**Monitoring checklist:**
```bash
# Every 4-6 hours, check:
squeue -u $USER
tail -50 logs/train_full_91k_<JOBID>.err | grep "step\|loss"

# Look for:
# - Loss decreasing steadily
# - No KeyErrors (vocab issues)
# - MFU > 5% (GPU utilization)
# - Checkpoints saving
```

**Early stopping criteria:**
- If loss < 3.0 by iteration 2000 → excellent
- If loss not decreasing after 500 iterations → investigate
- If KeyError/ValueError → vocab issue, need to fix

---

### Phase 6: Inference (12-16 hours)

**Day 5-6 (Feb 8-9)**

**Task 6.1: Run all 4 inference tasks in parallel**

```bash
# Launch all 4 tasks simultaneously
cd /blue/yonghui.wu/kolipakulak/ethos-ares

sbatch scripts/run_inference_mortality.sh
sbatch scripts/run_inference_readmission.sh  
sbatch scripts/run_inference_icu_admission.sh
sbatch scripts/run_inference_icu_mortality.sh

# Each runs 2-4 hours, all complete in ~4 hours (parallel)
```

**Task 6.2: Generate evaluation metrics** (2-3 hours)

```bash
# Use notebooks to calculate AUROC, AUPRC
jupyter lab  # or jupyter notebook

# Run:
# - notebooks/mortality.ipynb
# - notebooks/hosp_readmission.ipynb
# - notebooks/icu_admission.ipynb
# - notebooks/icu_mortality.ipynb (adapted)
```

---

## Complete Timeline Summary

| Phase | Task | Duration | Days | Status |
|-------|------|----------|------|--------|
| 0 | Baseline (completed) | - | Feb 4 | ✅ Done |
| 1 | Setup & config | 4 hours | Feb 4 PM | 📝 In progress |
| 2 | MEDS extraction | 6-8 hours | Feb 5 | ⏳ Pending |
| 3 | Tokenization | 4-6 hours | Feb 5-6 | ⏳ Pending |
| 4 | Training setup | 1 hour | Feb 6 | ⏳ Pending |
| 5 | Training (2000 iter) | 14-18 hours | Feb 6-7 | ⏳ Pending |
| 6 | Inference (all 4 tasks) | 4 hours | Feb 7-8 | ⏳ Pending |
| 7 | Evaluation metrics | 2-3 hours | Feb 8 | ⏳ Pending |

**Total time to results:** ~7 days (Feb 4 → Feb 11)  
**Aggressive timeline:** ~5 days if everything goes smoothly

---

## Resource Requirements

### Disk Space
- **MEDS extraction:** ~100-150GB (chartevents large)
- **Tokenization:** ~50-100GB
- **Model checkpoints:** ~40GB (100 checkpoints × 400MB)
- **Total needed:** ~200-300GB

### Compute Resources
- **Extraction:** 16 CPUs, 128GB RAM, 12 hours
- **Tokenization:** 16 CPUs, 128GB RAM, 8 hours
- **Training:** 1 A100 GPU, 4 CPUs, 32GB RAM, 24-48 hours
- **Inference:** 4 L4 GPUs (parallel), 4-6 hours each

### Cost Estimate (HyperGator SUs)
- **Extraction:** ~200 SUs
- **Tokenization:** ~150 SUs
- **Training:** ~1,000 SUs (A100 for 24 hours)
- **Inference:** ~200 SUs (4 L4 GPUs)
- **Total:** ~1,550 SUs

---

## Risk Mitigation

### Risk 1: chartevents too large
**Mitigation:** Filter to essential vitals only (already in config)  
**Backup:** If still too large, reduce vital types to top 5

### Risk 2: Training doesn't improve over baseline
**Mitigation:** Compare loss curves, check if new features used  
**Backup:** Tune learning rate, try different architecture

### Risk 3: Tokenization fails
**Mitigation:** Test on small subset first  
**Backup:** Debug stage-by-stage, skip problematic stages

### Risk 4: Time limit exceeded
**Mitigation:** Use 24-hour partition, checkpoint every 100 iterations  
**Backup:** Resume from latest checkpoint

---

## Success Criteria

### Minimum Viable:
- ✅ 12-table extraction completes without errors
- ✅ Tokenization generates 50-60K vocab
- ✅ Training reaches 2000 iterations
- ✅ All 4 inference tasks complete
- ✅ AUROC metrics calculated

### Ideal:
- ✅ Training loss < 3.0 by iteration 2000
- ✅ AUROC > 0.80 for all tasks
- ✅ ICU tasks show improvement over baseline
- ✅ No critical bugs or issues

---

## Next Immediate Actions (Tonight - Feb 4)

1. **Upload configs** (15 min)
2. **Verify source data** (15 min)  
3. **Modify base.py** (30 min)
4. **Test extraction on small sample** (1 hour)
5. **Launch full extraction overnight** (6-8 hours)

**Tomorrow morning (Feb 5):** Check extraction, launch tokenization

---

## Comparison: Baseline vs Full

| Metric | Baseline (5 tables) | Full (12 tables) | Improvement |
|--------|-------------------|------------------|-------------|
| Tables | 5 | 12 | +140% |
| Vocabulary | 39K tokens | 50-60K tokens | +50% |
| Events | 21M prescriptions | 50-100M total | +250% |
| Features | Basic | Comprehensive | Labs, vitals, ICU |
| ICU tasks | Inferred | Real data | Major upgrade |
| Timeline | Completed | ~7 days | - |

---

**Plan created:** February 4, 2026, 4:30 PM  
**Start date:** February 4, 2026 (tonight)  
**Target completion:** February 11, 2026  
**Status:** Ready to begin Phase 1
