# Response to Ziyi's Questions
## ETHOS-ARES Pipeline Implementation

---

## Loss Function Used

**Answer: Cross-Entropy Loss (Categorical Cross-Entropy)**

### Technical Details:

**Location in Code:**
- File: `src/ethos/model.py`, line 175
- Implementation: `F.cross_entropy(logits.view(-1, logits.size(-1)), labels.view(-1))`

**Function Signature:**
```python
def forward(self, input_ids, labels=None) -> ModelOutput:
    # ... model forward pass ...
    
    if labels is not None:
        logits = self.lm_head(x)
        loss = F.cross_entropy(logits.view(-1, logits.size(-1)), labels.view(-1))
    else:
        logits = self.lm_head(x[:, [-1], :])
        loss = None
    
    return ModelOutput(loss=loss, logits=logits)
```

### Why Cross-Entropy Loss?

**1. Next Token Prediction Task:**
- Model predicts: Which token comes next in the patient timeline?
- 72 possible tokens (vocabulary size)
- Cross-entropy is standard for multi-class classification

**2. Mathematical Formulation:**
```
Loss = -Σ y_true * log(y_pred)

Where:
- y_true: One-hot encoded actual next token (e.g., [0, 0, 1, 0, ..., 0])
- y_pred: Softmax probabilities over all 72 tokens
- Model learns to maximize probability of correct token
```

**3. Interpretation of Loss Values:**

| Loss Value | Meaning |
|------------|---------|
| 4.28 (Iteration 0) | Model randomly guessing (log(72) ≈ 4.28) |
| 1.84 (Iteration 500) | Learning patterns, better than random |
| 0.63 (Iteration 1400) | Best performance, high confidence predictions |
| 0.34 (Iteration 5000) | Excellent fit (possibly overfitting on small dataset) |

**Lower loss = Better predictions**
- Loss → 0: Perfect predictions (rare in real data)
- Loss → log(vocab_size): Random guessing

### Implementation Details:

**PyTorch Function:** `torch.nn.functional.cross_entropy()`

**Properties:**
- Combines `log_softmax` + `negative log likelihood`
- Numerically stable (avoids numerical underflow)
- Automatically handles class imbalances through weighting (not used in our case)

**Input Shapes:**
- `logits`: [batch_size × sequence_length, vocab_size=72]
- `labels`: [batch_size × sequence_length]
- Returns: Scalar loss value (averaged across all tokens)

**Gradient Flow:**
- Loss backpropagates through entire model
- Updates all 0.41M parameters
- Optimized with AdamW optimizer

### Example Calculation:

For a single prediction:
```python
# Model outputs logits for 72 tokens
logits = [1.2, 0.5, 3.8, -0.1, ..., 0.9]  # 72 values

# Convert to probabilities
probs = softmax(logits)  # [0.02, 0.01, 0.15, 0.01, ..., 0.02]

# Actual next token is token ID 28 (ICD code)
true_label = 28

# Cross-entropy loss
loss = -log(probs[28])

# If probs[28] = 0.15:
loss = -log(0.15) = 1.90

# If probs[28] = 0.80 (high confidence):
loss = -log(0.80) = 0.22 (much better!)
```

### Why Not Other Loss Functions?

**MSE (Mean Squared Error)?**
- ❌ Used for regression (continuous values)
- ❌ Doesn't capture probabilistic nature of token prediction

**Binary Cross-Entropy?**
- ❌ Used for binary classification (2 classes)
- ❌ We have 72 classes (tokens)

**Focal Loss / Label Smoothing?**
- ✓ Could be used for advanced training
- ❌ Not implemented in our pipeline (standard cross-entropy sufficient)

**Contrastive Loss?**
- ✓ Could help with representation learning
- ❌ Not needed for supervised next-token prediction

### Connection to Clinical Outcomes:

**Training:**
- Loss measures: How well model predicts next clinical event
- Lower loss → Better understanding of patient timelines

**Inference:**
- After ICU_ADMISSION token, predict next token
- High probability for MEDS_DEATH → Mortality risk
- High probability for ICU_DISCHARGE → Survival likely
- High probability for =6mt → Expects 6-month gap (temporal pattern)

**Current Challenge:**
- Model learned temporal patterns (time intervals)
- Needs more data to learn definitive outcome predictions
- Cross-entropy loss correctly penalizes wrong predictions

### Validation Loss Behavior:

**Training Loss (Blue curve):**
- Decreases consistently: 4.28 → 0.34
- Shows model learning training data patterns

**Validation Loss (Orange curve):**
- Decreases then plateaus: 4.28 → 1.10
- Best at iteration 1400 (loss = 1.03)
- Higher than training loss → Generalization gap

**Why Validation Loss Higher?**
- Only 39 test patients (small sample)
- Test patients have different patterns
- Sign of slight overfitting (expected with 356 train patients)

### Production Improvements:

For full-scale training (300k patients):

**1. Weighted Cross-Entropy:**
```python
# Weight rare outcomes more heavily
class_weights = {
    'MEDS_DEATH': 2.0,  # Emphasize mortality
    'ICU_DISCHARGE': 1.5,
    'time_intervals': 0.5  # De-emphasize time tokens
}
loss = F.cross_entropy(logits, labels, weight=class_weights)
```

**2. Label Smoothing:**
```python
# Prevent overconfidence
loss = F.cross_entropy(logits, labels, label_smoothing=0.1)
```

**3. Auxiliary Losses:**
```python
# Multi-task learning
total_loss = next_token_loss + 0.1 * outcome_prediction_loss
```

---

## Summary for Ziyi:

✅ **Loss Function:** Cross-Entropy Loss (PyTorch `F.cross_entropy()`)  
✅ **Purpose:** Predict next token in patient timeline (72 possible tokens)  
✅ **Behavior:** Started at 4.28 (random), improved to 0.63 (best), ended at 0.34  
✅ **Standard:** Industry-standard for language models and sequence prediction  
✅ **Implementation:** Single line in model.py, automatically handles backpropagation  

**Key Insight:** Loss values show model successfully learned clinical patterns from limited data. Validation loss plateau at 1.03 indicates need for more training data to improve generalization.

---

**References:**
- Code: `src/ethos/model.py` line 175
- PyTorch Documentation: https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html
- Training Logs: Loss curves from our 5,000 iteration training run

**Date:** January 29, 2026  
**Prepared by:** Krishna Kolipakulа
