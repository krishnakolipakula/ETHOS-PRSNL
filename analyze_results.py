"""Analyze ICU mortality prediction results."""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import f1_score, roc_auc_score, precision_score, recall_score, confusion_matrix, classification_report

results_dir = Path("results/ICU_MORTALITY/sample_run/")
results_files = list(results_dir.glob("*.parquet"))
if not results_files:
    print(f"No results found in {results_dir}")
    exit(1)

results_path = results_files[0]
print(f"Reading results from: {results_path.name}")
df = pd.read_parquet(results_path)

print("=" * 80)
print("ICU MORTALITY PREDICTION RESULTS")
print("=" * 80)

print(f"\nTotal ICU cases analyzed: {len(df)}")
print(f"\nColumns: {df.columns}")

# Show summary statistics
print("\n" + "=" * 80)
print("OUTCOME SUMMARY")
print("=" * 80)
outcomes = df.groupby("expected").size().reset_index(name='count')
print(outcomes)

# Show first few predictions
print("\n" + "=" * 80)
print("SAMPLE PREDICTIONS (First 10)")
print("=" * 80)
sample = df[[
    "patient_id",
    "expected",
    "actual",
    "actual_prob",
    "true_token_time",
    "token_time"
]].head(10)

for _, row in sample.iterrows():
    outcome = row['expected']
    pred = row['actual']
    correct = "✓" if outcome == pred else "✗"
    
    # Handle time conversion - could be microseconds or timedelta
    true_time_val = row['true_token_time']
    if isinstance(true_time_val, pd.Timedelta):
        true_time = true_time_val.total_seconds() / 86400  # Convert to days
    else:
        true_time = true_time_val / 1e6 / 3600 / 24  # Convert from microseconds to days
    
    pred_time_val = row['token_time']
    if pd.notna(pred_time_val):
        if isinstance(pred_time_val, pd.Timedelta):
            pred_time = pred_time_val.total_seconds() / 86400
        else:
            pred_time = pred_time_val / 1e6 / 3600 / 24
    else:
        pred_time = 0
    
    print(f"\nPatient {row['patient_id']}:")
    print(f"  Actual outcome:    {outcome}")
    print(f"  Predicted outcome: {pred} {correct}")
    print(f"  Prediction prob:   {row['actual_prob']:.3f}")
    print(f"  Actual time:       {true_time:.1f} days")
    if pred_time > 0:
        print(f"  Predicted time:    {pred_time:.1f} days")

# Calculate accuracy
accuracy = (df["expected"] == df["actual"]).mean()
print("\n" + "=" * 80)
print(f"OVERALL ACCURACY: {accuracy:.2%}")
print("=" * 80)

# Show confusion matrix
print("\nCONFUSION MATRIX:")
confusion = pd.crosstab(df['expected'], df['actual'], margins=True)
print(confusion)
