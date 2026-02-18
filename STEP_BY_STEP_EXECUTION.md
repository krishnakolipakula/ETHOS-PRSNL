# ETHOS-ARES: Step-by-Step Execution Guide

**Follow this guide one step at a time. Complete each step before moving to the next.**

---

## ✅ Current Status: STEP 1

---

## STEP 1: Environment Setup (15-30 minutes)

### What You'll Do:
Install Python environment and ETHOS package

### Commands to Execute:

Open PowerShell and run these commands one by one:

```powershell
# 1. Navigate to project directory
cd "c:\Users\Krishna\OneDrive\Desktop\UF\RA\ETHOS\ethos-ares-master"

# 2. Check if conda is installed
conda --version
# If this fails, install Miniconda from: https://docs.conda.io/en/latest/miniconda.html

# 3. Create new conda environment
conda create --name ethos python=3.12 -y

# 4. Activate environment
conda activate ethos

# 5. Install PyTorch (CUDA version if you have NVIDIA GPU, otherwise CPU)
# For GPU (if you have NVIDIA GPU):
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y

# OR for CPU only (no GPU):
# conda install pytorch torchvision torchaudio cpuonly -c pytorch -y

# 6. Install ETHOS package
pip install -e .[jupyter]
```

### How to Verify Success:

Run these commands to check everything is working:

```powershell
# Test 1: Check ETHOS commands are available
ethos_tokenize --help
ethos_train --help
ethos_infer --help

# Test 2: Check PyTorch and CUDA
python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available())"

# Test 3: Check other packages
python -c "import polars, hydra, transformers; print('All packages installed!')"
```

### Expected Output:
- All three `ethos_*` commands should show help text
- PyTorch version should print (e.g., 2.7.1)
- CUDA available: True (if GPU) or False (if CPU only)
- "All packages installed!" message

### If You Get Errors:
- **Command not found:** Make sure conda environment is activated
- **CUDA not available:** It's OK if you don't have GPU, you can use CPU
- **Import errors:** Try `pip install -e . --no-deps` then `pip install -r requirements.txt`

---

## 📋 STOP HERE - Report Back!

**Once Step 1 is complete, tell me:**
1. ✅ Did all commands run successfully?
2. 💻 Do you have a GPU? (CUDA available: True/False?)
3. 📊 What's your system RAM? (Check Task Manager)

**Then we'll move to Step 2!**

---

## STEP 2: Create Directory Structure (Coming Next)

Will be revealed after Step 1 is complete...

---

## STEP 3: Obtain MIMIC Data (Coming Next)

Will be revealed after Step 2 is complete...

---

## Progress Tracker

- [ ] **STEP 1:** Environment Setup
- [ ] **STEP 2:** Create Directory Structure
- [ ] **STEP 3:** Obtain MIMIC Data
- [ ] **STEP 4:** MEDS Extraction (Small Sample)
- [ ] **STEP 5:** Tokenization
- [ ] **STEP 6:** Training (Quick Test)
- [ ] **STEP 7:** Inference
- [ ] **STEP 8:** Analyze Results

**Current Step: 1/8**

---

Last Updated: January 24, 2026
