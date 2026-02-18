# 🎯 ETHOS-ARES: Quick Reference Summary

**Your Complete Guide to Running and Adapting the Pipeline**

---

## 📚 Documentation Index

I've created comprehensive documentation for you. Here's what each document covers:

### 1. **[UF_ADAPTATION_STRATEGIC_PLAN.md](UF_ADAPTATION_STRATEGIC_PLAN.md)** ⭐ START HERE
   - **Complete 12-week strategic plan**
   - Detailed step-by-step instructions for each phase
   - Pipeline architecture overview
   - Phase 1: Local experimentation with MIMIC (Weeks 1-3)
   - Phase 2: Understanding for UF adaptation (Weeks 4-5)
   - Phase 3: Scaling to HyperGator (Weeks 6-8)
   - Phase 4: Validation & deployment (Weeks 9-12)
   - Success metrics and timeline

### 2. **[WINDOWS_QUICKSTART.md](WINDOWS_QUICKSTART.md)** 🚀 FOR LOCAL SETUP
   - Quick 30-minute setup guide
   - Windows-specific commands (PowerShell)
   - Directory structure setup
   - Testing without MIMIC data
   - Step-by-step pipeline execution
   - Common Windows issues & solutions
   - WSL setup for bash scripts

### 3. **[MIMIC_VS_UF_ADAPTATION.md](MIMIC_VS_UF_ADAPTATION.md)** 🔄 FOR UF DATA
   - Detailed comparison: MIMIC vs UF data structures
   - Component-by-component modification checklist
   - Files that need to be created for UF
   - Code examples for adaptation
   - Decision points and strategies
   - Comprehensive adaptation checklist

### 4. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** 🔧 WHEN THINGS GO WRONG
   - 18 common issues with solutions
   - Installation problems
   - Data preprocessing errors
   - Training issues (OOM, loss not decreasing)
   - Inference problems
   - Results analysis fixes
   - Debugging strategies

---

## 🗺️ Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     ETHOS-ARES PIPELINE                         │
└─────────────────────────────────────────────────────────────────┘

Step 1: RAW EHR DATA
   │   (MIMIC-IV CSV files or UF Health data)
   ├── Patients, Admissions, Diagnoses, Procedures,
   │   Labs, Medications, etc.
   │
   ▼
Step 2: MEDS EXTRACTION ⚙️
   │   Script: scripts/meds/run_mimic.sh
   │   Tool: MEDS_transforms pipeline
   ├── Standardizes data format
   ├── Creates train/test splits
   │   Output: Parquet files in MEDS format
   │
   ▼
Step 3: TOKENIZATION 🔤
   │   Command: ethos_tokenize
   │   Config: src/ethos/configs/tokenization.yaml
   ├── Converts medical codes to tokens
   ├── Quantizes numeric values
   ├── Encodes time intervals
   ├── Builds vocabulary
   │   Output: Tokenized timelines (.safetensors)
   │
   ▼
Step 4: MODEL TRAINING 🧠
   │   Command: ethos_train
   │   Config: src/ethos/configs/training.yaml
   ├── GPT-2 architecture (decoder-only)
   ├── Learns patient trajectory patterns
   ├── Auto-regressive prediction
   │   Output: Model checkpoints (.pt)
   │
   ▼
Step 5: INFERENCE 🎯
   │   Command: ethos_infer
   │   Config: src/ethos/configs/inference.yaml
   ├── Zero-shot prediction
   ├── Generate future health trajectories
   ├── Aggregate to probability estimates
   │   Output: Predictions (parquet)
   │
   ▼
Step 6: EVALUATION 📊
   │   Tool: Jupyter notebooks
   │   Location: notebooks/
   ├── Calculate AUROC, AUPRC, etc.
   ├── Visualize trajectories
   ├── Error analysis
   │   Output: Performance metrics & figures
   │
   ▼
FINAL: CLINICAL USE 🏥
```

---

## ⚡ Quick Start Commands

### Initial Setup
```bash
# 1. Create environment
conda create --name ethos python=3.12 -y
conda activate ethos

# 2. Install ETHOS
cd c:\Users\Krishna\OneDrive\Desktop\UF\RA\ETHOS\ethos-ares-master
pip install -e .[jupyter]

# 3. Verify
ethos_tokenize --help
```

### Run Pipeline (Assuming you have MIMIC data)
```bash
# Step 1: MEDS extraction (bash/WSL)
export MIMIC_IV_DIR="D:/MIMIC-IV"
export N_WORKERS=2
bash scripts/meds/run_mimic.sh "$MIMIC_IV_DIR" "data/mimic-2.2-premeds" "data/mimic-2.2-meds" ""

# Step 2: Tokenization
ethos_tokenize -m worker='range(0,2)' \
    input_dir=data/mimic-2.2-meds/data/train \
    output_dir=data/tokenized_datasets/mimic \
    out_fn=train

ethos_tokenize -m worker='range(0,2)' \
    input_dir=data/mimic-2.2-meds/data/test \
    vocab=data/tokenized_datasets/mimic/train \
    output_dir=data/tokenized_datasets/mimic \
    out_fn=test

# Step 3: Training (quick test)
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

# Step 4: Inference
ethos_infer \
    task=hospital_mortality \
    model_fp=data/models/test_run/best_model.pt \
    input_dir=data/tokenized_datasets/mimic/test \
    output_dir=results/MORTALITY/test_run \
    output_fn=predictions \
    rep_num=8

# Step 5: Analysis
jupyter notebook  # Open notebooks/mortality.ipynb
```

---

## 📋 Key Files to Understand

### Configuration Files
| File | Purpose | When to Edit |
|------|---------|--------------|
| `src/ethos/configs/tokenization.yaml` | Tokenization settings | Adjust quantiles, time intervals |
| `src/ethos/configs/training.yaml` | Model & training params | Change model size, learning rate |
| `src/ethos/configs/inference.yaml` | Inference settings | Adjust prediction parameters |
| `src/ethos/configs/dataset/mimic.yaml` | MIMIC preprocessing | **Create uf.yaml for UF data** |

### Python Modules
| File | Purpose | When to Edit |
|------|---------|--------------|
| `src/ethos/model.py` | GPT-2 model definition | Rarely (architecture changes) |
| `src/ethos/vocabulary.py` | Token vocabulary | Rarely (automatic) |
| `src/ethos/datasets/base.py` | Base dataset class | **Add UF identifiers** |
| `src/ethos/datasets/hospital_mortality.py` | Mortality task | Adapt labeling logic |
| `src/ethos/tokenize/mimic/preprocessors.py` | MIMIC preprocessing | **Create uf/preprocessors.py** |

### Scripts
| File | Purpose | When to Use |
|------|---------|-------------|
| `scripts/meds/run_mimic.sh` | MEDS extraction | Once per dataset |
| `scripts/run_tokenization.sh` | Tokenization (SLURM) | On HPC cluster |
| `scripts/run_training.sh` | Training (SLURM) | On HPC cluster |
| `scripts/run_inference.sh` | Inference (SLURM) | On HPC cluster |

---

## 🎯 Your Immediate Next Steps

### Week 1: Setup & Familiarization
- [ ] **Day 1-2:** Complete environment setup (WINDOWS_QUICKSTART.md)
- [ ] **Day 3-4:** Read strategic plan thoroughly
- [ ] **Day 5-7:** Apply for MIMIC-IV access if not done

### Week 2: MIMIC Experimentation
- [ ] **Day 8-10:** Download MIMIC-IV data
- [ ] **Day 11-12:** Run MEDS extraction on small subset
- [ ] **Day 13-14:** Complete tokenization

### Week 3: Training & Inference
- [ ] **Day 15-17:** Train small test model
- [ ] **Day 18-19:** Run inference
- [ ] **Day 20-21:** Analyze results in notebooks

### Week 4-5: Documentation & Planning
- [ ] Document MIMIC pipeline learnings
- [ ] Wait for UF data access
- [ ] Plan UF-specific adaptations
- [ ] Create UF configuration templates

### Week 6+: Production on HyperGator
- [ ] Setup HyperGator environment
- [ ] Adapt for UF data when available
- [ ] Run full pipeline on HPC
- [ ] Validate and document results

---

## 🧪 Testing Strategy

### Level 1: Sanity Check (1 hour)
```bash
# Minimal test with tiny data
ethos_train \
    max_iters=100 \
    batch_size=2 \
    n_layer=1 \
    n_head=2 \
    n_embd=32 \
    device=cpu
```

### Level 2: Small Scale Test (4-8 hours)
```bash
# Use 1000-5000 patients
# 1000 training iterations
# Small model (2-4 layers)
# Verify entire pipeline works
```

### Level 3: Production Run (2-7 days)
```bash
# Full dataset
# Full model (6 layers, 768 dim)
# 300 epochs or until convergence
# On HPC with multiple GPUs
```

---

## 📊 Expected Performance Benchmarks

### MIMIC-IV Results (from paper)
| Task | AUROC | AUPRC |
|------|-------|-------|
| Hospital Mortality | 0.85-0.90 | 0.30-0.40 |
| ICU Admission | 0.80-0.85 | 0.40-0.50 |
| 30-day Readmission | 0.70-0.75 | 0.35-0.45 |

**Your test run performance will be lower** if:
- Using smaller model
- Less training time
- Smaller dataset
- CPU instead of GPU

**This is OK for learning!** Focus on understanding the pipeline first.

---

## 🔑 Key Concepts to Understand

### 1. MEDS (Medical Event Data Standard)
- Standardized format for EHR time-series
- Patient-centric timeline of events
- Enables interoperability
- Learn more: https://github.com/Medical-Event-Data-Standard/meds

### 2. Zero-Shot Prediction
- Model not explicitly trained on specific tasks
- Learns general patient trajectory patterns
- Generates future health trajectories
- Aggregates to probability estimates
- **Key advantage:** One model, multiple tasks

### 3. Patient Health Timelines (PHT)
- Sequence of tokenized medical events
- Includes: codes, time intervals, numeric values
- Context: demographics + timeline
- Model learns: what typically happens next

### 4. Tokenization vs. Natural Language
- **Not** natural language processing
- Specialized medical event language
- Example token: `DIAG//ICD10//I50.9[INTERVAL:2d-4d]`
- Captures: event type + code + time since last event

### 5. GPT-2 Architecture
- Decoder-only transformer
- Auto-regressive generation
- Attention mechanism learns patterns
- Adapted for EHR (not text)

---

## ⚠️ Common Pitfalls to Avoid

1. **Running on insufficient hardware**
   - Tokenization needs RAM (16GB+ recommended)
   - Training needs GPU (8GB+ VRAM)
   - Use HPC for production

2. **Wrong data order**
   - Always tokenize TRAINING first (builds vocab)
   - Then tokenize TEST (uses training vocab)

3. **Ignoring preprocessing**
   - Data quality affects performance
   - Review `dataset/mimic.yaml` carefully
   - Adapt preprocessing for UF data

4. **Expecting MIMIC performance immediately**
   - Takes time to understand pipeline
   - Test runs will have lower performance
   - OK for learning phase!

5. **Not documenting changes**
   - Document every modification
   - Keep notes on errors and solutions
   - Will help with UF adaptation

---

## 💡 Pro Tips

1. **Start Small, Scale Up**
   - Test with 1000 patients first
   - Verify pipeline works end-to-end
   - Then scale to full dataset

2. **Use Version Control**
   - Git commit before major changes
   - Branch for UF-specific modifications
   - Document commit messages well

3. **Monitor Everything**
   - Training loss curves
   - GPU utilization
   - Disk space
   - Log files

4. **Leverage Existing Results**
   - Download pre-computed results from paper
   - Compare your results to benchmarks
   - Use notebooks for visualization

5. **Join the Community**
   - GitHub issues for questions
   - Read existing issues first
   - Contribute back solutions

---

## 📞 Support Resources

### Documentation You Created
- ✅ [UF_ADAPTATION_STRATEGIC_PLAN.md](UF_ADAPTATION_STRATEGIC_PLAN.md) - Main guide
- ✅ [WINDOWS_QUICKSTART.md](WINDOWS_QUICKSTART.md) - Quick setup
- ✅ [MIMIC_VS_UF_ADAPTATION.md](MIMIC_VS_UF_ADAPTATION.md) - Adaptation details
- ✅ [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues

### External Resources
- **ETHOS Paper:** https://arxiv.org/abs/2502.06124
- **GitHub Repo:** https://github.com/ipolharvard/ethos-ares
- **MEDS Standard:** https://github.com/Medical-Event-Data-Standard/meds
- **MEDS Transforms:** https://github.com/mmcdermott/MEDS_transforms
- **MIMIC-IV:** https://physionet.org/content/mimiciv/
- **HyperGator Docs:** https://help.rc.ufl.edu/

---

## ✅ Success Criteria Checklist

### Phase 1: Local MIMIC (Weeks 1-3)
- [ ] Environment setup complete
- [ ] MIMIC data downloaded
- [ ] MEDS extraction successful
- [ ] Tokenization complete
- [ ] Test model trained
- [ ] Inference generates predictions
- [ ] Results analyzed in notebook
- [ ] Documentation updated

### Phase 2: UF Planning (Weeks 4-5)
- [ ] MIMIC pipeline fully understood
- [ ] UF data requirements documented
- [ ] Adaptation strategy created
- [ ] Configuration templates prepared

### Phase 3: HyperGator (Weeks 6-8)
- [ ] HPC environment setup
- [ ] Full MIMIC pipeline runs on HPC
- [ ] UF data integration complete
- [ ] Production model trained

### Phase 4: Deployment (Weeks 9-12)
- [ ] Model validated on UF data
- [ ] Performance meets requirements
- [ ] Documentation complete
- [ ] Ready for clinical use

---

## 🎓 Learning Path

### Beginner (Week 1-2)
1. Understand pipeline overview
2. Setup environment
3. Run tokenization on sample data
4. Explore notebooks

### Intermediate (Week 3-4)
1. Train small model
2. Run inference
3. Calculate metrics
4. Understand configuration files

### Advanced (Week 5+)
1. Modify preprocessing
2. Add new tasks
3. Adapt for UF data
4. Optimize performance
5. Deploy on HPC

---

## 📝 Progress Tracking Template

Use this to track your progress:

```markdown
## Week [X] Progress

### Completed This Week
- [ ] Task 1
- [ ] Task 2

### Issues Encountered
- Issue: [Description]
  - Solution: [What worked]

### Next Week Plan
- [ ] Task 1
- [ ] Task 2

### Questions/Notes
- [Your notes here]
```

---

## 🎯 Final Advice

1. **Be Patient:** This is complex research code. Takes time to understand.
2. **Document Everything:** Future you will thank present you.
3. **Ask Questions:** GitHub issues are your friend.
4. **Start Simple:** Small working example > large broken system.
5. **Iterate:** Get something working, then improve.

**Good luck with your research! 🚀**

---

**Document Created:** January 24, 2026  
**Author:** GitHub Copilot Assistant  
**Status:** Ready for use  
**Next Review:** After Phase 1 completion
