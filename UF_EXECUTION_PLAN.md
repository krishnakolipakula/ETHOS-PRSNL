# UF Data Execution Plan

## ✅ Phase 1: Converter Development (COMPLETE)

**Status:** Converter ready with time interval quantization

**What was implemented:**
- Time interval bins: 0-1day, 1-7day, 7-30day, 30-365day, 1-2year, 2+year
- Conversion from triplets [patient_id, age_days, code] to sequences
- Output format: [demographics, TIME_TOKEN, codes, TIME_TOKEN, codes, ...]
- Vocabulary expansion: 28,572 → 28,578 tokens
- .safetensors sharded output

**Files created:**
- `convert_uf_to_ethos_format.py` - Main converter
- `test_converter.py` - Test script (validated with sample patient)
- `CONVERTER_README.md` - Documentation
- `scripts/run_conversion.sh` - SLURM job script

**Test results:**
```
Patient 11: 8 triplets → 11-token sequence
[Healthy, M, TIME_2+YEAR, Z20822, 4280, TIME_30-365DAY, 3899, TIME_1-2YEAR, 41401]
```

---

## 🔄 Phase 2: Run Conversion on HyperGator (NEXT)

### Step 1: Pull updated code
```bash
ssh kkc@hpg.rc.ufl.edu
cd /blue/yonghui.wu/kolipakulak/ethos-ares
git pull origin main
```

### Step 2: Create logs directory
```bash
mkdir -p logs
```

### Step 3: Submit conversion job
```bash
sbatch scripts/run_conversion.sh
```

### Step 4: Monitor progress
```bash
# Check job status
squeue -u kkc

# Watch output in real-time
tail -f logs/convert_uf_*.out

# Check for errors
tail -f logs/convert_uf_*.err
```

### Expected Output Structure:
```
data/tokenized/uf_converted/
├── train/
│   ├── 0.safetensors (10,000 sequences)
│   ├── 1.safetensors
│   └── 13.safetensors (total ~134K patients)
├── val/
│   ├── 0.safetensors
│   └── 4.safetensors (~45K patients)
├── test/
│   ├── 0.safetensors
│   └── 4.safetensors (~45K patients)
├── metadata.json
└── vocabulary.csv (28,578 tokens)
```

### Expected Runtime:
- Train split: ~30-45 minutes (133,974 patients)
- Val split: ~10-15 minutes (44,658 patients)
- Test split: ~10-15 minutes (44,658 patients)
- **Total: 1-1.5 hours**

---

## 🔄 Phase 3: Update Training Config (AFTER CONVERSION)

### Step 1: Create UF-specific config
```bash
cp configs/mimic_full.yaml configs/uf_full.yaml
```

### Step 2: Update config file
Edit `configs/uf_full.yaml`:

```yaml
# Data paths
train_data_path: "data/tokenized/uf_converted/train"
val_data_path: "data/tokenized/uf_converted/val"

# Vocabulary
vocab_size: 28578  # Updated: 28,572 + 6 time tokens

# Model architecture (keep same as MIMIC-IV)
n_layer: 6
n_embd: 768
n_head: 12
dropout: 0.3

# Training
max_iters: 5000  # Start with 5K iterations
batch_size: 32
gradient_accumulation_steps: 8
learning_rate: 0.0006
min_lr: 0.00001

# Data
block_size: 2048
```

### Step 3: Create training script
```bash
cp scripts/run_training.sh scripts/run_training_uf.sh
```

Edit `scripts/run_training_uf.sh`:
```bash
# Change config path
--config configs/uf_full.yaml \
--output_dir outputs/$(date +%Y-%m-%d)/uf_training \
```

---

## 🔄 Phase 4: Train Model (AFTER CONFIG UPDATE)

### Submit training job:
```bash
sbatch scripts/run_training_uf.sh
```

### Monitor training:
```bash
tail -f logs/train_uf_*.out
```

### Expected metrics:
- Initial loss: ~7-8 (random)
- Final loss: ~0.6-0.7 (after 5K iters)
- Training time: 2-3 hours (1x L4 GPU)

---

## 🔄 Phase 5: Create Task Dataset (AFTER TRAINING)

We need to define the prediction task for UF data. Options:

**Option A: Mortality Prediction**
- Label: Death outcome in vocabulary
- Prediction window: 30-day or in-hospital

**Option B: Readmission Prediction**
- Label: Based on time gaps between encounters
- Prediction window: 30-day readmission

**Option C: Disease Onset Prediction**
- Label: Specific ICD codes (e.g., diabetes 25000)
- Prediction window: Future diagnosis

**Decision needed:** Ask Ziyi what task to predict!

Placeholder script structure:
```python
# scripts/create_uf_task_dataset.py
# TODO: Define based on Ziyi's requirements
```

---

## 🔄 Phase 6: Run Inference (AFTER TASK DATASET)

### Create inference script:
```bash
cp scripts/run_inference.sh scripts/run_inference_uf.sh
```

### Update paths:
```bash
--model_path outputs/.../uf_training/final_model.pt \
--test_data_path data/tokenized/uf_converted/test \
--task_data_path data/tasks/uf_TASKNAME/test.parquet \
--output_file results/UF_TASKNAME/predictions.csv
```

### Submit job:
```bash
sbatch scripts/run_inference_uf.sh
```

### Calculate AUROC:
```python
python analyze_results.py --task UF_TASKNAME
```

---

## 📊 Expected Timeline

| Phase | Task | Duration | Status |
|-------|------|----------|--------|
| 1 | Converter development | 2 hours | ✅ COMPLETE |
| 2 | Run conversion | 1-1.5 hours | ⏳ READY |
| 3 | Update config | 15 minutes | ⏳ WAITING |
| 4 | Train model (5K iters) | 2-3 hours | ⏳ WAITING |
| 5 | Create task dataset | 1 hour | ⏳ NEED TASK DEFINITION |
| 6 | Run inference | 1-2 hours | ⏳ WAITING |
| 7 | Calculate metrics | 15 minutes | ⏳ WAITING |

**Total time to first results: 6-8 hours** (if run sequentially)

---

## 🎯 Success Criteria

**Conversion success:**
- ✅ All 3 splits converted
- ✅ Vocabulary saved (28,578 tokens)
- ✅ Metadata shows correct stats
- ✅ No errors in logs

**Training success:**
- ✅ Loss converges below 1.0
- ✅ No overfitting (train/val loss similar)
- ✅ Model checkpoint saved

**Inference success:**
- ✅ AUROC > 0.60 (baseline)
- ✅ Predictions align with outcomes
- ✅ No NaN values in results

---

## 🚀 Next Immediate Action

**Run conversion on HyperGator:**
```bash
ssh kkc@hpg.rc.ufl.edu
cd /blue/yonghui.wu/kolipakulak/ethos-ares
git pull origin main
mkdir -p logs
sbatch scripts/run_conversion.sh
```

Monitor with:
```bash
watch -n 10 'squeue -u kkc; echo ""; tail -n 20 logs/convert_uf_*.out'
```

---

## 📝 Notes

**Key differences from MIMIC-IV:**
- UF vocab: 28,578 (vs MIMIC-IV ~50K)
- Only diagnoses (no meds/labs/vitals)
- Longer patient histories (avg 30 encounters vs ~15)
- Task definition TBD (need Ziyi's input)

**Real UF data status:**
- Sample data: Being used now
- Real data: Expected "next week" from Ziyi (as of Feb 18)
- Format: Should be identical to sample (triplets)

**Questions for Ziyi:**
1. What is the prediction task? (mortality/readmission/disease onset)
2. What is the outcome label in the data?
3. When will real UF data arrive?
4. Should we use ensemble models (rep_num > 1)?
