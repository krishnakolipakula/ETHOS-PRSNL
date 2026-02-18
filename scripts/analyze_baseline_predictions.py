# Baseline Model Analysis - Before Full Pipeline
## Check what we achieved with 5 tables before expanding to 12

---

## Step 1: Verify Saved Checkpoints

```bash
# Check what checkpoints exist
ls -lh /blue/yonghui.wu/kolipakulak/ethos-ares/models/full_91k_final/

# Expected to see:
# - best_model.pt (iter 800, loss 3.51)
# - recent_model.pt
# - checkpoint_iter_800.pt (if we saved it)
```

---

## Step 2: Check Inference Output (Job 24400000)

```bash
# Check if inference produced any results before timeout
ls -lh /blue/yonghui.wu/kolipakulak/ethos-ares/results/

# Look for directories:
# - MORTALITY/
# - ICU_MORTALITY/
# Or wherever inference was saving

# Check what files were created
find /blue/yonghui.wu/kolipakulak/ethos-ares/results/ -type f -name "*.csv" -o -name "*.json"
```

---

## Step 3: Quick Inference Test (5-10 minutes)

Let's run a SMALL inference test on just 100 samples to see predictions:

```bash
#!/bin/bash
#SBATCH --job-name=quick_test
#SBATCH --output=/blue/yonghui.wu/kolipakulak/ethos-ares/logs/quick_test_%j.log
#SBATCH --error=/blue/yonghui.wu/kolipakulak/ethos-ares/logs/quick_test_%j.err
#SBATCH --partition=hpg-gpu
#SBATCH --qos=yonghui.wu-b
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16gb
#SBATCH --time=00:30:00

module load conda
conda activate ethos-ares

cd /blue/yonghui.wu/kolipakulak/ethos-ares

# Run inference on SMALL subset for quick test
python -c "
import torch
from ethos.inference.run_inference import run_inference
from ethos.inference.constants import Task

# Quick test: 100 samples only
run_inference(
    model_fp='models/full_91k_final/best_model.pt',
    input_dir='data/tokenized_datasets/mimic-ziyi/train',
    output_dir='results/QUICK_TEST',
    task=Task.HOSPITAL_MORTALITY,
    max_samples=100,  # Just 100 samples for quick check
    dataset='mimic_bare'
)
"
```

---

## Step 4: Analyze Predictions

Once quick test completes, analyze results:

```python
#!/usr/bin/env python3
# File: analyze_baseline_predictions.py

import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score, confusion_matrix
import matplotlib.pyplot as plt

# Load predictions
pred_df = pd.read_csv('/blue/yonghui.wu/kolipakulak/ethos-ares/results/QUICK_TEST/predictions.csv')

print("=" * 60)
print("BASELINE MODEL PREDICTIONS ANALYSIS (5 tables, 812 iterations)")
print("=" * 60)

# Basic stats
print(f"\nTotal samples: {len(pred_df)}")
print(f"Columns: {pred_df.columns.tolist()}")

# Check prediction distribution
print("\n--- Prediction Distribution ---")
print(f"Mean prediction: {pred_df['prediction'].mean():.4f}")
print(f"Std prediction: {pred_df['prediction'].std():.4f}")
print(f"Min prediction: {pred_df['prediction'].min():.4f}")
print(f"Max prediction: {pred_df['prediction'].max():.4f}")

# Check if predictions are diverse or all same
if pred_df['prediction'].std() < 0.01:
    print("⚠️  WARNING: Predictions are nearly identical - model may not have learned much")
else:
    print("✅ Predictions are diverse - model is differentiating patients")

# Ground truth distribution
print("\n--- Ground Truth Distribution ---")
print(f"Positive cases: {pred_df['label'].sum()} ({pred_df['label'].mean()*100:.1f}%)")
print(f"Negative cases: {len(pred_df) - pred_df['label'].sum()} ({(1-pred_df['label'].mean())*100:.1f}%)")

# Performance metrics (if we have ground truth)
if 'label' in pred_df.columns:
    try:
        auroc = roc_auc_score(pred_df['label'], pred_df['prediction'])
        auprc = average_precision_score(pred_df['label'], pred_df['prediction'])
        
        print("\n--- Performance Metrics ---")
        print(f"AUROC: {auroc:.4f}")
        print(f"AUPRC: {auprc:.4f}")
        
        # Threshold at 0.5
        pred_binary = (pred_df['prediction'] > 0.5).astype(int)
        cm = confusion_matrix(pred_df['label'], pred_binary)
        
        print("\n--- Confusion Matrix (threshold=0.5) ---")
        print(f"True Negatives:  {cm[0,0]}")
        print(f"False Positives: {cm[0,1]}")
        print(f"False Negatives: {cm[1,0]}")
        print(f"True Positives:  {cm[1,1]}")
        
        accuracy = (cm[0,0] + cm[1,1]) / cm.sum()
        sensitivity = cm[1,1] / (cm[1,1] + cm[1,0]) if (cm[1,1] + cm[1,0]) > 0 else 0
        specificity = cm[0,0] / (cm[0,0] + cm[0,1]) if (cm[0,0] + cm[0,1]) > 0 else 0
        
        print(f"\nAccuracy: {accuracy:.4f}")
        print(f"Sensitivity (Recall): {sensitivity:.4f}")
        print(f"Specificity: {specificity:.4f}")
        
        # Interpretation
        print("\n--- Interpretation ---")
        if auroc > 0.75:
            print("✅ STRONG: Model performance is good (AUROC > 0.75)")
        elif auroc > 0.65:
            print("⚠️  MODERATE: Model performance is acceptable (AUROC 0.65-0.75)")
        elif auroc > 0.55:
            print("⚠️  WEAK: Model performance is poor (AUROC 0.55-0.65)")
        else:
            print("❌ FAILING: Model barely better than random (AUROC < 0.55)")
            
    except Exception as e:
        print(f"\n❌ Could not calculate metrics: {e}")

# Sample predictions
print("\n--- Sample Predictions (first 10) ---")
print(pred_df[['patient_id', 'label', 'prediction']].head(10).to_string(index=False))

print("\n--- High Confidence Correct (top 5) ---")
correct = pred_df[pred_df['label'] == (pred_df['prediction'] > 0.5).astype(int)]
if len(correct) > 0:
    high_conf_correct = correct.nlargest(5, 'prediction')
    print(high_conf_correct[['patient_id', 'label', 'prediction']].to_string(index=False))

print("\n--- High Confidence Wrong (top 5) ---")
wrong = pred_df[pred_df['label'] != (pred_df['prediction'] > 0.5).astype(int)]
if len(wrong) > 0:
    high_conf_wrong = wrong.nlargest(5, 'prediction')
    print(high_conf_wrong[['patient_id', 'label', 'prediction']].to_string(index=False))

print("\n" + "=" * 60)
print("DECISION POINT:")
print("=" * 60)
print("If AUROC > 0.70: Baseline is strong, adding 12 tables may give marginal gains")
print("If AUROC 0.60-0.70: Baseline is okay, 12 tables should help significantly")
print("If AUROC < 0.60: Baseline is weak, definitely need more data (12 tables)")
print("=" * 60)
