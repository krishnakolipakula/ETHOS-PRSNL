# ETHOS-ARES Troubleshooting Guide

**Common issues and solutions when running the ETHOS-ARES pipeline**

---

## 🚨 Installation Issues

### Issue 1: Pip install fails with dependency conflicts

**Error:**
```
ERROR: Cannot install ethos because these package versions have conflicts
```

**Solutions:**

```bash
# Solution 1: Use conda for PyTorch first
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
pip install -e .[jupyter]

# Solution 2: Install without dependencies, then manually
pip install --no-deps -e .
pip install hydra-core==1.3.2 polars numpy tqdm loguru

# Solution 3: Fresh environment
conda create -n ethos_fresh python=3.12 -y
conda activate ethos_fresh
pip install -e .[jupyter]
```

---

### Issue 2: ImportError: No module named 'ethos'

**Error:**
```python
ModuleNotFoundError: No module named 'ethos'
```

**Solutions:**

```bash
# Verify installation
pip show ethos

# Reinstall in editable mode
cd /path/to/ethos-ares-master
pip install -e .

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# If using Jupyter, restart kernel after installation
```

---

### Issue 3: CUDA not available despite having GPU

**Error:**
```python
torch.cuda.is_available()  # Returns False
```

**Solutions:**

```bash
# Check NVIDIA driver
nvidia-smi

# Reinstall PyTorch with correct CUDA version
# Check your CUDA version:
nvidia-smi  # Look for "CUDA Version: X.Y"

# Install matching PyTorch (example for CUDA 12.1)
pip uninstall torch
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia

# Verify
python -c "import torch; print(torch.cuda.is_available()); print(torch.version.cuda)"
```

---

## 📁 Data Preprocessing Issues

### Issue 4: MEDS extraction fails - File not found

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'hosp/admissions.csv'
```

**Solutions:**

```bash
# 1. Verify MIMIC directory structure
ls -R $MIMIC_IV_DIR

# Expected structure:
# MIMIC_IV_DIR/
#   hosp/
#     admissions.csv
#     diagnoses_icd.csv
#     ...
#   icu/
#     icustays.csv
#     ...

# 2. Check environment variable
echo $MIMIC_IV_DIR

# 3. Use absolute path
export MIMIC_IV_DIR="/full/path/to/mimic-iv-2.2"

# 4. Verify file permissions
ls -l $MIMIC_IV_DIR/hosp/admissions.csv
```

---

### Issue 5: MEDS extraction - Memory Error

**Error:**
```
MemoryError: Unable to allocate array
```

**Solutions:**

```bash
# Solution 1: Reduce number of workers
export N_WORKERS=1  # Default is 7, which needs ~250GB RAM

# Solution 2: Increase system swap (Linux)
sudo fallocate -l 64G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Solution 3: Process in smaller batches
# Edit scripts/meds/mimic/configs/extract_MIMIC.yaml
# Reduce split fractions temporarily

# Solution 4: Use HPC cluster instead
```

---

### Issue 6: MEDS extraction produces empty output

**Error:**
```
Output directory created but no parquet files generated
```

**Debugging steps:**

```bash
# 1. Check logs for errors
tail -100 meds_extraction.log

# 2. Verify input data is not empty
wc -l $MIMIC_IV_DIR/hosp/admissions.csv

# 3. Test with single small file
# Temporarily modify extraction script to process only one table

# 4. Check disk space
df -h

# 5. Verify write permissions
touch $OUTPUT_DIR/test.txt && rm $OUTPUT_DIR/test.txt
```

---

## 🔤 Tokenization Issues

### Issue 7: Tokenization fails - Hydra configuration error

**Error:**
```
omegaconf.errors.ConfigAttributeError: Key 'input_dir' not found
```

**Solutions:**

```bash
# Solution 1: Provide all required arguments
ethos_tokenize \
    input_dir=data/mimic-2.2-meds/data/train \
    output_dir=data/tokenized_datasets/mimic \
    out_fn=train

# Solution 2: Check config file
cat src/ethos/configs/tokenization.yaml

# Solution 3: Use absolute paths
ethos_tokenize \
    input_dir=/full/path/to/data/mimic-2.2-meds/data/train \
    output_dir=/full/path/to/data/tokenized_datasets/mimic \
    out_fn=train
```

---

### Issue 8: Tokenization crashes with "Invalid code"

**Error:**
```
ValueError: Code 'XYZ' not found in vocabulary
```

**Solutions:**

```bash
# This usually happens when using test vocab on training data

# Solution 1: Ensure correct order
# 1. Tokenize TRAINING data first (builds vocab)
ethos_tokenize input_dir=data/.../train output_dir=... out_fn=train

# 2. Then tokenize TEST data (uses training vocab)
ethos_tokenize \
    input_dir=data/.../test \
    vocab=data/tokenized_datasets/mimic/train \
    output_dir=... \
    out_fn=test

# Solution 2: Delete existing vocab and retokenize
rm -rf data/tokenized_datasets/mimic/train/vocab.json
# Then retokenize training data
```

---

### Issue 9: Tokenization very slow

**Symptoms:** Taking > 12 hours for small dataset

**Solutions:**

```bash
# Solution 1: Increase workers
ethos_tokenize -m worker='range(0,4)' ...  # Use 4 workers

# Solution 2: Check if using HDD instead of SSD
# Move data to SSD if possible

# Solution 3: Profile to find bottleneck
python -m cProfile -o profile.stats -m ethos.tokenize.run_tokenization ...
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"

# Solution 4: Reduce dataset size for testing
# Use only first few parquet files
```

---

## 🧠 Training Issues

### Issue 10: Training - Out of Memory (OOM)

**Error:**
```
RuntimeError: CUDA out of memory. Tried to allocate X MiB
```

**Solutions (ordered by preference):**

```bash
# 1. Reduce batch size
ethos_train batch_size=8 ...  # Default is 32

# 2. Reduce model size
ethos_train \
    n_layer=4 \     # Default 6
    n_head=8 \      # Default 12
    n_embd=512 ...  # Default 768

# 3. Reduce context length
ethos_train n_positions=1024 ...  # Default 2048

# 4. Enable gradient accumulation
ethos_train \
    batch_size=8 \
    gradient_accumulation_steps=4 ...  # Effective batch size = 8*4=32

# 5. Use mixed precision (already default)
ethos_train dtype=bfloat16 ...

# 6. Use CPU (very slow, only for testing)
ethos_train device=cpu batch_size=2 ...
```

---

### Issue 11: Training loss not decreasing

**Symptoms:** Loss stays constant or increases

**Debugging steps:**

```python
# 1. Check if data is loading correctly
from ethos.datasets import TimelineDataset
ds = TimelineDataset('data/tokenized_datasets/mimic/train')
print(f"Dataset size: {len(ds)}")
print(f"Vocab size: {len(ds.vocab)}")
sample = ds[0]
print(f"Sample shape: {sample[0].shape}")

# 2. Verify labels are not all the same
import torch
tokens = ds.tokens[:10000]
print(f"Unique tokens: {torch.unique(tokens).shape}")

# 3. Check learning rate
# Too high: loss explodes
# Too low: loss doesn't decrease
# Try: lr=0.0001 to lr=0.001
```

**Solutions:**

```bash
# 1. Reduce learning rate
ethos_train lr=0.0001 ...  # Default 0.0006

# 2. Increase warmup iterations
ethos_train warmup_iters=5000 ...  # Default 2000

# 3. Check data quality
# Ensure tokenization completed successfully

# 4. Try simpler model first
ethos_train n_layer=2 n_head=4 n_embd=64 max_iters=1000 ...

# 5. Verify you're not overfitting from iteration 0
# Check validation loss
```

---

### Issue 12: Training crashes randomly

**Error:**
```
RuntimeError: CUDA error: device-side assert triggered
```

**Solutions:**

```bash
# 1. Enable CUDA debug mode (slower, but gives better errors)
CUDA_LAUNCH_BLOCKING=1 ethos_train ...

# 2. Check for NaN values
# Add to training script:
torch.autograd.set_detect_anomaly(True)

# 3. Reduce batch size (could be memory corruption)
ethos_train batch_size=16 ...

# 4. Update GPU drivers
nvidia-smi
# Check for available driver updates

# 5. Test GPU stability
# Run CUDA samples or stress test
```

---

### Issue 13: Cannot resume training from checkpoint

**Error:**
```
FileNotFoundError: best_model.pt not found
```

**Solutions:**

```bash
# 1. Check if checkpoint exists
ls -lh data/models/test_run/

# 2. Use correct checkpoint file
ethos_train \
    resume=true \
    out_dir=data/models/test_run \
    ...

# 3. Check checkpoint format
python -c "import torch; torch.load('data/models/test_run/best_model.pt')"

# 4. If corrupted, use recent_model.pt instead
cp data/models/test_run/recent_model.pt data/models/test_run/best_model.pt
```

---

## 🎯 Inference Issues

### Issue 14: Inference - Model not found

**Error:**
```
FileNotFoundError: Model file not found: best_model.pt
```

**Solutions:**

```bash
# 1. Verify model file exists
ls -lh data/models/test_run/best_model.pt

# 2. Use absolute path
ethos_infer \
    model_fp=/full/path/to/data/models/test_run/best_model.pt \
    ...

# 3. Check file permissions
chmod 644 data/models/test_run/best_model.pt

# 4. If model missing, check if training completed
tail -50 data/models/test_run/training.log
```

---

### Issue 15: Inference produces all same predictions

**Symptoms:** All predictions are 0.5 or all 0 or all 1

**Debugging:**

```python
# Check model output distribution
import torch
from ethos.model import GPT
from ethos.vocabulary import Vocabulary

# Load model
model = torch.load('data/models/test_run/best_model.pt')
model.eval()

# Check model structure
print(model)

# Test forward pass
vocab = Vocabulary.from_path('data/tokenized_datasets/mimic/train')
test_input = torch.randint(0, len(vocab), (1, 100))
with torch.no_grad():
    output = model(test_input)
print(f"Output shape: {output.shape}")
print(f"Output range: [{output.min():.3f}, {output.max():.3f}]")
```

**Solutions:**

```bash
# 1. Train longer
# Model may not be converged

# 2. Check if test data is similar to training data
# Distribution shift can cause issues

# 3. Increase rep_num for more stable predictions
ethos_infer rep_num=32 ...  # Default might be 8

# 4. Verify task implementation
# Check src/ethos/datasets/<task_name>.py
```

---

### Issue 16: Inference very slow

**Symptoms:** Taking > 1 hour per 100 samples

**Solutions:**

```bash
# 1. Use multiple GPUs
ethos_infer n_gpus=4 ...  # If available

# 2. Increase batch size
# Edit src/ethos/configs/inference.yaml
batch_size: 64  # Increase from default

# 3. Reduce rep_num for testing
ethos_infer rep_num=4 ...  # Lower repetitions

# 4. Use subset for testing
ethos_infer subset=0.1 ...  # Only 10% of data

# 5. Check if using CPU by mistake
python -c "import torch; print(torch.cuda.is_available())"
```

---

## 📊 Results Analysis Issues

### Issue 17: Notebook kernel dies when loading results

**Error:**
```
Kernel died, restarting...
```

**Solutions:**

```python
# 1. Load data in chunks
import polars as pl
df = pl.scan_parquet('results/*.parquet').head(10000).collect()

# 2. Increase Jupyter memory limit
# In terminal before launching Jupyter:
export JUPYTER_MEMORY_LIMIT=16G
jupyter notebook

# 3. Use lazy loading
df_lazy = pl.scan_parquet('results/*.parquet')
# Only compute what you need
result = df_lazy.select(['patient_id', 'prediction']).collect()

# 4. Close other notebooks/processes
# Check memory usage:
htop  # Linux
# Or Task Manager (Windows)
```

---

### Issue 18: Metrics calculation fails

**Error:**
```
ValueError: y_true and y_pred have different lengths
```

**Debugging:**

```python
import polars as pl

# Load predictions
df = pl.read_parquet('results/predictions.parquet')

# Check data
print(df.describe())
print(f"Rows: {len(df)}")
print(f"Columns: {df.columns}")
print(f"Null values:\n{df.null_count()}")

# Check label distribution
print(df['label'].value_counts())

# Check prediction distribution
print(df['prediction'].describe())
```

**Solutions:**

```python
# 1. Remove null values
df_clean = df.drop_nulls()

# 2. Ensure predictions are in [0, 1]
df = df.with_columns(
    pl.col('prediction').clip(0, 1)
)

# 3. Check for duplicates
df = df.unique()

# 4. Verify label format (should be 0/1)
df = df.with_columns(
    pl.col('label').cast(pl.Int32)
)
```

---

## 🔧 General Debugging Strategies

### Enable Detailed Logging

```python
# Add to any Python script
import logging
logging.basicConfig(level=logging.DEBUG)

# For Hydra configs
python script.py hydra.verbose=true
```

### Check System Resources

```bash
# CPU usage
top
htop

# GPU usage
nvidia-smi -l 1  # Updates every second
watch -n 1 nvidia-smi  # Alternative

# Disk space
df -h

# Memory usage
free -h

# Check process
ps aux | grep python
```

### Profile Code Performance

```python
# Time a specific function
import time
start = time.time()
# ... your code ...
print(f"Time: {time.time() - start:.2f}s")

# Profile with cProfile
python -m cProfile -o profile.stats script.py
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"

# Memory profiling
pip install memory_profiler
python -m memory_profiler script.py
```

---

## 🆘 Getting Help

### Before Asking for Help:

1. ✅ Read error message carefully
2. ✅ Check this troubleshooting guide
3. ✅ Search GitHub issues: https://github.com/ipolharvard/ethos-ares/issues
4. ✅ Verify your environment setup
5. ✅ Try a minimal example

### When Asking for Help:

Include:
- Full error message and stack trace
- Your command or code
- Python version (`python --version`)
- PyTorch version (`python -c "import torch; print(torch.__version__)"`)
- OS and hardware (GPU type)
- Data size and configuration
- What you've already tried

### Useful Diagnostic Commands

```bash
# Environment info
python -c "import torch; import sys; print(f'Python: {sys.version}'); print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.version.cuda}'); print(f'CUDA available: {torch.cuda.is_available()}')"

# Package versions
pip list | grep -E "(torch|polars|hydra|ethos)"

# System info
uname -a  # Linux
systeminfo  # Windows

# GPU info
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
```

---

## 📚 Additional Resources

- **ETHOS Paper:** https://arxiv.org/abs/2502.06124
- **GitHub Issues:** https://github.com/ipolharvard/ethos-ares/issues
- **MEDS Documentation:** https://github.com/Medical-Event-Data-Standard/meds
- **PyTorch Debugging:** https://pytorch.org/docs/stable/notes/faq.html
- **Hydra Configuration:** https://hydra.cc/docs/intro/

---

**Last Updated:** January 24, 2026  
**Please contribute:** If you encounter an issue not listed here, please document the solution!
