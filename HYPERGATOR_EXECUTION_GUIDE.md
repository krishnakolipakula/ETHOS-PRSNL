# HYPERGATOR EXECUTION PLAN - Ziyi's Approved Features

**Date:** February 3, 2026  
**Goal:** Train ETHOS-ARES model on HyperGator with Ziyi's approved features  
**Location:** `/orange/yonghui.wu/chenziyi/MIMIC/mimiciv/3.1/`

---

## 📊 **CURRENT DATA STATUS**

### **Local Mac (Sample Data - 395 patients):**
```
data/mimic_sample/hosp/
├── patients_sample.csv.gz (3.5K) - ✅ HAS: gender, dod
├── admissions_sample.csv.gz (37K) - ✅ HAS: admit/discharge times, race, insurance, language
├── diagnoses_icd_sample.csv.gz (62K) - ✅ HAS: ICD codes
├── procedures_icd_sample.csv.gz (14K) - ❌ NOT NEEDED (Ziyi excluded)

data/mimic_sample/icu/
├── icustays_sample.csv.gz - ❌ NOT NEEDED (Ziyi excluded)
```

### **MISSING on Local Mac:**
- ❌ **prescriptions** - NOT in sample (Ziyi wants this)
- ❌ **drgcodes** - NOT in sample (Ziyi wants this)

### **HyperGator (Full Dataset - ~300K patients):**
**Location:** `/orange/yonghui.wu/chenziyi/MIMIC/mimiciv/3.1/hosp/`

**Available Files (from Ziyi's folder):**
```
✅ patients.csv.gz (5.89 MB) - gender, dod
✅ admissions.csv.gz (76.15 MB) - admit/discharge times
✅ diagnoses_icd.csv.gz (267.43 MB) - ICD diagnosis codes
✅ prescriptions.csv.gz (1.19 GB) - MEDICATION DATA (NEED THIS!)
✅ drgcodes.csv.gz (9.74 MB) - DRG codes (NEED THIS!)

❌ procedures_icd.csv.gz - Excluded by Ziyi
❌ labevents.csv.gz - Excluded by Ziyi
❌ emar.csv.gz - Excluded by Ziyi
❌ pharmacy.csv.gz - Excluded by Ziyi
❌ transfers.csv.gz - Excluded by Ziyi
```

---

## 🎯 **EXECUTION PLAN ON HYPERGATOR**

### **PHASE 1: Setup & Data Access**

**Step 1: Login to HyperGator**
```bash
ssh <your_username>@hpg.rc.ufl.edu
```

**Step 2: Navigate to Your Working Directory**
```bash
cd /blue/yonghui.wu/<your_username>/ethos-ares
# OR create new directory
mkdir -p /blue/yonghui.wu/<your_username>/ethos-ares
cd /blue/yonghui.wu/<your_username>/ethos-ares
```

**Step 3: Copy ETHOS-ARES Code**
```bash
# Option A: Git clone (if repo exists)
git clone <repo_url> .

# Option B: Transfer from local Mac
# On Mac terminal:
scp -r /Users/kkc/Downloads/ethos-ares-master/ethos-ares-master/* \
  <username>@hpg.rc.ufl.edu:/blue/yonghui.wu/<username>/ethos-ares/
```

---

### **PHASE 2: Create Symlinks to Ziyi's Data**

**Step 4: Create Data Directory Structure**
```bash
cd /blue/yonghui.wu/<your_username>/ethos-ares
mkdir -p data/mimic-iv/hosp
```

**Step 5: Symlink Approved Tables Only (Ziyi's RED features)**
```bash
# Link to Ziyi's MIMIC-IV data folder
ZIYI_DATA="/orange/yonghui.wu/chenziyi/MIMIC/mimiciv/3.1/hosp"

# Core tables
ln -s ${ZIYI_DATA}/patients.csv.gz data/mimic-iv/hosp/
ln -s ${ZIYI_DATA}/admissions.csv.gz data/mimic-iv/hosp/

# Diagnosis codes (Ziyi approved)
ln -s ${ZIYI_DATA}/diagnoses_icd.csv.gz data/mimic-iv/hosp/

# Medications (Ziyi approved - NEW!)
ln -s ${ZIYI_DATA}/prescriptions.csv.gz data/mimic-iv/hosp/

# DRG codes (Ziyi approved - NEW!)
ln -s ${ZIYI_DATA}/drgcodes.csv.gz data/mimic-iv/hosp/

# Dictionary tables (for metadata)
ln -s ${ZIYI_DATA}/d_icd_diagnoses.csv.gz data/mimic-iv/hosp/
ln -s ${ZIYI_DATA}/d_icd_procedures.csv.gz data/mimic-iv/hosp/

# Verify symlinks
ls -lh data/mimic-iv/hosp/
```

**Expected Output:**
```
patients.csv.gz -> /orange/yonghui.wu/chenziyi/MIMIC/mimiciv/3.1/hosp/patients.csv.gz (5.89 MB)
admissions.csv.gz -> ... (76.15 MB)
diagnoses_icd.csv.gz -> ... (267.43 MB)
prescriptions.csv.gz -> ... (1.19 GB)
drgcodes.csv.gz -> ... (9.74 MB)
```

---

### **PHASE 3: Update Configuration Files**

**Step 6: Create Ziyi-Approved event_configs.yaml**
```bash
cd scripts/meds/mimic/configs/
cp event_configs.yaml event_configs-ziyi.yaml
nano event_configs-ziyi.yaml  # Or vim
```

**Step 7: Modify event_configs-ziyi.yaml**

**Changes to make:**

1. **ADD prescriptions configuration** (new section):
```yaml
hosp/prescriptions:
  medication_start:
    code:
      - MEDICATION
      - col(drug)
      - col(route)
    time: col(starttime)
    time_format: 
      - "%Y-%m-%d %H:%M:%S"
      - "%Y-%m-%d"
    hadm_id: hadm_id
    pharmacy_id: pharmacy_id
    dose_val_rx: dose_val_rx
    dose_unit_rx: dose_unit_rx
    drug_type: drug_type
  medication_stop:
    code:
      - MEDICATION
      - STOP
      - col(drug)
    time: col(stoptime)
    time_format: 
      - "%Y-%m-%d %H:%M:%S"
      - "%Y-%m-%d"
    hadm_id: hadm_id
    pharmacy_id: pharmacy_id
```

2. **MODIFY drgcodes** (remove data leakage):
```yaml
hosp/drgcodes:
  drg:
    code:
      - DRG
      - col(drg_type)
      - col(drg_code)
      - col(description)
    hadm_id: hadm_id
    time: col(dischtime)
    time_format: "%Y-%m-%d %H:%M:%S"
    # REMOVED: drg_severity and drg_mortality (data leakage!)
```

3. **REMOVE/COMMENT OUT** these sections:
```yaml
# hosp/procedures_icd:  # Excluded by Ziyi
# hosp/emar:  # Excluded by Ziyi
# hosp/labevents:  # Excluded by Ziyi
# hosp/transfers:  # Excluded by Ziyi
# icu/icustays:  # Excluded by Ziyi
```

**Step 8: (Optional) Remove Bias Features from admissions**
If we want to exclude race, insurance, language:
```yaml
hosp/admissions:
  admission:
    code:
      - HOSPITAL_ADMISSION
      - col(admission_type)
      - col(admission_location)
    time: col(admittime)
    time_format: "%Y-%m-%d %H:%M:%S"
    # REMOVED: race, insurance, language
    marital_status: marital_status
    hadm_id: hadm_id
```

---

### **PHASE 4: Setup Python Environment on HyperGator**

**Step 9: Load Modules & Create Conda Environment**
```bash
# Load Python and CUDA
module load conda
module load cuda/11.8

# Create environment
conda create -n ethos-ares python=3.12 -y
conda activate ethos-ares

# Install PyTorch with CUDA support
pip install torch==2.10.0 torchvision==0.25.0 torchaudio==2.10.0 \
  --index-url https://download.pytorch.org/whl/cu118

# Install ETHOS package
cd /blue/yonghui.wu/<username>/ethos-ares
pip install -e .

# Install additional dependencies
pip install pandas scikit-learn polars safetensors
```

**Step 10: Verify Installation**
```bash
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA:', torch.cuda.is_available())"
```

---

### **PHASE 5: Data Extraction with MEDS**

**Step 11: Create SLURM Job Script for MEDS Extraction**
```bash
nano scripts/meds/run_mimic_ziyi.sh
```

**File: `run_mimic_ziyi.sh`**
```bash
#!/bin/bash
#SBATCH --job-name=meds_extract_ziyi
#SBATCH --output=logs/meds_extract_%j.log
#SBATCH --error=logs/meds_extract_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64GB
#SBATCH --time=24:00:00
#SBATCH --partition=gpu
#SBATCH --gpus=1

# Load environment
module load conda
conda activate ethos-ares

# Set paths
INPUT_DIR="/blue/yonghui.wu/<username>/ethos-ares/data/mimic-iv"
OUTPUT_DIR="/blue/yonghui.wu/<username>/ethos-ares/data/mimic-meds-ziyi"
CONFIG_FILE="scripts/meds/mimic/configs/event_configs-ziyi.yaml"

# Run MEDS extraction
echo "Starting MEDS extraction with Ziyi's approved features..."
echo "Input: ${INPUT_DIR}"
echo "Output: ${OUTPUT_DIR}"
echo "Config: ${CONFIG_FILE}"

# Extract events
MEDS_extract-convert_to_sharded_events \
  --input_dir ${INPUT_DIR} \
  --output_dir ${OUTPUT_DIR} \
  --event_configs ${CONFIG_FILE} \
  --num_workers 16

echo "MEDS extraction complete!"
```

**Step 12: Submit MEDS Extraction Job**
```bash
mkdir -p logs
sbatch scripts/meds/run_mimic_ziyi.sh

# Monitor job
squeue -u <username>
tail -f logs/meds_extract_*.log
```

**Expected Runtime:** 4-8 hours for ~300K patients

---

### **PHASE 6: Tokenization**

**Step 13: Create Tokenization Script**
```bash
nano scripts/run_tokenization_ziyi.sh
```

**File: `run_tokenization_ziyi.sh`**
```bash
#!/bin/bash
#SBATCH --job-name=tokenize_ziyi
#SBATCH --output=logs/tokenize_%j.log
#SBATCH --error=logs/tokenize_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32GB
#SBATCH --time=12:00:00

module load conda
conda activate ethos-ares

python tensorize_data.py \
  --input_dir data/mimic-meds-ziyi \
  --output_dir data/tokenized-ziyi \
  --vocab_size 1000 \
  --max_seq_len 2048

echo "Tokenization complete!"
```

**Step 14: Submit Tokenization Job**
```bash
sbatch scripts/run_tokenization_ziyi.sh
```

**Expected Vocabulary Size:** 300-500 tokens (vs 72 in sample)

---

### **PHASE 7: Model Training**

**Step 15: Create Training Configuration**
```bash
nano src/ethos/configs/train_ziyi.yaml
```

**File: `train_ziyi.yaml`**
```yaml
# Dataset
data_dir: data/tokenized-ziyi/mimic
train_split: train
val_split: test

# Model architecture
n_layer: 4  # Increase from 2 (more data = bigger model)
n_head: 8   # Increase from 4
n_embd: 256 # Increase from 128

# Training
batch_size: 16
max_iters: 50000  # Increase from 5000
learning_rate: 3e-4
eval_interval: 1000
eval_iters: 100

# Hardware
device: cuda
compile: true

# Output
out_dir: out/ziyi_model
```

**Step 16: Create Training Job Script**
```bash
nano scripts/run_training_ziyi.sh
```

**File: `run_training_ziyi.sh`**
```bash
#!/bin/bash
#SBATCH --job-name=train_ziyi
#SBATCH --output=logs/train_%j.log
#SBATCH --error=logs/train_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64GB
#SBATCH --time=48:00:00
#SBATCH --partition=gpu
#SBATCH --gpus=a100:1  # Request A100 GPU

module load conda
conda activate ethos-ares

python -m ethos.train.run_training \
  --config src/ethos/configs/train_ziyi.yaml

echo "Training complete!"
```

**Step 17: Submit Training Job**
```bash
sbatch scripts/run_training_ziyi.sh

# Monitor training
tail -f logs/train_*.log
```

**Expected Runtime:** 24-48 hours on A100 GPU

---

### **PHASE 8: Inference**

**Step 18: Run Inference**
```bash
#!/bin/bash
#SBATCH --job-name=inference_ziyi
#SBATCH --output=logs/inference_%j.log
#SBATCH --mem=32GB
#SBATCH --time=04:00:00
#SBATCH --partition=gpu
#SBATCH --gpus=1

module load conda
conda activate ethos-ares

python -m ethos.inference.run_inference \
  --model_dir out/ziyi_model \
  --data_dir data/tokenized-ziyi/mimic \
  --output_dir results/ziyi_predictions \
  --task ICU_MORTALITY \
  --device cuda

echo "Inference complete!"
```

**Step 19: Analyze Results**
```bash
python analyze_results.py \
  --results_dir results/ziyi_predictions \
  --output_file results/ziyi_accuracy.txt
```

---

## 📋 **COMPLETE EXECUTION CHECKLIST**

### **Setup Phase:**
- [ ] Login to HyperGator
- [ ] Create working directory `/blue/yonghui.wu/<username>/ethos-ares`
- [ ] Transfer ETHOS-ARES code to HyperGator
- [ ] Create symlinks to Ziyi's MIMIC data (5 approved tables)
- [ ] Verify symlinks point to correct files

### **Configuration Phase:**
- [ ] Create `event_configs-ziyi.yaml`
- [ ] Add `hosp/prescriptions` configuration
- [ ] Modify `hosp/drgcodes` (remove drg_mortality/severity)
- [ ] Remove excluded tables (procedures_icd, labevents, emar, transfers, icu)
- [ ] (Optional) Remove bias features (race, insurance, language)

### **Environment Phase:**
- [ ] Load conda module
- [ ] Create conda environment with Python 3.12
- [ ] Install PyTorch with CUDA support
- [ ] Install ETHOS package in development mode
- [ ] Verify CUDA availability

### **Extraction Phase:**
- [ ] Create SLURM script `run_mimic_ziyi.sh`
- [ ] Submit MEDS extraction job
- [ ] Monitor progress (4-8 hours)
- [ ] Verify output files created

### **Tokenization Phase:**
- [ ] Create tokenization script
- [ ] Submit tokenization job
- [ ] Verify vocabulary size (~300-500 tokens)
- [ ] Check safetensors files created

### **Training Phase:**
- [ ] Create training config `train_ziyi.yaml`
- [ ] Create training script `run_training_ziyi.sh`
- [ ] Submit training job (24-48 hours)
- [ ] Monitor loss convergence
- [ ] Verify checkpoint files saved

### **Inference Phase:**
- [ ] Create inference script
- [ ] Run inference on test set
- [ ] Generate predictions
- [ ] Calculate accuracy metrics

### **Validation Phase:**
- [ ] Verify no data leakage (drg_mortality excluded)
- [ ] Check predictions are reasonable
- [ ] Report accuracy to Ziyi
- [ ] Document results

---

## 🚨 **IMPORTANT NOTES**

### **Data Leakage Prevention:**
1. **drg_mortality and drg_severity** - Removed from configuration
2. **discharge_location = DIED** - Keep but use as TARGET only
3. **MEDS_DEATH token** - Use as TARGET, not input feature
4. **Verify in preprocessors** that death events don't leak into input

### **Expected Performance:**
- **Sample (395 patients):** 7-28% accuracy (high variance)
- **Full dataset (300K patients):** 50-70% accuracy (more stable)

### **Storage Requirements:**
- Raw data: ~1.5 GB (5 compressed tables)
- MEDS output: ~5-10 GB
- Tokenized data: ~2-3 GB
- Model checkpoints: ~50-100 MB per checkpoint
- **Total:** ~10-15 GB

### **Compute Requirements:**
- MEDS extraction: 16 CPU cores, 64 GB RAM, 4-8 hours
- Tokenization: 8 CPU cores, 32 GB RAM, 2-4 hours
- Training: 1 A100 GPU, 64 GB RAM, 24-48 hours
- Inference: 1 GPU, 32 GB RAM, 1-2 hours

---

## 🎯 **READY TO START?**

**Commands to begin:**
```bash
# 1. Login
ssh <username>@hpg.rc.ufl.edu

# 2. Setup
cd /blue/yonghui.wu/<username>
mkdir -p ethos-ares
cd ethos-ares

# 3. Transfer code (from Mac)
# scp -r /Users/kkc/Downloads/ethos-ares-master/ethos-ares-master/* \
#   <username>@hpg.rc.ufl.edu:/blue/yonghui.wu/<username>/ethos-ares/

# 4. Begin setup
module load conda
conda create -n ethos-ares python=3.12 -y
```

**Need HyperGator credentials?** Contact your PI or check UF Research Computing docs.
