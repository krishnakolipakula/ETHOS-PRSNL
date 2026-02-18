# ETHOS-ARES Pipeline Visual Guide

This document provides visual representations of the ETHOS-ARES pipeline workflow.

---

## 📊 Complete Pipeline Flowchart

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    ETHOS-ARES COMPLETE PIPELINE                       ║
╚═══════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 1: DATA PREPARATION (1-2 days)                                │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  Raw EHR Data    │  
│  (MIMIC-IV)      │  CSV files: admissions, diagnoses, procedures,
│                  │  labs, medications, ICU stays, demographics
└────────┬─────────┘
         │
         │ scripts/meds/run_mimic.sh
         │ (MEDS_transforms pipeline)
         │
         ▼
┌──────────────────┐
│  MEDS Format     │  Parquet files: Standardized patient timelines
│  Data            │  - Subject-centric organization
│  ├─ train/       │  - Timestamp-ordered events
│  └─ test/        │  - Consistent schema
└────────┬─────────┘
         │
         │
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 2: TOKENIZATION (4-12 hours)                                  │
└─────────────────────────────────────────────────────────────────────┘
         │
         │ ethos_tokenize (train data)
         │ - Build vocabulary
         │ - Map codes to tokens
         │ - Quantize numeric values
         │ - Encode time intervals
         ▼
┌──────────────────┐
│  Tokenized       │  Safetensors files: Numerical sequences
│  Training Data   │  - Token IDs
│  + Vocabulary    │  - Time intervals
│                  │  - Patient metadata
└────────┬─────────┘  - vocab.json, quantiles.json
         │
         │ ethos_tokenize (test data, uses training vocab)
         ▼
┌──────────────────┐
│  Tokenized       │  Safetensors files: Uses training vocabulary
│  Test Data       │  
└────────┬─────────┘
         │
         │
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 3: MODEL TRAINING (2-7 days)                                  │
└─────────────────────────────────────────────────────────────────────┘
         │
         │ ethos_train
         │ - GPT-2 architecture
         │ - Auto-regressive learning
         │ - Next-token prediction
         ▼
┌──────────────────┐
│  Trained Model   │  PyTorch checkpoint (.pt)
│                  │  - Model weights
│  best_model.pt   │  - Configuration
│  recent_model.pt │  - Optimizer state
└────────┬─────────┘
         │
         │
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 4: INFERENCE (12-24 hours)                                    │
└─────────────────────────────────────────────────────────────────────┘
         │
         │ ethos_infer
         │ - Zero-shot prediction
         │ - Trajectory generation
         │ - Probability aggregation
         ▼
┌──────────────────┐
│  Predictions     │  Parquet file with:
│                  │  - Patient IDs
│  predictions.    │  - Predicted probabilities
│  parquet         │  - True labels
└────────┬─────────┘  - Timestamps
         │
         │
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 5: EVALUATION & ANALYSIS                                      │
└─────────────────────────────────────────────────────────────────────┘
         │
         │ Jupyter notebooks
         ▼
┌──────────────────┐
│  Results         │  - AUROC, AUPRC metrics
│  Analysis        │  - Performance figures
│                  │  - Trajectory visualizations
│  Figures &       │  - Error analysis
│  Metrics         │  
└──────────────────┘
```

---

## 🔄 Zero-Shot Prediction Process

```
┌─────────────────────────────────────────────────────────────────────┐
│           HOW ETHOS MAKES PREDICTIONS (Zero-Shot)                   │
└─────────────────────────────────────────────────────────────────────┘

Patient Timeline:
[BIRTH]──[DIAG:Diabetes]──[LAB:Glucose↑]──[MED:Insulin]──[?]
    ▲                                                        │
    │                                                        │
    └────── Model predicts what comes next ─────────────────┘

Step 1: Input Patient History
┌─────────────────────────────────────────────┐
│ Context (Demographics):                      │
│ - Age: 65 years                             │
│ - Gender: Male                              │
│ - Race: White                               │
│                                             │
│ Timeline (Recent events):                   │
│ - t-48h: Admission (Emergency)              │
│ - t-36h: Diagnosis (Heart Failure)          │
│ - t-24h: Lab (BNP: elevated)                │
│ - t-12h: Med (Furosemide)                   │
│ - t-6h:  Lab (Creatinine: rising)           │
│ - NOW: What happens next?                   │
└─────────────────────────────────────────────┘
                    ▼
Step 2: Model Generates Future Trajectory (Repeat N times)
┌─────────────────────────────────────────────┐
│ Generation 1:                                │
│ → ICU Transfer → Intubation → Death         │ (High risk)
│                                             │
│ Generation 2:                                │
│ → Med adjustment → Lab improvement → DC     │ (Low risk)
│                                             │
│ Generation 3:                                │
│ → ICU Transfer → Stabilization → DC         │ (Med risk)
│                                             │
│ ... (N total generations)                   │
└─────────────────────────────────────────────┘
                    ▼
Step 3: Aggregate to Probability
┌─────────────────────────────────────────────┐
│ Task: Hospital Mortality                     │
│                                             │
│ Trajectories ending in DEATH: 12 / 32       │
│ Predicted Probability: 0.375 (37.5%)        │
│                                             │
│ Task: ICU Admission                          │
│                                             │
│ Trajectories with ICU: 20 / 32              │
│ Predicted Probability: 0.625 (62.5%)        │
└─────────────────────────────────────────────┘
```

---

## 🏗️ Model Architecture

```
╔═══════════════════════════════════════════════════════════════════╗
║                    GPT-2 MODEL ARCHITECTURE                        ║
╚═══════════════════════════════════════════════════════════════════╝

Input Tokens (Context + Timeline):
┌──────────────────────────────────────────────────────────────────┐
│ [AGE:65] [GENDER:M] [RACE:W] [DOB] [EVENT1] [INT:2d] [EVENT2] ...│
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
                  ┌─────────────────┐
                  │ Token Embedding │ (n_embd = 768)
                  │     Layer       │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   Positional    │ (n_positions = 2048)
                  │    Encoding     │
                  └────────┬────────┘
                           │
          ┌────────────────┴────────────────┐
          │                                 │
          ▼                                 ▼
┌──────────────────┐              ┌──────────────────┐
│ Transformer      │              │ Transformer      │
│ Block 1          │ ──────────▶  │ Block 2          │
│                  │              │                  │
│ - Multi-head     │              │ - Multi-head     │
│   Attention (12) │              │   Attention (12) │
│ - Feed Forward   │              │ - Feed Forward   │
│ - Layer Norm     │              │ - Layer Norm     │
│ - Dropout        │              │ - Dropout        │
└──────────────────┘              └──────────────────┘
          │                                 │
          └────────────────┬────────────────┘
                           │
                    ... (n_layer = 6)
                           │
                           ▼
                  ┌─────────────────┐
                  │  Output Layer   │
                  │  (vocab_size)   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   Softmax       │
                  └────────┬────────┘
                           │
                           ▼
              Probability Distribution
              over Next Tokens
         [0.001, 0.32, 0.002, 0.15, ...]
```

**Default Configuration:**
- Layers: 6
- Attention Heads: 12
- Embedding Dimension: 768
- Context Window: 2048 tokens
- Vocabulary Size: ~10,000-20,000 (depends on data)
- Parameters: ~100M (approximate)

---

## 📊 Data Flow Details

```
╔═══════════════════════════════════════════════════════════════════╗
║                    TOKENIZATION PROCESS                            ║
╚═══════════════════════════════════════════════════════════════════╝

Raw Event:
┌─────────────────────────────────────────────────────────────────┐
│ timestamp: 2023-06-15 14:30:00                                   │
│ code: I50.9 (Heart Failure, unspecified)                        │
│ type: DIAGNOSIS                                                  │
│ time_since_last_event: 2.5 days                                 │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────┐
         │  Code Mapping                     │
         │  I50.9 → DIAG//ICD10//I50        │ (Grouped to category)
         └──────────────────┬───────────────┘
                            │
                            ▼
         ┌──────────────────────────────────┐
         │  Time Interval Encoding           │
         │  2.5 days → [INTERVAL:2d-4d]     │
         └──────────────────┬───────────────┘
                            │
                            ▼
Final Token Sequence:
┌─────────────────────────────────────────────────────────────────┐
│ DIAG//ICD10//I50[INTERVAL:2d-4d]                                │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    Token ID: 4327


Numeric Value Example (Lab Result):
┌─────────────────────────────────────────────────────────────────┐
│ test: Glucose                                                    │
│ value: 215 mg/dL                                                │
│ timestamp: 2023-06-15 08:00:00                                  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────┐
         │  Quantization                     │
         │  215 mg/dL → Q8 (8th decile)     │
         └──────────────────┬───────────────┘
                            │
                            ▼
Final Token Sequence:
┌─────────────────────────────────────────────────────────────────┐
│ LAB//GLUCOSE//Q8[INTERVAL:12h-18h]                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Task-Specific Prediction

```
╔═══════════════════════════════════════════════════════════════════╗
║              TASK DEFINITIONS & LABELING                           ║
╚═══════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────┐
│ Task 1: HOSPITAL MORTALITY                                       │
├─────────────────────────────────────────────────────────────────┤
│ Prediction Point: Any time during admission                     │
│ Outcome Window: Same admission                                  │
│ Positive Label: Death occurs before discharge                   │
│ Negative Label: Patient discharged alive                        │
│                                                                  │
│ Timeline:                                                        │
│ ─[Admission]────[Events...]────[PREDICT]────[Discharge/Death]   │
│                                    ▲                             │
│                                    │                             │
│                              Model predicts                      │
│                              from this point                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Task 2: ICU ADMISSION (24-hour)                                  │
├─────────────────────────────────────────────────────────────────┤
│ Prediction Point: Any time during admission (before ICU)        │
│ Outcome Window: Next 24 hours                                   │
│ Positive Label: ICU transfer within 24h                         │
│ Negative Label: No ICU transfer within 24h                      │
│                                                                  │
│ Timeline:                                                        │
│ ─[Admission]────[PREDICT]────[24h window]────[ICU/No ICU]       │
│                     ▲                                            │
│                     └── Model predicts ICU need                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Task 3: 30-DAY READMISSION                                       │
├─────────────────────────────────────────────────────────────────┤
│ Prediction Point: At discharge                                  │
│ Outcome Window: 30 days after discharge                         │
│ Positive Label: Readmission within 30 days                      │
│ Negative Label: No readmission within 30 days                   │
│                                                                  │
│ Timeline:                                                        │
│ ─[Admission]────[Discharge/PREDICT]────[30 days]────[Readm?]    │
│                               ▲                                  │
│                               └── Model predicts readmission     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Adaptation Workflow (MIMIC → UF)

```
╔═══════════════════════════════════════════════════════════════════╗
║           ADAPTING FROM MIMIC TO UF DATA                           ║
╚═══════════════════════════════════════════════════════════════════╝

Phase 1: UNDERSTAND MIMIC
┌────────────────────────────────────────┐
│ 1. Run complete MIMIC pipeline         │
│ 2. Document all steps                  │
│ 3. Identify MIMIC-specific code        │
│ 4. Note configuration parameters       │
└────────────────┬───────────────────────┘
                 │
                 ▼
Phase 2: ANALYZE UF DATA
┌────────────────────────────────────────┐
│ 1. Obtain UF data dictionary           │
│ 2. Map UF fields to MIMIC fields       │
│ 3. Identify differences                │
│ 4. Document UF-specific requirements   │
└────────────────┬───────────────────────┘
                 │
                 ▼
Phase 3: CREATE UF CONFIGURATIONS
┌────────────────────────────────────────┐
│ Create New:                             │
│ ├─ scripts/meds/uf/                    │
│ │  ├─ pre_MEDS.py                      │
│ │  └─ configs/                         │
│ ├─ src/ethos/configs/dataset/uf.yaml  │
│ └─ src/ethos/tokenize/uf/              │
│                                         │
│ Modify:                                 │
│ ├─ src/ethos/datasets/base.py         │
│ └─ Task-specific dataset files         │
└────────────────┬───────────────────────┘
                 │
                 ▼
Phase 4: TEST & ITERATE
┌────────────────────────────────────────┐
│ 1. Test MEDS extraction                │
│ 2. Test tokenization                   │
│ 3. Test training on small subset       │
│ 4. Debug and fix issues                │
│ 5. Scale to full dataset               │
└────────────────┬───────────────────────┘
                 │
                 ▼
Phase 5: VALIDATE
┌────────────────────────────────────────┐
│ 1. Run inference on UF test set        │
│ 2. Calculate performance metrics       │
│ 3. Clinical validation                 │
│ 4. Document results                    │
└────────────────────────────────────────┘
```

---

## 💻 Computational Requirements

```
╔═══════════════════════════════════════════════════════════════════╗
║                RESOURCE REQUIREMENTS BY STAGE                      ║
╚═══════════════════════════════════════════════════════════════════╝

┌─────────────────────┬──────────┬──────────┬───────────┬──────────┐
│ Stage               │ CPU      │ RAM      │ GPU       │ Time     │
├─────────────────────┼──────────┼──────────┼───────────┼──────────┤
│ MEDS Extraction     │ 7 cores  │ 250 GB   │ Not needed│ 6-12 h   │
│ (Full MIMIC)        │          │          │           │          │
│                     │ OR       │ OR       │           │          │
│ (Reduced workers)   │ 2 cores  │ 64 GB    │ Not needed│ 12-24 h  │
├─────────────────────┼──────────┼──────────┼───────────┼──────────┤
│ Tokenization        │ 7 cores  │ 128 GB   │ Not needed│ 4-8 h    │
│ (Full dataset)      │          │          │           │          │
├─────────────────────┼──────────┼──────────┼───────────┼──────────┤
│ Training            │ 20 cores │ 128 GB   │ 8x A100   │ 2-3 days │
│ (Full model)        │          │          │ 40GB VRAM │          │
│                     │ OR       │ OR       │ OR        │ OR       │
│ (Small test)        │ 4 cores  │ 16 GB    │ 1x GPU    │ 1-2 h    │
│                     │          │          │ 8GB VRAM  │          │
├─────────────────────┼──────────┼──────────┼───────────┼──────────┤
│ Inference           │ 40 cores │ 256 GB   │ 8x A100   │ 12-24 h  │
│ (Full dataset)      │          │          │           │          │
├─────────────────────┼──────────┼──────────┼───────────┼──────────┤
│ Analysis            │ 1 core   │ 16 GB    │ Not needed│ 1-2 h    │
│ (Jupyter)           │          │          │           │          │
└─────────────────────┴──────────┴──────────┴───────────┴──────────┘

LOCAL MACHINE (Typical):
├─ Suitable for: Small tests, development, analysis
├─ CPU: 4-8 cores
├─ RAM: 16-32 GB
├─ GPU: NVIDIA GPU with 8-16 GB VRAM (optional but recommended)
└─ Storage: 200-500 GB SSD

HYPERGATOR (Production):
├─ Suitable for: Full pipeline, production models
├─ CPU: 20-40 cores per job
├─ RAM: 128-256 GB per job
├─ GPU: 1-8 A100 GPUs (40 GB VRAM each)
└─ Storage: 1-2 TB
```

---

## 📈 Performance Expectations

```
╔═══════════════════════════════════════════════════════════════════╗
║        MODEL PERFORMANCE vs TRAINING CONFIGURATION                 ║
╚═══════════════════════════════════════════════════════════════════╝

Configuration:        Toy Model    Small Model    Full Model (Paper)
────────────────────────────────────────────────────────────────────
Layers:                    1             2              6
Heads:                     2             4             12
Embedding:                32           128            768
Training Time:         10 min        1-2 h          2-3 days
Dataset:              Subset        Medium           Full
────────────────────────────────────────────────────────────────────

Expected Performance (Hospital Mortality AUROC):
────────────────────────────────────────────────────────────────────
Toy Model:              0.55-0.60    (Barely better than random)
Small Model:            0.65-0.75    (Reasonable for testing)
Full Model:             0.85-0.90    (Production quality)
────────────────────────────────────────────────────────────────────

Training Loss:
────────────────────────────────────────────────────────────────────
Initial Loss:           ~8-10        (All models start here)
Toy Model Final:        ~6-7         (Limited learning)
Small Model Final:      ~4-5         (Good learning)
Full Model Final:       ~3-4         (Best learning)
────────────────────────────────────────────────────────────────────

Notes:
- Toy model: Quick sanity check only
- Small model: Development and testing
- Full model: Production deployment
```

---

## 🗂️ Directory Structure

```
ethos-ares-master/
│
├── 📄 START_HERE.md                         ⭐ Read this first!
├── 📄 UF_ADAPTATION_STRATEGIC_PLAN.md       Main strategic guide
├── 📄 WINDOWS_QUICKSTART.md                 Quick Windows setup
├── 📄 MIMIC_VS_UF_ADAPTATION.md             Adaptation checklist
├── 📄 TROUBLESHOOTING.md                    Problem solutions
├── 📄 README.md                             Original repo README
│
├── 📁 scripts/                              Shell scripts
│   ├── meds/                                MEDS extraction
│   │   ├── run_mimic.sh                     Main MEDS script
│   │   └── mimic/                           MIMIC configs
│   │       └── configs/
│   ├── run_tokenization.sh                  Tokenization (SLURM)
│   ├── run_training.sh                      Training (SLURM)
│   └── run_inference.sh                     Inference (SLURM)
│
├── 📁 src/ethos/                            Main Python package
│   ├── configs/                             Hydra configurations
│   │   ├── tokenization.yaml                Tokenization config
│   │   ├── training.yaml                    Training config
│   │   ├── inference.yaml                   Inference config
│   │   └── dataset/
│   │       └── mimic.yaml                   MIMIC preprocessing
│   ├── datasets/                            Dataset classes
│   │   ├── base.py                          Base dataset
│   │   ├── hospital_mortality.py            Mortality task
│   │   ├── readmission.py                   Readmission task
│   │   └── ...
│   ├── tokenize/                            Tokenization logic
│   │   ├── run_tokenization.py              Main script
│   │   └── mimic/                           MIMIC preprocessors
│   ├── train/                               Training logic
│   │   └── run_training.py                  Main script
│   ├── inference/                           Inference logic
│   │   └── run_inference.py                 Main script
│   ├── model.py                             GPT-2 implementation
│   └── vocabulary.py                        Vocabulary class
│
├── 📁 notebooks/                            Jupyter notebooks
│   ├── mortality.ipynb                      Mortality analysis
│   ├── icu_admission.ipynb                  ICU analysis
│   ├── readmission.ipynb                    Readmission analysis
│   └── figures.ipynb                        Generate figures
│
├── 📁 data/                                 ⚠️ YOU CREATE THIS
│   ├── mimic-2.2-premeds/                   MEDS pre-processing
│   ├── mimic-2.2-meds/                      MEDS formatted data
│   ├── tokenized_datasets/                  Tokenized data
│   │   └── mimic/
│   │       ├── train/
│   │       └── test/
│   └── models/                              Trained models
│       └── test_run/
│           ├── best_model.pt
│           └── recent_model.pt
│
└── 📁 results/                              ⚠️ YOU CREATE THIS
    ├── MORTALITY/                           Mortality predictions
    ├── ICU_ADMISSION/                       ICU predictions
    └── READMISSION/                         Readmission predictions
```

---

**This visual guide complements the main documentation.**
**Refer to START_HERE.md for the complete overview.**

Last Updated: January 24, 2026
