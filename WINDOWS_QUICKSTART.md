# ETHOS-ARES Quick Start Guide for Windows

**For Local Windows Development**

---

## 🚀 Quick Setup (30 minutes)

### Step 1: Create Python Environment

```powershell
# Open PowerShell and navigate to project
cd "c:\Users\Krishna\OneDrive\Desktop\UF\RA\ETHOS\ethos-ares-master"

# Create conda environment
conda create --name ethos python=3.12 -y
conda activate ethos

# Install ETHOS package
pip install -e .[jupyter]

# Verify installation
ethos_tokenize --help
```

### Step 2: Check Dependencies

```powershell
# Test PyTorch
python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available())"

# Test other key packages
python -c "import polars, hydra; print('All packages OK')"
```

---

## 📁 Directory Setup

```powershell
# Create data directories
New-Item -ItemType Directory -Force -Path "data"
New-Item -ItemType Directory -Force -Path "data\mimic-2.2-premeds"
New-Item -ItemType Directory -Force -Path "data\mimic-2.2-meds"
New-Item -ItemType Directory -Force -Path "data\tokenized_datasets"
New-Item -ItemType Directory -Force -Path "data\models"
New-Item -ItemType Directory -Force -Path "results"
```

---

## 🧪 Testing with Demo Data (WITHOUT MIMIC)

If you don't have MIMIC data yet, you can test the pipeline with the demo:

```powershell
# Generate demo results (if available)
python create_demo_results.py
```

---

## 📊 Pipeline Execution (With MIMIC Data)

### Option A: Run Step-by-Step (Recommended for Learning)

#### 1. MEDS Extraction (PowerShell Adaptation)

Since the bash scripts won't work directly on Windows, here's the PowerShell equivalent:

```powershell
# Set environment variables
$env:MIMIC_IV_DIR = "D:\MIMIC-IV"  # Adjust to your path
$env:N_WORKERS = "2"  # Reduce for local machine

# Note: The MEDS extraction scripts are complex bash scripts
# For Windows, you have two options:

# Option 1: Use WSL (Windows Subsystem for Linux)
wsl bash scripts/meds/run_mimic.sh "$env:MIMIC_IV_DIR" "data/mimic-2.2-premeds" "data/mimic-2.2-meds" ""

# Option 2: Use Git Bash (if installed)
bash scripts/meds/run_mimic.sh "$env:MIMIC_IV_DIR" "data/mimic-2.2-premeds" "data/mimic-2.2-meds" ""

# Option 3: Run Python directly (bypassing bash script)
# This requires understanding the MEDS_transforms pipeline
# See: https://github.com/mmcdermott/MEDS_transforms
```

#### 2. Tokenization

```powershell
# Tokenize training data
ethos_tokenize -m worker='range(0,2)' `
    input_dir=data/mimic-2.2-meds/data/train `
    output_dir=data/tokenized_datasets/mimic `
    out_fn=train

# Tokenize test data
ethos_tokenize -m worker='range(0,2)' `
    input_dir=data/mimic-2.2-meds/data/test `
    vocab=data/tokenized_datasets/mimic/train `
    output_dir=data/tokenized_datasets/mimic `
    out_fn=test
```

**Note:** Use backtick `` ` `` for line continuation in PowerShell (not backslash `\`)

#### 3. Training (Small Test Run)

```powershell
# Small test training (CPU or GPU)
ethos_train `
    data_fp=data/tokenized_datasets/mimic/train `
    val_size=1 `
    batch_size=8 `
    max_iters=1000 `
    n_layer=2 `
    n_head=4 `
    n_embd=128 `
    device=cuda `
    out_dir=data/models/test_run

# If CUDA not available, use CPU:
ethos_train `
    data_fp=data/tokenized_datasets/mimic/train `
    val_size=1 `
    batch_size=4 `
    max_iters=500 `
    n_layer=2 `
    n_head=4 `
    n_embd=64 `
    device=cpu `
    out_dir=data/models/test_run_cpu
```

#### 4. Inference

```powershell
# Run prediction for hospital mortality
ethos_infer `
    task=hospital_mortality `
    model_fp=data/models/test_run/best_model.pt `
    input_dir=data/tokenized_datasets/mimic/test `
    output_dir=results/MORTALITY/test_run `
    output_fn=predictions `
    rep_num=8 `
    n_gpus=1
```

---

## 🐛 Common Windows Issues & Solutions

### Issue 1: Command Not Found
```powershell
# If ethos_tokenize not found, use full path:
python -m ethos.tokenize.run_tokenization --help

# Or add to PATH
$env:PATH += ";$HOME\.local\bin"
```

### Issue 2: CUDA Out of Memory
```powershell
# Reduce batch size and model size
ethos_train `
    batch_size=2 `
    n_layer=1 `
    n_head=2 `
    n_embd=32 `
    ...
```

### Issue 3: Bash Scripts Don't Run
```powershell
# Install WSL (Windows Subsystem for Linux)
wsl --install

# Or use Git Bash
# Download from: https://git-scm.com/download/win
```

### Issue 4: File Path Issues
```powershell
# Windows uses backslashes, Python/Unix use forward slashes
# Always use forward slashes in configs and commands:
# Good: data/models/test
# Bad:  data\models\test

# Or use raw strings in Python:
# r"C:\Users\Krishna\data"
```

---

## 📊 Monitoring Progress

### Check Training Progress
```powershell
# Watch training log
Get-Content data/models/test_run/training.log -Wait -Tail 20

# Or use Python
python -c "import sys; [print(line, end='') for line in open('data/models/test_run/training.log')]"
```

### Check GPU Usage
```powershell
# If NVIDIA GPU
nvidia-smi

# Or continuously monitor
while ($true) { nvidia-smi; Start-Sleep -Seconds 2; Clear-Host }
```

---

## 🔍 Exploring Results

### Launch Jupyter Notebook
```powershell
# Start Jupyter
jupyter notebook

# Open browser to: http://localhost:8888
# Navigate to notebooks/ folder
```

### Quick Data Inspection
```powershell
# Check vocabulary size
python -c "from ethos.vocabulary import Vocabulary; v = Vocabulary.from_path('data/tokenized_datasets/mimic/train'); print(f'Vocab size: {len(v)}')"

# Check dataset size
python -c "from ethos.datasets import TimelineDataset; ds = TimelineDataset('data/tokenized_datasets/mimic/train'); print(f'Dataset size: {len(ds):,}')"
```

---

## 🎯 Next Steps After Setup

1. **Read the main strategic plan:** [UF_ADAPTATION_STRATEGIC_PLAN.md](UF_ADAPTATION_STRATEGIC_PLAN.md)
2. **Explore the notebooks:** Check `notebooks/` folder for examples
3. **Understand the code:** Start with `src/ethos/model.py` to see the model architecture
4. **Join discussions:** https://github.com/ipolharvard/ethos-ares/issues

---

## 📚 Useful PowerShell Commands

```powershell
# List directory contents
Get-ChildItem data/

# Create directory
New-Item -ItemType Directory -Path data/new_folder

# Copy files
Copy-Item source.txt destination.txt

# Check file size
(Get-Item file.txt).Length / 1MB  # Size in MB

# Find files
Get-ChildItem -Recurse -Filter *.py

# Search in files
Select-String -Path "src/**/*.py" -Pattern "TimelineDataset"

# Monitor process
Get-Process | Where-Object {$_.Name -like "*python*"}

# Kill process
Stop-Process -Name python
```

---

## 🔧 Advanced: WSL Setup (Recommended for Production)

If you plan to do serious work, WSL is highly recommended:

```powershell
# Install WSL
wsl --install -d Ubuntu-22.04

# After installation, restart and setup:
wsl

# Inside WSL:
cd /mnt/c/Users/Krishna/OneDrive/Desktop/UF/RA/ETHOS/ethos-ares-master
conda create -n ethos python=3.12
conda activate ethos
pip install -e .[jupyter]

# Now you can run bash scripts directly:
bash scripts/meds/run_mimic.sh ...
```

---

## 💡 Pro Tips for Windows Development

1. **Use VS Code:** Best editor for this project on Windows
   - Install Python extension
   - Install Jupyter extension
   - Integrated terminal supports both PowerShell and WSL

2. **Use Conda:** Better than pip for Windows
   - Handles complex dependencies
   - Easier CUDA setup

3. **WSL for Scripts:** Run bash scripts in WSL, Python in Windows
   - Access Windows files from WSL: `/mnt/c/Users/...`
   - Access WSL files from Windows: `\\wsl$\Ubuntu\home\...`

4. **Git Bash Alternative:** Lighter than WSL
   - Good for running bash scripts
   - Limited functionality compared to WSL

---

## 🆘 Getting Help

- **ETHOS Issues:** https://github.com/ipolharvard/ethos-ares/issues
- **Windows/WSL:** https://docs.microsoft.com/en-us/windows/wsl/
- **PyTorch Windows:** https://pytorch.org/get-started/locally/
- **Conda Windows:** https://docs.conda.io/projects/conda/en/latest/user-guide/install/windows.html

---

**Last Updated:** January 24, 2026  
**Tested On:** Windows 11, Python 3.12, CUDA 12.1
