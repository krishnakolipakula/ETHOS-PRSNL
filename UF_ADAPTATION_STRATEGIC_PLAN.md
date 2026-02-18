# ETHOS-ARES Pipeline: Strategic Plan for UF Data Adaptation

**Date Created:** January 24, 2026  
**Project:** Adapting ETHOS-ARES from MIMIC-IV to UF Data  
**Current Status:** Initial exploration phase with MIMIC data

---

## 📋 Executive Summary

This document provides a comprehensive strategic plan for understanding the ETHOS-ARES pipeline using MIMIC data and preparing for UF (University of Florida) data adaptation. The pipeline consists of 3 main stages: **Data Preprocessing → Model Training → Inference/Prediction**.

---

## 🎯 Project Objectives

1. **Short-term (Local Experimentation):**
   - Understand ETHOS-ARES pipeline with small MIMIC dataset
   - Run all pipeline stages successfully on local machine
   - Document the workflow and identify adaptation points for UF data

2. **Long-term (Production on HyperGator):**
   - Scale to full dataset on HyperGator cluster
   - Adapt pipeline for UF Health EHR data
   - Train and evaluate models for UF-specific prediction tasks

---

## 🏗️ Pipeline Architecture Overview

### **Stage 1: Data Extraction & Preprocessing (MEDS Format)**
```
Raw EHR Data → MEDS Extraction → MEDS Format → Ready for Tokenization
```

### **Stage 2: Tokenization**
```
MEDS Data → Tokenization → Patient Health Timelines (PHT) → Ready for Training
```

### **Stage 3: Model Training**
```
Tokenized Data → GPT-2 Model Training → Trained Model Checkpoints
```

### **Stage 4: Inference & Evaluation**
```
Trained Model + Test Data → Zero-shot Prediction → Results Analysis
```

---

## 📊 Current Repository Structure

```
ethos-ares-master/
├── scripts/                    # Shell scripts for running pipeline
│   ├── meds/                  # MEDS data extraction scripts
│   │   ├── run_mimic.sh      # Main MEDS extraction script
│   │   └── mimic/            # MIMIC-specific configs
│   ├── run_tokenization.sh   # Tokenization script
│   ├── run_training.sh       # Model training script
│   └── run_inference.sh      # Inference script
├── src/ethos/
│   ├── tokenize/             # Tokenization logic
│   ├── train/                # Training logic
│   ├── inference/            # Inference logic
│   ├── datasets/             # Dataset classes (MIMIC-specific)
│   └── configs/              # Hydra configuration files
├── notebooks/                 # Analysis notebooks
└── results/                  # Output results directory
```

---

## 🚀 Phase 1: Local Experimentation with MIMIC Data (Weeks 1-3)

### **Step 1.1: Environment Setup** ⚙️

**Goal:** Install dependencies and verify environment

**Actions:**
```bash
# 1. Create conda environment
conda create --name ethos python=3.12
conda activate ethos

# 2. Install ETHOS package
cd c:\Users\Krishna\OneDrive\Desktop\UF\RA\ETHOS\ethos-ares-master
pip install -e .[jupyter]

# 3. Verify installation
ethos_tokenize --help
ethos_train --help
ethos_infer --help
```

**Success Criteria:**
- ✅ All dependencies installed without errors
- ✅ Three CLI commands are accessible
- ✅ No import errors when running Python

**Time Estimate:** 1-2 hours

---

### **Step 1.2: Obtain MIMIC-IV Dataset** 📦

**Goal:** Download and prepare a small subset of MIMIC-IV data

**Requirements:**
- PhysioNet account with MIMIC-IV access
- MIMIC-IV v2.2 (or compatible version)
- Optional: MIMIC-IV-ED extension

**Actions:**
1. Download MIMIC-IV from PhysioNet (https://physionet.org/content/mimiciv/)
2. Extract to a local directory (e.g., `D:\MIMIC-IV\`)
3. For local testing, consider creating a small subset:
   - Select first 1000-5000 patients
   - Copy relevant CSV files to a test directory

**Data Structure Expected:**
```
MIMIC-IV/
├── hosp/
│   ├── admissions.csv
│   ├── diagnoses_icd.csv
│   ├── labevents.csv
│   └── ...
├── icu/
│   ├── icustays.csv
│   └── ...
└── ed/ (optional)
    └── ...
```

**Success Criteria:**
- ✅ MIMIC-IV data downloaded and accessible
- ✅ Directory structure matches expected format

**Time Estimate:** 2-4 hours (depending on download speed)

---

### **Step 1.3: MEDS Extraction (Data Preprocessing)** 🔄

**Goal:** Convert raw MIMIC CSV files to MEDS format

**What is MEDS?**
- Medical Event Data Standard - a standardized format for EHR time-series data
- Makes data interoperable between different EHR systems
- ETHOS uses MEDS as an intermediate representation

**Configuration Files:**
- `scripts/meds/mimic/configs/extract_MIMIC.yaml` - Main extraction config
- `scripts/meds/mimic/configs/event_configs.yaml` - Event definitions

**Key Configuration Parameters to Understand:**
```yaml
# In extract_MIMIC.yaml
split_fracs:
  train: 0.9        # 90% for training
  test: 0.1         # 10% for testing
  tuning: null
  held_out: null
```

**Actions:**
```bash
# Set environment variables
export N_WORKERS=2  # Reduce for local testing (default: 7 requires 250GB RAM)
export MIMIC_IV_DIR="D:/MIMIC-IV"  # Your MIMIC directory
export OUTPUT_DIR="data"  # Project data directory

# Create output directory
mkdir -p data

# Run MEDS extraction (without ED extension for simplicity)
cd scripts/meds
bash run_mimic.sh \
    "$MIMIC_IV_DIR" \
    "../../data/mimic-2.2-premeds" \
    "../../data/mimic-2.2-meds" \
    ""
```

**Expected Output:**
```
data/
└── mimic-2.2-meds/
    ├── data/
    │   ├── train/
    │   │   ├── 0.parquet
    │   │   ├── 1.parquet
    │   │   └── ...
    │   └── test/
    │       └── *.parquet
    └── metadata/
        └── subject_splits.parquet
```

**Success Criteria:**
- ✅ MEDS parquet files created in output directory
- ✅ Train/test splits generated
- ✅ No errors during extraction

**Common Issues & Solutions:**
- **Memory Error:** Reduce N_WORKERS to 1-2
- **Missing Files:** Verify MIMIC directory structure
- **Encoding Issues:** Check CSV files are UTF-8 encoded

**Time Estimate:** 2-6 hours (depending on data size and workers)

---

### **Step 1.4: Tokenization** 🔤

**Goal:** Convert MEDS data into tokenized Patient Health Timelines (PHT)

**What Happens During Tokenization?**
1. Medical codes are mapped to tokens (diagnoses, procedures, labs, etc.)
2. Numeric values are quantized (e.g., lab values → discrete bins)
3. Time intervals between events are encoded
4. Patient demographics are added as context
5. A vocabulary is built from training data

**Configuration Files:**
- `src/ethos/configs/tokenization.yaml` - Tokenization settings
- `src/ethos/configs/dataset/mimic.yaml` - MIMIC-specific preprocessing

**Key Configuration Parameters:**
```yaml
# In tokenization.yaml
num_quantiles: 10           # Number of bins for numeric values
time_intervals_spec:        # Time interval encoding
  5m-15m: {minutes: 5}
  1d-2d: {days: 1}
  # ... etc
```

**Actions:**
```bash
# Navigate to project root
cd c:\Users\Krishna\OneDrive\Desktop\UF\RA\ETHOS\ethos-ares-master

# For Windows PowerShell, adapt the script:
# Instead of running bash scripts, use the commands directly

# Tokenize TRAINING data (builds vocabulary)
ethos_tokenize -m worker='range(0,2)' \
    input_dir=data/mimic-2.2-meds/data/train \
    output_dir=data/tokenized_datasets/mimic \
    out_fn=train

# Tokenize TEST data (uses training vocabulary)
ethos_tokenize -m worker='range(0,2)' \
    input_dir=data/mimic-2.2-meds/data/test \
    vocab=data/tokenized_datasets/mimic/train \
    output_dir=data/tokenized_datasets/mimic \
    out_fn=test
```

**Expected Output:**
```
data/tokenized_datasets/mimic/
├── train/
│   ├── shard_0.safetensors
│   ├── shard_1.safetensors
│   ├── vocab.json
│   ├── code_counts.csv
│   ├── quantiles.json
│   └── static_data.pickle
└── test/
    ├── shard_0.safetensors
    └── ...
```

**Understanding the Outputs:**
- **vocab.json:** Token vocabulary mapping
- **code_counts.csv:** Frequency of each medical code
- **quantiles.json:** Quantization thresholds for numeric values
- **static_data.pickle:** Patient demographics
- **shard_*.safetensors:** Tokenized patient timelines

**Success Criteria:**
- ✅ Training vocabulary created
- ✅ All data shards generated
- ✅ Token count > 0 in all shards

**Time Estimate:** 1-3 hours (for subset), 4-12 hours (for full data)

---

### **Step 1.5: Model Training** 🧠

**Goal:** Train a GPT-2 based EHR foundation model

**Model Architecture:**
- Base: GPT-2 decoder-only transformer
- Default config (small model for testing):
  - Layers: 6
  - Heads: 12
  - Embedding dimension: 768
  - Context length: 2048 tokens

**Configuration Files:**
- `src/ethos/configs/training.yaml` - Training hyperparameters
- `scripts/run_training.sh` - Training script

**Key Training Parameters:**
```yaml
# Key parameters to adjust for local testing
batch_size: 32              # Reduce to 8-16 for local GPU
n_positions: 2048           # Context window
n_layer: 6                  # Model depth
n_embd: 768                # Embedding size
max_iters: 100000          # Reduce to 1000 for quick testing
learning_rate: 0.0006
device: "cuda"             # Use "cpu" if no GPU
```

**Actions for Local Testing (CPU/Single GPU):**

```bash
# For SMALL TEST RUN (1000 iterations, ~30 min)
ethos_train \
    data_fp=data/tokenized_datasets/mimic/train \
    val_size=1 \
    batch_size=8 \
    max_iters=1000 \
    n_layer=2 \
    n_head=4 \
    n_embd=128 \
    device=cuda \
    out_dir=data/models/test_run

# For FULL TRAINING (if you have good GPU)
ethos_train \
    data_fp=data/tokenized_datasets/mimic/train \
    val_size=6 \
    batch_size=32 \
    max_epochs=300 \
    n_layer=6 \
    n_head=12 \
    n_embd=768 \
    device=cuda \
    out_dir=data/models/full_model
```

**Expected Output:**
```
data/models/test_run/
├── best_model.pt           # Best model checkpoint
├── recent_model.pt         # Latest model checkpoint
├── config.yaml             # Training configuration
└── training.log            # Training logs
```

**Monitoring Training:**
- Watch loss decrease over iterations
- Check validation loss periodically
- Expected: Training loss should decrease from ~8-10 to ~3-4

**Success Criteria:**
- ✅ Model trains without errors
- ✅ Loss decreases over time
- ✅ Model checkpoints saved

**Time Estimate:** 
- Test run: 30 minutes - 1 hour
- Full training: 12-72 hours (depending on hardware)

**Note:** For serious training, consider using HyperGator with multiple GPUs.

---

### **Step 1.6: Inference & Evaluation** 🎯

**Goal:** Run predictions on test data and evaluate performance

**Available Tasks:**
1. **Hospital Mortality** - Predict in-hospital death
2. **ICU Admission** - Predict ICU admission within 24 hours
3. **30-day Readmission** - Predict hospital readmission
4. **Prolonged Length of Stay** - Predict extended hospital stay
5. **ED Discharge** - Predict emergency department outcomes

**How Zero-shot Prediction Works:**
1. Model receives patient history up to a time point
2. Model generates future health trajectory (tokens)
3. Process repeated multiple times (rep_num)
4. Predictions aggregated to probability estimates

**Configuration:**
- `src/ethos/configs/inference.yaml` - Inference settings

**Actions:**
```bash
# Run inference for Hospital Mortality
ethos_infer \
    task=hospital_mortality \
    model_fp=data/models/test_run/best_model.pt \
    input_dir=data/tokenized_datasets/mimic/test \
    output_dir=results/MORTALITY/test_run \
    output_fn=predictions \
    rep_num=8 \
    n_gpus=1

# Run inference for ICU Admission
ethos_infer \
    task=icu_admission \
    model_fp=data/models/test_run/best_model.pt \
    input_dir=data/tokenized_datasets/mimic/test \
    output_dir=results/ICU_ADMISSION/test_run \
    output_fn=predictions \
    rep_num=8

# Run inference for 30-day Readmission
ethos_infer \
    task=readmission \
    model_fp=data/models/test_run/best_model.pt \
    input_dir=data/tokenized_datasets/mimic/test \
    output_dir=results/READMISSION/test_run \
    output_fn=predictions \
    rep_num=32
```

**Expected Output:**
```
results/
└── MORTALITY/
    └── test_run/
        └── predictions.parquet  # Columns: patient_id, hadm_id, prediction, label, etc.
```

**Success Criteria:**
- ✅ Inference runs without errors
- ✅ Predictions generated for all test samples
- ✅ Results saved in parquet format

**Time Estimate:** 1-4 hours (depending on test size and rep_num)

---

### **Step 1.7: Results Analysis** 📈

**Goal:** Evaluate model performance and understand predictions

**Analysis Tools:**
- Jupyter notebooks in `notebooks/` directory
- Key metrics: AUROC, AUPRC, Accuracy, F1-score

**Actions:**
```bash
# Launch Jupyter
jupyter notebook

# Open relevant notebooks:
# - notebooks/mortality.ipynb
# - notebooks/icu_admission.ipynb
# - notebooks/readmission.ipynb
```

**Key Analyses:**
1. **Performance Metrics:**
   - Calculate AUROC, AUPRC for each task
   - Compare to baseline models
   - Stratify by patient demographics

2. **Prediction Trajectories:**
   - Visualize future health trajectory predictions
   - Understand what model learned
   - Identify high-risk vs low-risk patterns

3. **Error Analysis:**
   - False positives/negatives
   - Edge cases
   - Data quality issues

**Expected Performance (MIMIC-IV benchmarks from paper):**
- Hospital Mortality: AUROC ~0.85-0.90
- ICU Admission: AUROC ~0.80-0.85
- 30-day Readmission: AUROC ~0.70-0.75

**Success Criteria:**
- ✅ Metrics calculated successfully
- ✅ Performance is reasonable (AUROC > 0.65)
- ✅ Results documented

**Time Estimate:** 2-4 hours

---

## 🔬 Phase 2: Understanding the Pipeline for UF Adaptation (Weeks 4-5)

### **Step 2.1: Document MIMIC-Specific Components** 📝

**Goal:** Identify all MIMIC-specific code that needs adaptation

**Key Areas to Document:**

1. **Data Extraction (`scripts/meds/mimic/`):**
   - Input file structure assumptions
   - Column names and schemas
   - MIMIC-specific identifiers (subject_id, hadm_id, etc.)

2. **Preprocessing (`src/ethos/configs/dataset/mimic.yaml`):**
   - ICD code processing (ICD-9 to ICD-10 conversion)
   - Lab test name standardization
   - Medication ATC code mapping
   - Transfer/admission type processing
   - Demographics extraction

3. **Dataset Classes (`src/ethos/datasets/`):**
   - `mimic_icu.py` - ICU-specific features
   - `hospital_mortality.py` - Mortality labels
   - `readmission.py` - Readmission labels
   - `ed.py` - ED-specific features

4. **Task Definitions (`src/ethos/inference/constants.py`):**
   - How labels are defined for each prediction task
   - Timing of prediction (e.g., "predict within 24h")

**Actions:**
- Create a detailed comparison table: MIMIC vs UF data
- Document all field mappings
- Identify UF-specific requirements

**Deliverable:** `MIMIC_VS_UF_MAPPING.md` document

---

### **Step 2.2: Analyze UF Data Structure** 🏥

**Goal:** Understand UF Health EHR data format and requirements

**When UF Data Arrives, Document:**

1. **Data Format:**
   - File types (CSV, Parquet, Database?)
   - Schema and table structure
   - Identifiers used (patient_id, encounter_id, etc.)

2. **Data Content:**
   - Available tables (demographics, diagnoses, procedures, labs, etc.)
   - Coding systems (ICD-10 only? CPT? LOINC?)
   - Medication coding (NDC? RxNorm? Custom?)
   - Time granularity (timestamps available?)

3. **Prediction Tasks:**
   - What outcomes does UF want to predict?
   - Label definitions
   - Evaluation metrics

4. **Data Volume:**
   - Number of patients
   - Average encounters per patient
   - Time span of data

**Actions:**
- Meet with UF data providers to understand structure
- Request data dictionary/documentation
- Create sample data exploration notebooks

**Deliverable:** `UF_DATA_SPECIFICATION.md`

---

### **Step 2.3: Design UF Adaptation Strategy** 🎨

**Goal:** Plan the modifications needed for UF data

**Required Modifications:**

1. **Create UF MEDS Extraction Script:**
   - New `scripts/meds/uf/` directory
   - UF-specific configuration files
   - Field mapping logic

2. **Create UF Dataset Configuration:**
   - New `src/ethos/configs/dataset/uf.yaml`
   - UF-specific preprocessing transforms
   - Code filtering and normalization

3. **Adapt Dataset Classes:**
   - Modify or create new dataset classes in `src/ethos/datasets/`
   - Handle UF-specific identifiers
   - Define UF prediction tasks

4. **Update Tokenization:**
   - Verify vocabulary compatibility
   - Add UF-specific token mappings if needed
   - Handle UF-specific data quirks

**Strategy Decision Points:**
- **Minimal Adaptation:** Only change data extraction, keep rest same
- **Full Adaptation:** Customize all stages for UF specifics
- **Recommended:** Hybrid - adapt extraction & preprocessing, keep model architecture

**Deliverable:** `UF_ADAPTATION_DESIGN.md`

---

## 🚀 Phase 3: Scaling to HyperGator (Weeks 6-8)

### **Step 3.1: HyperGator Setup** 🖥️

**Goal:** Prepare environment on UF HyperGator cluster

**Requirements:**
- HyperGator account with GPU access
- Sufficient storage allocation
- SLURM job scheduling knowledge

**Setup Steps:**

```bash
# 1. Login to HyperGator
ssh username@hpg.rc.ufl.edu

# 2. Load required modules
module load conda
module load cuda/12.1

# 3. Create conda environment
conda create -n ethos_prod python=3.12
conda activate ethos_prod

# 4. Clone repository
cd /blue/your_group/username/
git clone https://github.com/ipolharvard/ethos-ares.git
cd ethos-ares

# 5. Install ETHOS
pip install -e .[jupyter]

# 6. Verify CUDA availability
python -c "import torch; print(torch.cuda.is_available())"
```

**Resource Allocation:**
- Storage: 500GB - 2TB (depending on data size)
- GPU: 1-8 A100 or V100 GPUs for training
- CPU: 20-40 cores for data preprocessing
- RAM: 128-256GB

**Success Criteria:**
- ✅ Environment setup on HyperGator
- ✅ GPU access verified
- ✅ Storage allocated

---

### **Step 3.2: SLURM Job Scripts** 📜

**Goal:** Create job scripts for automated pipeline execution

**The provided scripts use SLURM (designed for HPC clusters):**

**Modify Scripts for HyperGator:**

```bash
# Example: Modified run_training.sh for HyperGator
#!/bin/bash
#SBATCH --job-name=ethos_train
#SBATCH --output=logs/train_%j.log
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=20
#SBATCH --mem=128gb
#SBATCH --time=72:00:00
#SBATCH --partition=gpu
#SBATCH --gpus=a100:8
#SBATCH --account=your_account

# Load modules
module load conda cuda/12.1

# Activate environment
conda activate ethos_prod

# Run training
srun ethos_train \
    data_fp=/blue/your_group/username/data/tokenized_datasets/uf/train \
    val_size=6 \
    batch_size=32 \
    max_epochs=300 \
    n_layer=6 \
    n_head=12 \
    n_embd=768 \
    device=cuda \
    out_dir=/blue/your_group/username/models/uf_model
```

**Submit Jobs:**
```bash
# Submit training job
sbatch scripts/run_training.sh

# Monitor job
squeue -u username

# Check logs
tail -f logs/train_<job_id>.log
```

**Success Criteria:**
- ✅ Jobs submit successfully
- ✅ GPU allocation working
- ✅ Logs captured

---

### **Step 3.3: Full Pipeline Execution** 🔄

**Goal:** Run complete pipeline on full UF dataset

**Execution Plan:**

1. **MEDS Extraction (Job 1):**
   - Time: 6-12 hours
   - Resources: 20 CPUs, 256GB RAM
   - Output: MEDS formatted data

2. **Tokenization (Job 2):**
   - Time: 4-8 hours
   - Resources: 7 workers, 250GB RAM
   - Output: Tokenized timelines

3. **Training (Job 3):**
   - Time: 2-3 days
   - Resources: 8 GPUs, 128GB RAM
   - Output: Trained model

4. **Inference (Job 4):**
   - Time: 12-24 hours
   - Resources: 8 GPUs
   - Output: Predictions

**Pipeline Monitoring:**
- Check job status regularly
- Monitor GPU utilization
- Watch for out-of-memory errors
- Verify intermediate outputs

**Success Criteria:**
- ✅ All jobs complete successfully
- ✅ Final model trained
- ✅ Predictions generated

---

## 📊 Phase 4: UF-Specific Validation & Deployment (Weeks 9-12)

### **Step 4.1: Model Validation**

**Goal:** Ensure model performs well on UF data

**Validation Steps:**
1. Calculate performance metrics on UF test set
2. Compare to baseline models
3. Clinical validation with domain experts
4. Fairness analysis across patient groups
5. Calibration assessment

**Expected Challenges:**
- Different patient population characteristics
- Different coding practices
- Different prediction horizons
- Class imbalance

---

### **Step 4.2: Documentation & Reporting**

**Deliverables:**
1. **Technical Report:**
   - Pipeline modifications
   - Model performance
   - Comparison with MIMIC results

2. **Code Documentation:**
   - Commented code
   - Configuration guide
   - Troubleshooting guide

3. **User Manual:**
   - How to run pipeline
   - How to interpret results
   - Maintenance guide

---

## 🎓 Key Learning Points

### **What Makes ETHOS Unique:**
1. **Zero-shot Prediction:** No task-specific training needed
2. **Specialized EHR Language:** Not natural language, but medical event sequences
3. **Foundation Model:** Pre-trained once, used for multiple tasks
4. **Trajectory Explanation:** ARES provides interpretable health trajectories

### **Critical Components to Understand:**
1. **MEDS Format:** Standard for EHR time-series data
2. **Tokenization:** Converting medical events to model inputs
3. **GPT-2 Architecture:** How the model learns patterns
4. **Zero-shot Inference:** How predictions are generated

---

## ⚠️ Common Pitfalls & Solutions

| Issue | Solution |
|-------|----------|
| **Out of Memory** | Reduce batch size, use fewer workers, or reduce model size |
| **Slow Training** | Use multiple GPUs, increase batch size, use faster hardware |
| **Poor Performance** | More training data, longer training, hyperparameter tuning |
| **Code Mapping Errors** | Check vocabulary, verify coding system compatibility |
| **SLURM Job Failures** | Check resource limits, verify module loading, check logs |

---

## 📚 Additional Resources

### **Papers to Read:**
1. ETHOS-ARES Paper: https://arxiv.org/abs/2502.06124
2. Original ETHOS: https://www.nature.com/articles/s41746-024-01235-0
3. MEDS Standard: https://github.com/Medical-Event-Data-Standard/meds

### **Useful Tools:**
- **Polars:** For fast data processing
- **PyTorch:** Deep learning framework
- **Hydra:** Configuration management
- **Weights & Biases:** Experiment tracking (optional)

### **Code Repositories:**
- ETHOS-ARES: https://github.com/ipolharvard/ethos-ares
- MEDS Transforms: https://github.com/mmcdermott/MEDS_transforms

---

## ✅ Success Metrics

### **Phase 1 Success:**
- [ ] Environment setup complete
- [ ] MIMIC data preprocessed
- [ ] Model trained (even if small)
- [ ] Predictions generated
- [ ] Results analyzed

### **Phase 2 Success:**
- [ ] MIMIC pipeline fully understood
- [ ] UF data structure documented
- [ ] Adaptation plan created

### **Phase 3 Success:**
- [ ] HyperGator setup complete
- [ ] Full pipeline runs on HyperGator
- [ ] Trained production model

### **Phase 4 Success:**
- [ ] Model performs well on UF data
- [ ] Documentation complete
- [ ] Ready for deployment

---

## 📅 Timeline Summary

| Phase | Duration | Key Milestone |
|-------|----------|---------------|
| **Phase 1: Local Experimentation** | 3 weeks | Working MIMIC pipeline |
| **Phase 2: UF Adaptation Planning** | 2 weeks | Adaptation strategy |
| **Phase 3: HyperGator Scaling** | 3 weeks | Production model |
| **Phase 4: Validation & Deployment** | 4 weeks | Deployed system |
| **Total** | **12 weeks** | Production-ready UF model |

---

## 🤝 Next Steps (Immediate Actions)

1. **Today:** Set up conda environment and install ETHOS
2. **This Week:** Obtain MIMIC-IV access and download data
3. **Week 1:** Run MEDS extraction on small MIMIC subset
4. **Week 2:** Complete tokenization and start training
5. **Week 3:** Run inference and analyze results

---

## 📞 Support & Questions

- **GitHub Issues:** https://github.com/ipolharvard/ethos-ares/issues
- **MEDS Documentation:** https://github.com/Medical-Event-Data-Standard/meds
- **HyperGator Help:** https://help.rc.ufl.edu/

---

**Document Version:** 1.0  
**Last Updated:** January 24, 2026  
**Author:** GitHub Copilot  
**Status:** Living Document (Update as you progress!)
