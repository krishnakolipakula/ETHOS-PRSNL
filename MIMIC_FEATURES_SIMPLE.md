# MIMIC-IV Features for Model Training Review

**Date:** February 1, 2026  
**For:** Ziyi - Feature Selection Review  
**From:** Krishna Kolipakulа  
**Location:** `/orange/yonghui.wu/chenziyi/MIMIC/mimiciv/3.1/`

---

## 🏥 **HOSPITAL MODULE (hosp/)**

| Feature | Type | Significance | Currently Used | Include? |
|---------|------|--------------|----------------|----------|
| **patients** | Demographics | Patient age, gender, date of death | ✅ Yes | [ ] |
| **admissions** | Events | Hospital admission/discharge times, type, location | ✅ Yes | [ ] |
| **diagnoses_icd** | Codes | ICD-9/10 diagnosis codes (what diseases patient has) | ✅ Yes | [ ] |
| **procedures_icd** | Codes | ICD-9/10 procedure codes (what procedures performed) | ✅ Yes | [ ] |
| **drgcodes** | Billing | DRG severity & mortality risk scores (⚠️ direct mortality predictor) | ❌ No | [ ] |
| **labevents** | Labs | All laboratory test results (CBC, metabolic panel, cardiac markers) | ❌ No | [ ] |
| **emar** | Medications | Medication administration records (when drugs given, dose, route) | ❌ No | [ ] |
| **pharmacy** | Medications | Pharmacy dispensing records (prescriptions filled) | ❌ No | [ ] |
| **prescriptions** | Medications | Medication orders (what doctors prescribed) | ❌ No | [ ] |
| **microbiologyevents** | Labs | Microbiology cultures and antibiotic sensitivity results | ❌ No | [ ] |
| **transfers** | Events | Patient transfers between care units (ward → ICU → ward) | ❌ No | [ ] |
| **hcpcsevents** | Codes | HCPCS procedure codes (outpatient procedures, supplies) | ❌ No | [ ] |
| **omr** | Clinical | Online medical records (patient-reported outcomes) | ❌ No | [ ] |

---

## 🏥 **ICU MODULE (icu/)**

| Feature | Type | Significance | Currently Used | Include? |
|---------|------|--------------|----------------|----------|
| **icustays** | Events | ICU admission/discharge times, ICU type (MICU, SICU, CCU) | ✅ Yes | [ ] |
| **chartevents** | Time-Series | Vital signs (HR, BP, RR, SpO2, temp) charted every 1-5 minutes | ❌ No | [ ] |
| **inputevents** | Infusions | IV fluids, vasopressors, medications with rates and volumes | ❌ No | [ ] |
| **outputevents** | Measurements | Patient fluid outputs (urine, drains, blood loss) | ❌ No | [ ] |
| **procedureevents** | Procedures | ICU procedures (intubation, dialysis, central lines) | ❌ No | [ ] |
| **datetimeevents** | Events | Time-stamped events (device insertion/removal dates) | ❌ No | [ ] |

---

## ⚠️ **CRITICAL QUESTIONS FOR ZIYI**

### **1. Data Leakage - Features That Predict the Outcome:**
- [ ] **DRG Mortality Risk** - Healthcare billing system's mortality prediction (1-4 scale) - EXCLUDE?
- [ ] **DRG Severity** - Disease severity score (1-4 scale) - EXCLUDE?
- [ ] **Discharge Location = DIED** - Direct death indicator in admissions table - EXCLUDE?
- [ ] **MEDS_DEATH token** - Death event itself in patient timeline - EXCLUDE from input?

### **2. Bias - Features That May Introduce Unfairness:**
- [ ] **Race/Ethnicity** - In admissions and patients tables - EXCLUDE?
- [ ] **Insurance Type** - Medicaid/Medicare/Private (socioeconomic proxy) - EXCLUDE?
- [ ] **Language** - Primary language spoken (immigration status proxy) - EXCLUDE?

### **3. End-of-Life Features - May Indicate Terminal Care:**
- [ ] **Comfort Care Medications** - Morphine drips, atropine, scopolamine - EXCLUDE?
- [ ] **Hospice Discharge Location** - Patient discharged to hospice - EXCLUDE?
- [ ] **Terminal Extubation** - Removing life support - EXCLUDE?

### **4. Size Considerations - Very Large Tables:**
- [ ] **labevents (2.59 GB)** - Millions of lab results - Include ALL or filter to common labs?
- [ ] **chartevents (20+ GB)** - ICU vitals every 1-5 min - Include ALL or sample hourly?

---

## 📋 **RECOMMENDATION CHECKLIST**

**Please mark each category:**
- ✅ = INCLUDE in training
- ❌ = EXCLUDE from training
- ⚠️ = PARTIAL (with filtering rules)

### **Demographics:**
- [ ] Age, Gender
- [ ] Race/Ethnicity
- [ ] Insurance Type
- [ ] Language

### **Hospital Events:**
- [ ] Admission/Discharge times and types
- [ ] Discharge location (Home, SNF, Rehab, etc.)
- [ ] Discharge location = DIED
- [ ] ICU admission/discharge

### **Diagnoses & Procedures:**
- [ ] ICD diagnosis codes (all)
- [ ] ICD procedure codes (all)
- [ ] DRG codes (billing category)
- [ ] DRG Severity score (1-4)
- [ ] DRG Mortality Risk score (1-4)

### **Laboratory Tests:**
- [ ] All lab results (2.59 GB)
- [ ] Common labs only (CBC, BMP, cardiac markers)
- [ ] Exclude post-mortem labs

### **Medications:**
- [ ] All medications (emar + pharmacy)
- [ ] Exclude comfort care/end-of-life meds
- [ ] Include vasopressors (critical care drugs)

### **ICU Data:**
- [ ] Vital signs (chartevents)
- [ ] IV fluids/medications (inputevents)
- [ ] Procedures (intubation, dialysis, lines)
- [ ] Exclude terminal extubation

### **Transfers:**
- [ ] Care unit transfers (ward ↔ ICU)
- [ ] Exclude transfers to morgue

---

## 🎯 **NEXT STEPS AFTER YOUR FEEDBACK**

1. Update MEDS configuration to exclude specified features
2. Re-extract data with approved feature set
3. Retrain model with clean, unbiased features
4. Validate predictions are not driven by leakage

---

## 🔧 **MODEL & LOSS FUNCTION DETAILS**

### **Architecture:**
- **Model Type:** GPT-2 Decoder-Only Transformer
- **Parameters:** 0.41M (sample model with 2 layers, 128 embedding dimensions)
- **Framework:** PyTorch 2.10.0

### **Loss Function:**
**Type:** Cross-Entropy Loss (`torch.nn.functional.cross_entropy`)

**Mathematical Formulation:**
$$L = -\frac{1}{N}\sum_{n=1}^{N}\sum_{c=1}^{C} y_{n,c} \log(p_{n,c})$$

Where:
- $N$ = number of tokens in batch (all sequences combined)
- $C$ = vocabulary size (72 tokens in current model, 500+ after scaling)
- $y_{n,c}$ = true label (1 if token $n$ is class $c$, 0 otherwise - one-hot encoded)
- $p_{n,c}$ = predicted probability for class $c$ at position $n$ (after softmax)

**Step-by-Step Computation:**
1. **Model Output (Logits):** Raw scores from final layer → shape `[batch_size, seq_length, vocab_size]`
   - Example: `[8, 2048, 72]` = 8 patients, up to 2048 events each, 72 possible tokens
2. **Flatten:** Reshape to `[N, vocab_size]` where N = batch_size × seq_length
   - Example: `[16384, 72]` = all token positions combined
3. **Softmax:** Convert logits to probabilities: $p_c = \frac{e^{z_c}}{\sum_{j=1}^{C} e^{z_j}}$
   - Each row sums to 1.0 (valid probability distribution)
4. **Negative Log-Likelihood:** For each position, take $-\log(p_{\text{true class}})$
   - If model predicts correct token with 90% confidence: $-\log(0.9) = 0.105$ (low loss)
   - If model predicts correct token with 10% confidence: $-\log(0.1) = 2.303$ (high loss)
5. **Average:** Mean across all N positions to get final scalar loss

**Why Cross-Entropy for Healthcare Prediction?**
1. **Multi-Class Token Prediction:** At each timestep, model must choose 1 of 72 tokens (MEDS_DEATH, ICU_ADMISSION, ANTIBIOTIC//VANCOMYCIN, etc.)
   - Cross-entropy naturally handles this discrete choice problem
   - Alternative losses (MSE, MAE) designed for continuous values, not categorical outcomes

2. **Probabilistic Interpretation:** Output probabilities $p_c$ represent model's confidence
   - Can rank predictions: "80% chance of ICU admission, 15% death, 5% discharge"
   - Useful for clinical decision support (not just binary yes/no)

3. **Well-Behaved Gradients:** Loss is convex with respect to logits
   - Smooth gradient flow during backpropagation
   - Avoids vanishing/exploding gradients common in other losses
   - Model learns faster and more stably

4. **Handles Class Imbalance:** Implicitly weights by frequency
   - Rare tokens (MEDS_DEATH occurs ~5% of time) get appropriate loss contribution
   - Common tokens (TIME_DELTA, routine vitals) don't dominate learning

5. **Information-Theoretic Justification:** Minimizes KL-divergence between true and predicted distributions
   - Finds best probabilistic model of patient trajectories
   - Aligns with medical reasoning under uncertainty

**Optimization Details:**
- **No Class Weights:** Default uniform weighting (each token type treated equally)
- **No Label Smoothing:** Using hard targets (0 or 1), not smoothed probabilities
- **Ignore Index:** Special padding tokens excluded from loss calculation
- **Reduction:** Mean (not sum) across all positions for stable gradients regardless of sequence length

### **Training Specs (Current Sample Run):**
- **Iterations:** 5,000
- **Initial Loss:** 4.38
- **Final Loss:** 0.41
- **Training Time:** ~5 minutes on MPS GPU (Apple Silicon)
- **Optimizer:** AdamW (default from PyTorch)
- **Device:** MPS (Metal Performance Shaders) for training, CPU for inference

---

**Your Response Needed:**
Please review and mark which features to INCLUDE/EXCLUDE, then send back to Krishna.

**Questions?** Contact Krishna Kolipakulа
