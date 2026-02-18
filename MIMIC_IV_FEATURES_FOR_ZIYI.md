# MIMIC-IV Features Used in ETHOS-ARES Model
**Date:** February 1, 2026  
**Purpose:** Review with Ziyi to determine which features should NOT be used for training  
**Request:** Please mark which features should be EXCLUDED from model training

---

## 📋 Quick Summary

**Current Sample (395 patients):**
- 5 tables used
- 72 tokens in vocabulary
- Features: Demographics, Diagnoses, Procedures, Admissions, ICU Stays

**Full MIMIC-IV Available on HyperGator:**
- **Location:** `/orange/yonghui.wu/chenziyi/MIMIC/mimiciv/3.1/`
- **14 hosp/ tables** (14 files checked/available)
- **ICU tables** available in separate directory
- **Dictionary tables** for code lookups (d_items, d_labitems, etc.)
- Thousands of potential features
- Need guidance on which to exclude

---

## 📂 **ACTUAL FILES AVAILABLE ON HYPERGATOR**

### **Hospital Module (hosp/) - 14 Tables Available:**

#### ✅ **Currently Used in Sample (5 tables):**
1. ✅ **patients.csv.gz** (2.84 MB) - Demographics
2. ✅ **admissions.csv.gz** (19.93 MB) - Hospital admissions/discharges
3. ✅ **diagnoses_icd.csv.gz** (33.56 MB) - ICD diagnosis codes
4. ✅ **procedures_icd.csv.gz** (7.78 MB) - ICD procedure codes
5. ✅ **icustays** (from icu/ directory) - ICU stays

#### 🔲 **Available But NOT in Sample (9 tables):**
6. 🔲 **labevents.csv.gz** (2.59 GB) ⭐ **LARGEST FILE** - All lab test results
7. 🔲 **emar.csv.gz** (811.31 MB) - Medication administration records
8. 🔲 **pharmacy.csv.gz** (525.71 MB) - Pharmacy dispensing records
9. 🔲 **microbiologyevents.csv.gz** (117.64 MB) - Microbiology cultures
10. 🔲 **transfers.csv.gz** (46.19 MB) - Patient transfers between units
11. 🔲 **drgcodes.csv.gz** (9.74 MB) - DRG billing codes
12. 🔲 **hcpcsevents.csv.gz** (2.16 MB) - HCPCS procedure codes
13. 🔲 **omr.csv.gz** (44.07 MB) - Online Medical Records
14. 🔲 **prescriptions.csv.gz** (606.30 MB) - Prescription orders

#### 📚 **Dictionary/Lookup Tables (5 available):**
- **d_hcpcs.csv.gz** (427.55 kB) - HCPCS code definitions
- **d_icd_diagnoses.csv.gz** (876.36 kB) - ICD diagnosis descriptions
- **d_icd_procedures.csv.gz** (589.19 kB) - ICD procedure descriptions
- **d_labitems.csv.gz** (13.17 kB) - Lab test definitions
- (Additional d_items from ICU module)

#### ❌ **Not Available/Not Checked:**
- emar_detail.csv.gz (748.16 MB)
- poe.csv.gz (666.59 MB) - Provider order entry
- poe_detail.csv.gz (55.27 MB)
- provider.csv.gz (127.33 kB) - Provider identifiers
- services.csv.gz (8.57 MB) - Service records

### **ICU Module (icu/) - Available in Separate Directory:**
- **icustays** - ICU stay tracking
- **chartevents** - Vital signs, assessments (time-series)
- **inputevents** - IV fluids, medications
- **outputevents** - Patient outputs (urine, etc.)
- **procedureevents** - ICU procedures
- **datetimeevents** - Time-stamped events
- **d_items** - ICU item definitions
- **caregiver** - Caregiver identifiers

---

## 🏥 MIMIC-IV Tables & Features (DETAILED)

### **1. DEMOGRAPHICS (hosp/patients)**

#### **Currently Using:**
- ✅ **Gender** (Male/Female)
- ✅ **Date of Birth** (year only) → Age calculation
- ✅ **Date of Death** (MEDS_DEATH)

#### **Available in Full MIMIC-IV (NOT currently used):**
- 🔲 Race/Ethnicity
- 🔲 Marital Status
- 🔲 Language
- 🔲 Anchor Age (age at anchor date)
- 🔲 Anchor Year

**❓ Question for Ziyi:** Should we EXCLUDE any demographic features? (e.g., race, language)

---

### **2. HOSPITAL ADMISSIONS (hosp/admissions)**

#### **Currently Using:**
- ✅ **Admission Type** (Emergency, Elective, Urgent, Observation)
- ✅ **Admission Location** (Emergency Dept, Transfer, Clinic Referral, etc.)
- ✅ **Admission Time** (timestamp)
- ✅ **Discharge Time** (timestamp)
- ✅ **Discharge Location** (Home, Died, Skilled Nursing, Hospice, etc.)

#### **Available in Full MIMIC-IV (NOT currently used):**
- 🔲 **Insurance Type** (Medicare, Medicaid, Private, Other)
- 🔲 **Language**
- 🔲 **Marital Status** (at admission)
- 🔲 **Race** (at admission)
- 🔲 **Hospital Expire Flag** (died in hospital)
- 🔲 **ED Registration Time**
- 🔲 **ED Out Time**

**❓ Question for Ziyi:** 
- Should we EXCLUDE insurance type? (might introduce bias)
- Should we EXCLUDE race/ethnicity from admissions? (redundant with patient table)

---

### **3. DIAGNOSES (hosp/diagnoses_icd)**

#### **Currently Using:**
- ✅ **ICD-9 Diagnosis Codes** (hierarchical grouping)
- ✅ **ICD-10 Diagnosis Codes** (hierarchical grouping)
- ✅ **Diagnosis Time** (discharge time)

#### **Processing:**
- Grouped into hierarchical categories (3-char, 4-char, 5-char codes)
- Only top frequent codes kept in vocabulary

**❓ Question for Ziyi:** 
- Should we EXCLUDE specific diagnosis categories? (e.g., mental health, substance abuse)
- Any codes that would be "data leakage" for mortality prediction?

---

### **4. PROCEDURES (hosp/procedures_icd)**

#### **Currently Using:**
- ✅ **ICD-9 Procedure Codes**
- ✅ **ICD-10 PCS Procedure Codes**
- ✅ **Procedure Date**

#### **Processing:**
- Grouped into hierarchical categories
- Only top frequent codes kept

**❓ Question for Ziyi:** 
- Should we EXCLUDE specific procedures? (e.g., palliative care codes that might leak outcome)
- Any procedures that are outcome indicators rather than predictors?

---

### **5. ICU STAYS (icu/icustays)**

#### **Currently Using:**
- ✅ **ICU Admission** (with care unit type: MICU, SICU, CCU, etc.)
- ✅ **ICU Discharge** (with last care unit)
- ✅ **ICU In Time**
- ✅ **ICU Out Time**

#### **Available (NOT currently used):**
- 🔲 **Length of Stay** (calculated field)
- 🔲 **First/Last Care Unit Match** (boolean)

**❓ Question for Ziyi:** 
- ICU admission itself predicts higher mortality - should we still use it?
- Should we EXCLUDE length of stay (calculated feature)?

---

### **6. DRG CODES (hosp/drgcodes)** ⚠️ NOT IN SAMPLE
**💰 File Size: 9.74 MB - Available on HyperGator**

#### **Available in Full MIMIC-IV:**
- 🔲 **DRG Type** (APR, HCFA, MS-DRG)
- 🔲 **DRG Code** (diagnostic related group)
- 🔲 **DRG Description** (text description of diagnosis group)
- 🔲 **DRG Severity** (1-4 scale: Minor, Moderate, Major, Extreme)
- 🔲 **DRG Mortality Risk** (1-4 scale: Minor, Moderate, Major, Extreme)

**What DRG Codes Represent:**
- Billing/reimbursement classification
- Groups diagnoses by resource intensity
- Includes severity and mortality risk scores assigned by billing system
- Assigned at DISCHARGE (retrospective coding)

**❓ Question for Ziyi:** 
- **CRITICAL:** DRG Mortality Risk directly predicts mortality! Should we EXCLUDE this? ⚠️⚠️⚠️
- Should we EXCLUDE DRG Severity? (might be outcome proxy)
- DRG codes assigned at discharge - timing issue for prediction?
- Should we use DRG category but NOT severity/mortality scores?

---

### **8. MEDICATIONS (hosp/emar + pharmacy)** ⚠️ NOT IN SAMPLE
**💊 File Sizes: emar.csv.gz (811.31 MB) + pharmacy.csv.gz (525.71 MB) - Available on HyperGator**

#### **Available in Full MIMIC-IV:**

**From emar.csv.gz (Medication Administration Record):**
- 🔲 **Medication Name** (thousands of medications)
- 🔲 **Administration Time** (when given)
- 🔲 **Event Type** (Started, Stopped, Administered, Paused, etc.)
- 🔲 **Route** (IV, Oral, Sublingual, Topical, etc.)
- 🔲 **Dose Amount**
- 🔲 **Dose Unit** (mg, mcg, units, etc.)

**From pharmacy.csv.gz (Pharmacy Dispensing):**
- 🔲 **Drug Name**
- 🔲 **Formulation** (Tablet, Solution, Injection, etc.)
- 🔲 **Dosage**
- 🔲 **Frequency**
- 🔲 **Start/Stop Times**
- 🔲 **Route of Administration**

**Common Medication Categories:**
- **Antibiotics** (Vancomycin, Ceftriaxone, Piperacillin-Tazobactam)
- **Anticoagulants** (Heparin, Warfarin, Enoxaparin)
- **Pain Management** (Morphine, Fentanyl, Acetaminophen)
- **Sedatives** (Propofol, Midazolam, Dexmedetomidine)
- **Cardiovascular** (Metoprolol, Furosemide, Lisinopril, Aspirin)
- **Vasopressors** (Norepinephrine, Dopamine, Epinephrine, Vasopressin)
- **Insulin** (Sliding scale, long-acting)
- **Anti-nausea** (Ondansetron, Metoclopramide)
- **Comfort Care** (Morphine, Atropine, Scopolamine patches)

**❓ Question for Ziyi:** 
- Should we EXCLUDE end-of-life/comfort care medications? (high-dose morphine, atropine)
- Should we EXCLUDE medications given AFTER DNR/comfort care order?
- Should we EXCLUDE sedatives used for terminal extubation?
- Vasopressors indicate critical state - include or exclude?
- Should we group medications by therapeutic class?

---

### **8. LABORATORY TESTS (hosp/labevents)** ⚠️ NOT IN SAMPLE

#### **Available in Full MIMIC-IV:**
- 🔲 **Lab Test Name** (1000+ different tests)
- 🔲 **Lab Value** (numeric)
- 🔲 **Lab Value Text** (interpretations)
- 🔲 **Units of Measurement**
- 🔲 **Reference Range**
- 🔲 **Abnormal Flag**

**Common Labs:**
- Hemoglobin, White Blood Cell Count, Platelet Count
- Sodium, Potassium, Chloride, Bicarbonate
- Creatinine, Blood Urea Nitrogen (kidney function)
- Glucose, Lactate
- Liver enzymes (AST, ALT, Bilirubin)
- Troponin (heart damage marker)
- Arterial Blood Gas (pH, pO2, pCO2)

**❓ Question for Ziyi:** 
- Should we EXCLUDE labs drawn AFTER patient declared brain dead?
- Should we EXCLUDE post-mortem labs?

---

### **9. VITAL SIGNS (icu/chartevents)** ⚠️ NOT IN SAMPLE

#### **Available in Full MIMIC-IV:**
- 🔲 **Heart Rate**
- 🔲 **Blood Pressure** (Systolic/Diastolic/Mean)
- 🔲 **Respiratory Rate**
- 🔲 **Temperature**
- 🔲 **SpO2** (Oxygen Saturation)
- 🔲 **Glasgow Coma Scale** (consciousness level)
- 🔲 **Pain Scale** (0-10)

**❓ Question for Ziyi:** 
- Should we EXCLUDE vitals measured during terminal extubation?
- Should we EXCLUDE "0" vitals (often indicate death/machine off)?

---

### **10. INFUSIONS (icu/inputevents)** ⚠️ NOT IN SAMPLE

#### **Available in Full MIMIC-IV:**
- 🔲 **Fluid Type** (Saline, Lactated Ringers, etc.)
- 🔲 **Vasopressors** (Norepinephrine, Dopamine, Epinephrine)
- 🔲 **Rate** (ml/hour)
- 🔲 **Duration**
- 🔲 **Start/Stop Times**

**❓ Question for Ziyi:** 
- Should we EXCLUDE vasopressor use? (strong mortality predictor)
- Should we EXCLUDE infusions during comfort care?

---

### **11. PROCEDURES (icu/procedureevents)** ⚠️ NOT IN SAMPLE

#### **Available in Full MIMIC-IV:**
- 🔲 **Intubation/Extubation**
- 🔲 **Central Line Placement**
- 🔲 **Dialysis**
- 🔲 **Chest Tube Placement**
- 🔲 **CPR/Resuscitation**

**❓ Question for Ziyi:** 
- Should we EXCLUDE CPR? (happens at time of death - data leakage)
- Should we EXCLUDE terminal extubation?

---

### **12. TRANSFERS (hosp/transfers)** ⚠️ NOT IN SAMPLE
**🏥 File Size: 46.19 MB - Available on HyperGator**

#### **Available in Full MIMIC-IV:**
- 🔲 **Care Unit Transfers** (Floor → ICU → Floor → ICU)
- 🔲 **Event Type** (Admit, Transfer, Discharge)
- 🔲 **Transfer Time** (in-time and out-time)
- 🔲 **Care Unit** (Medical Floor, MICU, SICU, CCU, etc.)

**Transfer Patterns:**
- Emergency Department → ICU (critical admission)
- Floor → ICU (clinical deterioration)
- ICU → Floor (improvement)
- ICU → ICU (unit change for specialty care)
- Floor → Morgue (death)
- ICU → Morgue (death)

**❓ Question for Ziyi:** 
- Should we EXCLUDE transfers TO morgue? (direct death indicator)
- Multiple ICU readmissions indicate severity - include or exclude?
- Should we count NUMBER of transfers as severity indicator?
- Exclude transfers happening AFTER terminal care decision?

---

### **13. EMERGENCY DEPARTMENT (ed/edstays)** ⚠️ NOT IN SAMPLE

#### **Available in Full MIMIC-IV:**
- 🔲 **ED Chief Complaint**
- 🔲 **ED Triage Acuity** (1-5 scale, 1=most urgent)
- 🔲 **ED Arrival Mode** (Ambulance, Walk-in)
- 🔲 **ED Length of Stay**
- 🔲 **ED Disposition** (Admitted, Discharged, Left AMA)

**❓ Question for Ziyi:** 
- Should we use ED triage acuity? (predicts severity)
- ED chief complaint for "cardiac arrest" - too predictive?

---

## 🎯 FEATURES IN OUR CURRENT VOCABULARY (72 tokens)

### **Time Intervals** (18 tokens)
```
5m-15m, 15m-45m, 45m-1h15m, 1h15m-2h, 2h-3h, 3h-5h, 5h-8h, 8h-12h, 
12h-18h, 18h-1d, 1d-2d, 2d-4d, 4d-7d, 7d-12d, 12d-20d, 20d-30d, 
30d-2mt, 2mt-6mt, =6mt
```
*Model-generated tokens to encode time between events*

### **Demographics** (2 tokens)
```
GENDER//F, GENDER//M
```

### **Admission Types** (3 tokens)
```
ADMISSION_TYPE//EMERGENCY
ADMISSION_TYPE//OBSERVATION  
ADMISSION_TYPE//SCHEDULED
```

### **Discharge Locations** (11 tokens)
```
HOSPITAL_DISCHARGE//HOME
HOSPITAL_DISCHARGE//DIED
HOSPITAL_DISCHARGE//HOME_HEALTH_CARE
HOSPITAL_DISCHARGE//SKILLED_NURSING_FACILITY
HOSPITAL_DISCHARGE//REHAB
HOSPITAL_DISCHARGE//HOSPICE
HOSPITAL_DISCHARGE//ACUTE_HOSPITAL
HOSPITAL_DISCHARGE//CHRONIC/LONG_TERM_ACUTE_CARE
HOSPITAL_DISCHARGE//OTHER_FACILITY
HOSPITAL_DISCHARGE//PSYCH_FACILITY
HOSPITAL_DISCHARGE//AGAINST_ADVICE
HOSPITAL_DISCHARGE//UNK
```

**❓ Question for Ziyi:** Should we EXCLUDE "HOSPITAL_DISCHARGE//DIED"? (This is the outcome!)

### **Insurance Types** (4 tokens)
```
INSURANCE//MEDICARE
INSURANCE//MEDICAID
INSURANCE//PRIVATE
INSURANCE//OTHER
```

**❓ Question for Ziyi:** Should we EXCLUDE insurance? (socioeconomic bias)

### **ICU Types** (8 tokens)
```
ICU_TYPE//MEDICAL_INTENSIVE_CARE_UNIT_(MICU)
ICU_TYPE//SURGICAL_INTENSIVE_CARE_UNIT_(SICU)
ICU_TYPE//MEDICAL/SURGICAL_INTENSIVE_CARE_UNIT_(MICU/SICU)
ICU_TYPE//CARDIAC_VASCULAR_INTENSIVE_CARE_UNIT_(CVICU)
ICU_TYPE//CORONARY_CARE_UNIT_(CCU)
ICU_TYPE//TRAUMA_SICU_(TSICU)
ICU_TYPE//NEURO_SURGICAL_INTENSIVE_CARE_UNIT_(NEURO_SICU)
ICU_TYPE//NEURO_INTERMEDIATE
ICU_TYPE//NEURO_STEPDOWN
```

### **ICD Code Types** (4 tokens)
```
ICD//CM//9    (Diagnosis ICD-9)
ICD//CM//10   (Diagnosis ICD-10)
ICD//PCS//9   (Procedure ICD-9)
ICD//PCS//10  (Procedure ICD-10-PCS)
```

### **Event Codes** (8 tokens)
```
MEDS_BIRTH              (Patient birth)
MEDS_DEATH              (Patient death) ⚠️ THIS IS THE OUTCOME!
HOSPITAL_ADMISSION       (Hospital admission event)
ICU_ADMISSION           (ICU admission event)
ICU_DISCHARGE           (ICU discharge event)
ED_REGISTRATION         (ED registration)
ED_OUT                  (ED discharge)
TIMELINE_END            (End of patient timeline)
```

**❓ Question for Ziyi:** Should MEDS_DEATH be EXCLUDED from input features? (It's the outcome!)

### **Quantile Bins** (10 tokens)
```
Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10
```
*Used to bin continuous values (age, lab values, etc.)*

### **Clinical Scores** (1 token)
```
SOFA (Sequential Organ Failure Assessment score)
```

**❓ Question for Ziyi:** Should we EXCLUDE SOFA score? (Strong mortality predictor)

---

## ⚠️ POTENTIAL DATA LEAKAGE CONCERNS

### **Features That Directly Indicate Outcome:**

1. **MEDS_DEATH** - This IS the outcome we're predicting! ❌ MUST EXCLUDE
2. **HOSPITAL_DISCHARGE//DIED** - Directly indicates death ❌ MUST EXCLUDE
3. **DRG Mortality Risk** - Healthcare system's mortality prediction ❌ LIKELY EXCLUDE
4. **SOFA Score** - Organ failure score correlates with mortality ⚠️ DISCUSS
5. **Vasopressor Use** - Strong severity indicator ⚠️ DISCUSS
6. **CPR/Resuscitation** - Happens during cardiac arrest ❌ LIKELY EXCLUDE
7. **Hospice Discharge** - End-of-life care ⚠️ DISCUSS
8. **Comfort Care Orders** - Palliative care ⚠️ DISCUSS

### **Features That Might Introduce Bias:**

1. **Race/Ethnicity** - Could perpetuate healthcare disparities ⚠️ DISCUSS
2. **Insurance Type** - Socioeconomic proxy ⚠️ DISCUSS
3. **Language** - Immigration status proxy ⚠️ DISCUSS
4. **Zip Code** (if available) - Geographic/economic bias ⚠️ DISCUSS

---

## 📝 QUESTIONS FOR ZIYI - CHECKLIST

Please mark each item:
- ✅ = INCLUDE in training
- ❌ = EXCLUDE from training
- ⚠️ = DISCUSS/CONDITIONAL

### **Demographics:**
- [ ] Gender (Male/Female)
- [ ] Age (from birth year)
- [ ] Race/Ethnicity
- [ ] Marital Status
- [ ] Language
- [ ] Insurance Type

### **Admission Features:**
- [ ] Admission Type (Emergency, Elective, etc.)
- [ ] Admission Location (ED, Transfer, etc.)
- [ ] Discharge Location (Home, SNF, Rehab, etc.)
- [ ] Discharge Location = DIED ⚠️ (This is the outcome!)

### **Clinical Events:**
- [ ] Hospital Admission/Discharge times
- [ ] ICU Admission/Discharge times
- [ ] ICU Type (MICU, SICU, CCU, etc.)
- [ ] ED Visits
- [ ] Care Unit Transfers

### **Diagnoses & Procedures:**
- [ ] ICD-9/10 Diagnosis Codes (all categories)
- [ ] ICD-9/10 Procedure Codes (all categories)
- [ ] DRG Codes
- [ ] DRG Severity Score ⚠️
- [ ] DRG Mortality Risk ⚠️ (Direct outcome predictor!)

### **Clinical Data (NOT in current sample):**
- [ ] Laboratory Test Results
- [ ] Vital Signs (HR, BP, RR, Temp, SpO2)
- [ ] Glasgow Coma Scale
- [ ] Pain Scores
- [ ] Medications (all types)
- [ ] End-of-life Medications (morphine, comfort meds) ⚠️
- [ ] Vasopressors (Norepinephrine, Dopamine, etc.) ⚠️
- [ ] IV Fluids/Infusions
- [ ] ICU Procedures (intubation, dialysis, central lines)
- [ ] CPR/Resuscitation ⚠️ (Happens at arrest)

### **Severity Scores:**
- [ ] SOFA Score ⚠️ (Organ failure assessment)
- [ ] APACHE Score (if available) ⚠️
- [ ] SAPS Score (if available) ⚠️

### **Outcome/Terminal Events (LEAKAGE RISK):**
- [ ] MEDS_DEATH token ⚠️ (This IS the outcome!)
- [ ] Terminal Extubation ⚠️
- [ ] Comfort Care/Palliative Orders ⚠️
- [ ] Hospice Transfers ⚠️
- [ ] Organ Donation Procedures ⚠️
- [ ] Post-mortem Labs/Vitals ⚠️

---

## 🎯 RECOMMENDED APPROACH

### **Step 1: Exclusions for Data Leakage**
Remove features that directly indicate or strongly predict the outcome:
- MEDS_DEATH token (in input sequence)
- HOSPITAL_DISCHARGE//DIED
- DRG Mortality Risk
- CPR/Resuscitation events
- Comfort care/hospice events happening AFTER prediction time
- Post-mortem measurements

### **Step 2: Exclusions for Bias Mitigation**
Consider removing features that could perpetuate healthcare disparities:
- Race/Ethnicity (controversial - discuss with ethics board)
- Insurance Type
- Language preference
- Zip code/geographic data

### **Step 3: Time-based Filtering**
For ICU Mortality prediction:
- Only use data BEFORE ICU admission + 24 hours
- Exclude any events happening AFTER the prediction time point
- Exclude "future" discharge locations

### **Step 4: Feature Engineering**
Keep temporal features that represent:
- Time since admission
- Time since ICU admission  
- Number of previous admissions
- Trajectory of lab values (improving vs worsening)

---

## 📊 NEXT STEPS AFTER ZIYI'S REVIEW

1. **Update MEDS Configuration:**
   - Modify `event_configs.yaml` to exclude specified features
   - Add filters for time-based exclusions

2. **Update Tokenization:**
   - Modify `preprocessors.py` to skip excluded features
   - Add checks to prevent leakage

3. **Re-run Pipeline:**
   - Extract MEDS with new config
   - Tokenize with excluded features
   - Verify vocabulary doesn't contain excluded tokens

4. **Validate:**
   - Check that outcome tokens don't appear in input sequences
### **Files Available on HyperGator (Confirmed):**
**Location:** `/orange/yonghui.wu/chenziyi/MIMIC/mimiciv/3.1/`

#### **Hospital Module (hosp/) - 14 Files:**
1. ✅ `admissions.csv.gz` (19.93 MB) - Hospital admissions/discharges
2. ✅ `patients.csv.gz` (2.84 MB) - Patient demographics
3. ✅ `diagnoses_icd.csv.gz` (33.56 MB) - ICD diagnosis codes
4. ✅ `procedures_icd.csv.gz` (7.78 MB) - ICD procedure codes
5. ✅ `drgcodes.csv.gz` (9.74 MB) - DRG billing codes
6. ✅ `labevents.csv.gz` (2.59 GB) - Laboratory test results ⭐ LARGEST
7. ✅ `emar.csv.gz` (811.31 MB) - Medication administration
8. ✅ `pharmacy.csv.gz` (525.71 MB) - Pharmacy dispensing
9. ✅ `microbiologyevents.csv.gz` (117.64 MB) - Microbiology cultures
10. ✅ `transfers.csv.gz` (46.19 MB) - Care unit transfers
11. ✅ `hcpcsevents.csv.gz` (2.16 MB) - HCPCS procedure codes
12. ✅ `omr.csv.gz` (44.07 MB) - Online Medical Records
13. ✅ `prescriptions.csv.gz` (606.30 MB) - Prescription orders
14. ✅ `d_*.csv.gz` (5 dictionary files) - Code definitions

#### **ICU Module (icu/) - Available in Separate Directory:**
- `icustays` - ICU stay tracking
- `chartevents` - Vital signs, assessments (time-series)
- `inputevents` - IV fluids, medications
- `outputevents` - Patient outputs (urine, etc.)
- `procedureevents` - ICU procedures
- `datetimeevents` - Time-stamped events
- `d_items` - ICU item definitions
- `caregiver` - Caregiver identifiers

### **Total Dataset Size Estimate:**
- **Hospital Module:** ~5.5 GB (compressed)
- **ICU Module:** ~20+ GB (chartevents is massive)
- **Total Patients:** ~300,000
- **Total Admissions:** ~500,000+
- **Total ICU Stays:** ~76,000+

### **Sample vs Full Comparison:**

| Feature | Sample (395 patients) | Full MIMIC-IV |
|---------|----------------------|---------------|
| Tables | 5 tables | 14+ tables |
| Data Size | 138 KB (MEDS) | 25+ GB (raw) |
| Patients | 395 | ~300,000 |
| Diagnoses | Thousands | Millions |
| Lab Tests | None | Millions (2.59 GB) |
| Medications | None | Millions (1.3+ GB) |
| Vocabulary | 72 tokens | 5,000+ tokens expected |

---

## 🎯 **SCALING RECOMMENDATIONS**

### **Phase 1: Add High-Value Tables (Moderate Increase)**
Add these 3 tables for better predictions:
1. **labevents** (2.59 GB) - Critical lab values
2. **transfers** (46.19 MB) - Clinical deterioration signals
3. **microbiologyevents** (117.64 MB) - Infection indicators

**Expected Impact:**
- Vocabulary: 72 → 500+ tokens
- Training time: 6 min → 2-3 hours
- Accuracy: 28% → 50-60% expected

### **Phase 2: Full Hospital Module (Large Increase)**
Add all hospital tables:
- Add medications (emar, pharmacy)
- Add DRG codes (without mortality scores)
- Full patient trajectories

**Expected Impact:**
- Vocabulary: 500 → 2,000+ tokens
- Training time: 3 hours → 12-24 hours
- Accuracy: 60% → 70-75% expected

### **Phase 3: ICU Module (Massive Increase)**
Add ICU time-series data:
- chartevents (vital signs every 1-5 minutes)
- inputevents (IV medications, fluids)
- procedureevents (procedures, devices)

**Expected Impact:**
- Vocabulary: 2,000 → 5,000+ tokens
- Training time: 24 hours → 3-5 days
- Accuracy: 75% → 80-85% (publication-ready)

---

**Contact:** Krishna Kolipakulа  
**Date:** February 1, 2026  
**Awaiting Feedback From:** Ziyi

**Next Steps After Ziyi's Response:**
1. Update `event_configs.yaml` to exclude specified features
2. Modify `preprocessors.py` for feature filtering
3. Re-extract MEDS with approved feature set
4. Re-tokenize with updated vocabulary
5. Train and evaluate on clean feature setdure timestamps
15. `icu/inputevents` - IV fluids and medications
16. `icu/outputevents` - Fluid output
17. `icu/procedureevents` - ICU procedures

---

**Contact:** Krishna Kolipakulа  
**Date:** February 1, 2026  
**Awaiting Feedback From:** Ziyi
