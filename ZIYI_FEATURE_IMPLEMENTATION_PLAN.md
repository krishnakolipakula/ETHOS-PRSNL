# ZIYI'S FEATURE SELECTION - IMPLEMENTATION PLAN

**Date:** February 3, 2026  
**Based On:** Ziyi's red-highlighted features from MIMIC-IV table list  
**Goal:** Train model on large dataset with approved features only

---

## ✅ **APPROVED FEATURES (RED = INCLUDE)**

### **Core Module:**
1. **patients → gender** - Patient's biological sex (M/F)
2. **patients → date of death** - When patient died (if applicable)
3. **admissions → admission** - Hospital admission timestamp
4. **admissions → discharge** - Hospital discharge timestamp  
5. **admissions → diagnoses** - Primary diagnosis for admission

### **Hospital Module:**
6. **diagnoses_icd** - ICD-9/10 diagnosis codes
7. **prescriptions** - Medications prescribed to patient
8. **drgcodes** - Diagnosis Related Group billing codes

---

## 📋 **DETAILED FIELD MAPPING**

### **Table 1: hosp/patients**
**File:** `patients.csv.gz`  
**Fields to Extract:**
- `subject_id` (patient identifier - PRIMARY KEY)
- `gender` → Token: `GENDER//MALE` or `GENDER//FEMALE`
- `anchor_year` (year of birth proxy for age calculation)
- `dod` (date of death) → Token: `MEDS_DEATH` + timestamp

**Current Status in event_configs.yaml:** ✅ Already configured
```yaml
hosp/patients:
  gender:
    code: [GENDER, col(gender)]
    time: null
  death:
    code: MEDS_DEATH
    time: col(dod)
```

---

### **Table 2: hosp/admissions**
**File:** `admissions.csv.gz`  
**Fields to Extract:**
- `subject_id` (links to patient)
- `hadm_id` (hospital admission ID - links to other tables)
- `admittime` → Token: `HOSPITAL_ADMISSION` + timestamp
- `dischtime` → Token: `HOSPITAL_DISCHARGE` + timestamp
- `admission_type` (EMERGENCY, ELECTIVE, URGENT, etc.)
- `admission_location` (where admitted from: ER, clinic, transfer)
- `discharge_location` (where discharged to: HOME, REHAB, SNF, etc.)
- `insurance` (Medicare, Medicaid, Private)
- `language` (primary language)
- `marital_status` (married, single, etc.)
- `race` (ethnicity)
- ⚠️ **Ziyi included "diagnoses" in admissions** - this likely refers to primary diagnosis stored in `diagnoses_icd` table

**Current Status in event_configs.yaml:** ✅ Already configured
```yaml
hosp/admissions:
  admission:
    code: [HOSPITAL_ADMISSION, col(admission_type), col(admission_location)]
    time: col(admittime)
  discharge:
    code: [HOSPITAL_DISCHARGE, col(discharge_location)]
    time: col(dischtime)
```

**⚠️ NOTE:** Currently includes race, insurance, language - may want to exclude for bias concerns

---

### **Table 3: hosp/diagnoses_icd**
**File:** `diagnoses_icd.csv.gz`  
**Fields to Extract:**
- `subject_id` (patient)
- `hadm_id` (admission)
- `icd_code` (ICD-9 or ICD-10 diagnosis code, e.g., "I50.9" = heart failure)
- `icd_version` (9 or 10)
- `seq_num` (sequence number - 1 = primary diagnosis, 2+ = secondary)

**Token Format:** `DIAGNOSIS//ICD//9//I50.9` or `DIAGNOSIS//ICD//10//I50.9`

**Current Status in event_configs.yaml:** ✅ Already configured
```yaml
hosp/diagnoses_icd:
  diagnosis:
    code: [DIAGNOSIS, ICD, col(icd_version), col(icd_code)]
    hadm_id: hadm_id
    time: col(dischtime)  # Assigned at discharge
```

**Dictionary Table:** `d_icd_diagnoses.csv.gz` - human-readable descriptions (optional)

---

### **Table 4: hosp/prescriptions** ⚠️ **NOT CURRENTLY CONFIGURED**
**File:** `prescriptions.csv.gz`  
**Fields to Extract:**
- `subject_id` (patient)
- `hadm_id` (admission)
- `pharmacy_id` (unique prescription ID)
- `starttime` (when medication started)
- `stoptime` (when medication stopped)
- `drug_type` (MAIN, BASE, ADDITIVE)
- `drug` (medication name, e.g., "Aspirin", "Vancomycin")
- `gsn` (Generic Sequence Number - drug identifier)
- `ndc` (National Drug Code)
- `prod_strength` (dosage strength)
- `form_val_disp` (form: tablet, IV, etc.)
- `dose_val_rx` (prescribed dose)
- `dose_unit_rx` (units: mg, mL, etc.)
- `route` (oral, IV, IM, etc.)

**Token Format (NEEDS CONFIGURATION):**
- Start: `MEDICATION//START//Vancomycin//IV` + starttime
- Stop: `MEDICATION//STOP//Vancomycin//IV` + stoptime

**Current Status:** ❌ **NOT in event_configs.yaml - NEED TO ADD**

---

### **Table 5: hosp/drgcodes**
**File:** `drgcodes.csv.gz`  
**Fields to Extract:**
- `subject_id` (patient)
- `hadm_id` (admission)
- `drg_type` (APR or HCFA - two different DRG systems)
- `drg_code` (3-digit code, e.g., "871" = sepsis)
- `description` (human-readable, e.g., "SEPTICEMIA WITHOUT MV 96+ HOURS W MCC")
- `drg_severity` (1-4 scale: minor, moderate, major, extreme)
- `drg_mortality` (1-4 scale: minor, moderate, major, extreme likelihood of dying)

**Token Format:** `DRG//APR//871//SEPTICEMIA`

**Current Status in event_configs.yaml:** ✅ Already configured
```yaml
hosp/drgcodes:
  drg:
    code: [DRG, col(drg_type), col(drg_code), col(description)]
    hadm_id: hadm_id
    time: col(dischtime)
    drg_severity: drg_severity
    drg_mortality: drg_mortality
```

**⚠️ DATA LEAKAGE WARNING:**
- `drg_mortality` = Healthcare system's mortality prediction (1-4 scale)
- This is a **direct predictor** of death outcome
- **RECOMMENDATION:** Exclude `drg_mortality` and `drg_severity` from input features

---

## ❌ **EXCLUDED FEATURES (NOT RED = EXCLUDE)**

### **From Core Module:**
- ❌ Race, Ethnicity (bias concerns)
- ❌ transfers (patient movement between wards)

### **From Hospital Module:**
- ❌ procedures_icd (surgical procedures)
- ❌ labevents (laboratory test results - 2.59 GB)
- ❌ emar / emar_detail (medication administration records)
- ❌ pharmacy (pharmacy dispensing - different from prescriptions)
- ❌ microbiologyevents (culture results)
- ❌ omr (patient-reported outcomes)
- ❌ poe / poe_detail (provider order entry)
- ❌ services (patient service type)
- ❌ provider (healthcare provider identifiers)
- ❌ hcpcsevents (outpatient procedure codes)

### **From ICU Module:**
- ❌ ALL ICU tables (chartevents, inputevents, outputevents, procedureevents, datetimeevents)

---

## 🔧 **IMPLEMENTATION TASKS**

### **Task 1: Add hosp/prescriptions to event_configs.yaml**
**Priority:** HIGH  
**Action:** Add prescriptions configuration to extract medication data

```yaml
hosp/prescriptions:
  medication_start:
    code:
      - MEDICATION
      - col(drug)
      - col(route)
    time: col(starttime)
    time_format: "%Y-%m-%d %H:%M:%S"
    hadm_id: hadm_id
    pharmacy_id: pharmacy_id
    dose: dose_val_rx
    dose_unit: dose_unit_rx
    drug_type: drug_type
```

### **Task 2: Remove Data Leakage Fields**
**Priority:** CRITICAL  
**Action:** Modify existing configurations to exclude leakage

**Changes Needed:**
1. **admissions table:** Remove or flag `discharge_location` if it contains "DIED"
2. **drgcodes table:** Remove `drg_mortality` and `drg_severity` from stored attributes
3. **patients table:** Keep `dod` (date of death) but only use as TARGET, not input feature

### **Task 3: Remove Bias Features (Optional)**
**Priority:** MEDIUM  
**Action:** Decide whether to exclude demographic bias

**Options:**
- Remove `race`, `language`, `insurance` from admissions
- Keep `marital_status` (less biased)
- Keep `gender` (approved by Ziyi)

### **Task 4: Create Filtered event_configs.yaml**
**Priority:** HIGH  
**Action:** Create new config file with only approved features

**Name:** `event_configs-ziyi-approved.yaml`

**Contents:**
- hosp/patients (gender, dod only)
- hosp/admissions (admission/discharge times, types, locations)
- hosp/diagnoses_icd (all ICD codes)
- hosp/prescriptions (NEW - medications)
- hosp/drgcodes (codes + descriptions, NO mortality/severity)

### **Task 5: Update Preprocessors (if needed)**
**Priority:** MEDIUM  
**Action:** Check if preprocessors need modifications for prescriptions table

**File:** `src/ethos/tokenize/mimic/preprocessors.py`

---

## 📊 **EXPECTED RESULTS AFTER IMPLEMENTATION**

### **Current Vocabulary (72 tokens):**
- 5 tables: patients, admissions, diagnoses_icd, procedures_icd, icustays
- Token types: GENDER, MEDS_DEATH, HOSPITAL_ADMISSION, HOSPITAL_DISCHARGE, DIAGNOSIS, PROCEDURE, ICU_ADMISSION, ICU_DISCHARGE

### **New Vocabulary (Estimated 300-500 tokens):**
- 5 tables: patients, admissions, diagnoses_icd, prescriptions, drgcodes
- Token types:
  - GENDER (2 tokens: M/F)
  - MEDS_DEATH (1 token)
  - HOSPITAL_ADMISSION + types (5-10 tokens)
  - HOSPITAL_DISCHARGE + locations (10-15 tokens)
  - DIAGNOSIS//ICD codes (100-200 most common codes)
  - MEDICATION + drug names (100-200 most common drugs)
  - DRG codes (50-100 most common DRG codes)

### **Dataset Size:**
- Current: 395 patients (sample)
- Target: 300,000+ patients (full MIMIC-IV)
- Expected training time: 2-4 hours on HyperGator GPU

### **Expected Accuracy:**
- Current: 7-28% (unstable, small dataset)
- After scaling: 50-70% (with 300K patients)

---

## 🎯 **NEXT STEPS - EXECUTION ORDER**

1. ✅ **Verify Ziyi's Requirements** - Confirm feature list is complete
2. 🔧 **Add prescriptions to event_configs.yaml** - Enable medication data
3. 🚨 **Remove data leakage fields** - Clean drg_mortality, drg_severity, discharge_location=DIED
4. 📝 **Create event_configs-ziyi-approved.yaml** - New clean configuration
5. 🧪 **Test on sample data** - Verify no errors with new config
6. 🚀 **Run full extraction on HyperGator** - Process all 300K patients
7. 📦 **Tokenize new dataset** - Create vocabulary and safetensors
8. 🏋️ **Train larger model** - Scale up model size for more data
9. 📊 **Evaluate results** - Check accuracy and predictions
10. ✅ **Report back to Ziyi** - Share results and model performance

---

**READY TO PROCEED?**
Confirm these are the exact features Ziyi wants, then I'll implement Tasks 1-4.
