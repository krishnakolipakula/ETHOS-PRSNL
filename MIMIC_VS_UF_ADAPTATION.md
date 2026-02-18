# MIMIC vs UF Data Adaptation Checklist

**Purpose:** Track what needs to be modified when adapting ETHOS from MIMIC to UF data

---

## 📊 Data Format Comparison

### MIMIC-IV Structure

| Table/File | Key Columns | Purpose |
|------------|-------------|---------|
| **hosp/admissions.csv** | subject_id, hadm_id, admittime, dischtime, admission_type | Hospital admissions |
| **hosp/diagnoses_icd.csv** | subject_id, hadm_id, icd_code, icd_version | Diagnoses (ICD-9/10) |
| **hosp/procedures_icd.csv** | subject_id, hadm_id, icd_code, icd_version | Procedures (ICD-9/10) |
| **hosp/prescriptions.csv** | subject_id, hadm_id, drug, drug_code | Medications |
| **hosp/labevents.csv** | subject_id, hadm_id, itemid, charttime, value, valuenum | Lab results |
| **icu/icustays.csv** | subject_id, hadm_id, icustay_id, intime, outtime | ICU stays |
| **patients.csv** | subject_id, gender, anchor_age, dod | Patient demographics |

### UF Data Structure (TO BE DOCUMENTED)

| Table/File | Key Columns | Purpose | Notes |
|------------|-------------|---------|-------|
| **TBD** | patient_id, encounter_id, admit_date, discharge_date | Hospital admissions | Document when received |
| **TBD** | patient_id, encounter_id, icd10_code | Diagnoses | Check if ICD-9 exists |
| **TBD** | patient_id, encounter_id, cpt_code | Procedures | Different from MIMIC |
| **TBD** | patient_id, encounter_id, medication, ndc_code | Medications | Check coding system |
| **TBD** | patient_id, encounter_id, loinc_code, result_time, value | Lab results | Check if LOINC used |
| **TBD** | patient_id, encounter_id, icu_in, icu_out | ICU stays | If available |
| **TBD** | patient_id, gender, age, race | Demographics | Privacy restrictions? |

**Action Items:**
- [ ] Request UF data dictionary
- [ ] Document all available tables
- [ ] Identify primary/foreign keys
- [ ] Check date/time formats
- [ ] Verify identifier anonymization

---

## 🔧 Code Components Requiring Modification

### 1. MEDS Extraction Scripts

#### Location: `scripts/meds/mimic/`

**Files to Create/Modify for UF:**

| MIMIC File | New UF File | Modifications Needed |
|------------|-------------|---------------------|
| `scripts/meds/mimic/pre_MEDS.py` | `scripts/meds/uf/pre_MEDS.py` | - Change input file paths<br>- Update column name mappings<br>- Modify ID field names |
| `scripts/meds/mimic/configs/event_configs.yaml` | `scripts/meds/uf/configs/event_configs.yaml` | - Define UF event types<br>- Map UF tables to MEDS events |
| `scripts/meds/mimic/configs/extract_MIMIC.yaml` | `scripts/meds/uf/configs/extract_UF.yaml` | - Change file paths<br>- Update subject/encounter ID fields |
| `scripts/meds/run_mimic.sh` | `scripts/meds/run_uf.sh` | - Update paths and variables<br>- Change function calls |

**Key Changes:**

```yaml
# MIMIC event config example
events:
  - name: admission
    input: hosp/admissions.csv
    columns:
      subject_id: subject_id
      time: admittime
      code: admission_type

# UF event config (TO BE CREATED)
events:
  - name: admission
    input: encounters/encounters.csv  # <-- Change input file
    columns:
      subject_id: patient_id         # <-- Change ID field
      time: admit_datetime           # <-- Change time field
      code: encounter_type           # <-- Change code field
```

---

### 2. Dataset Preprocessing Configuration

#### Location: `src/ethos/configs/dataset/mimic.yaml`

**Create:** `src/ethos/configs/dataset/uf.yaml`

**Preprocessing Steps to Review:**

| MIMIC Preprocessing | Keep/Modify/Remove | UF Adaptation |
|---------------------|-------------------|---------------|
| `LabData.retain_only_test_with_numeric_result` | **Keep** | May need to adjust filtering logic |
| `TransferData.retain_only_transfer_and_admit_types` | **Modify** | Update admission type codes for UF |
| `DemographicData.retrieve_demographics_from_hosp_adm` | **Modify** | Change source table and field names |
| `DemographicData.process_race` | **Keep/Modify** | Check UF race categories |
| `DemographicData.process_marital_status` | **Keep** | If UF has this data |
| `InpatientData.process_drg_codes` | **Keep** | If UF provides DRG codes |
| `DiagnosesData.convert_icd_9_to_10` | **Remove?** | If UF only has ICD-10 |
| `ProcedureData.convert_icd_9_to_10` | **Remove?** | If UF only has ICD-10 |
| `MedicationData.convert_to_atc` | **Modify** | Change from MIMIC drug codes to UF system |

**Code Filtering - MUST REVIEW:**

```yaml
# MIMIC filters out these prefixes
codes_to_remove:
  - INFUSION_
  - SUBJECT_WEIGHT_AT_INFUSION
  - Weight
  - Height
  - eGFR
  - PROCEDURE//START
  - PROCEDURE//END
  - MEDICATION//START//
  - SUBJECT_FLUID_OUTPUT//

# UF: Review if same filters apply
# Add UF-specific codes to filter
```

---

### 3. Dataset Classes

#### Location: `src/ethos/datasets/`

**Files Requiring Review/Modification:**

| File | MIMIC-Specific? | Modification Level | Notes |
|------|----------------|-------------------|-------|
| `base.py` | Partial | **Low** | Check identifier properties |
| `mimic_icu.py` | Yes | **High** | Create `uf_icu.py` if needed |
| `hospital_mortality.py` | Partial | **Medium** | Update death detection logic |
| `readmission.py` | Partial | **Medium** | Update encounter linkage |
| `ed.py` | Yes | **High** | Create `uf_ed.py` if UF has ED data |
| `extensions.py` | No | **None** | General utilities |

**Key Properties to Check in `base.py`:**

```python
# MIMIC-specific properties (lines 84-94)
@property
def is_mimic(self):
    return "hadm_id" in self._data.shards[0]

@property
def hadm_id(self):  # Hospital admission ID
    if not self.is_mimic:
        raise AttributeError("It's not MIMIC, no 'hadm_id' available.")
    return self._data.hadm_id

@property
def icu_stay_id(self):
    if not self.is_mimic:
        raise AttributeError("It's not MIMIC, no 'icustay_id' available.")
    return self._data.icu_stay_id
```

**UF Adaptation:**

```python
# Add UF-specific properties
@property
def is_uf(self):
    return "encounter_id" in self._data.shards[0]  # Update field name

@property
def encounter_id(self):  # UF encounter ID
    if not self.is_uf:
        raise AttributeError("It's not UF data, no 'encounter_id' available.")
    return self._data.encounter_id

# Add other UF-specific identifiers as needed
```

---

### 4. Task Definitions

#### Location: `src/ethos/inference/constants.py`

**Review Task Definitions:**

Current MIMIC tasks:
1. Hospital Mortality
2. ICU Admission (within 24h)
3. 30-day Readmission
4. Prolonged Length of Stay
5. ED Discharge

**UF Tasks (TO BE DEFINED):**

| Task | Keep? | Definition | Label Source |
|------|-------|------------|--------------|
| Hospital Mortality | ✓ Yes | Same as MIMIC | Death within admission |
| ICU Admission | ✓ Yes | Same as MIMIC | ICU transfer within 24h |
| 30-day Readmission | ✓ Yes | Same as MIMIC | Readmission within 30 days |
| Prolonged LoS | ✓ Yes | May need different threshold | Define threshold for UF |
| ED Discharge | ? TBD | If UF has ED data | TBD |
| **New UF Task 1** | ? TBD | Define based on UF needs | TBD |
| **New UF Task 2** | ? TBD | Define based on UF needs | TBD |

**Action Items:**
- [ ] Confirm which tasks UF wants to predict
- [ ] Define labeling criteria for each task
- [ ] Document data availability for each task
- [ ] Determine evaluation metrics

---

### 5. Preprocessing Transforms

#### Location: `src/ethos/tokenize/mimic/preprocessors.py`

**MIMIC-Specific Transforms:**

```python
# Example: Processing MIMIC admission types
class InpatientData:
    @staticmethod
    def process_hospital_admissions(df: pl.DataFrame) -> pl.DataFrame:
        # MIMIC-specific admission type codes
        admission_types = {
            'AMBULATORY OBSERVATION': 'OBSERVATION',
            'DIRECT EMER.': 'EMERGENCY',
            'DIRECT OBSERVATION': 'OBSERVATION',
            # ... more MIMIC codes
        }
        return df.with_columns(...)
```

**UF Adaptation:**

```python
# Create: src/ethos/tokenize/uf/preprocessors.py
class UfInpatientData:
    @staticmethod
    def process_hospital_admissions(df: pl.DataFrame) -> pl.DataFrame:
        # UF-specific admission type codes (TO BE DEFINED)
        admission_types = {
            'TBD': 'TBD',
            # Document UF codes when data arrives
        }
        return df.with_columns(...)
```

---

## 🗂️ Files to Create for UF

### New Directory Structure:

```
scripts/
└── meds/
    └── uf/                                    # NEW
        ├── pre_MEDS.py                        # NEW
        ├── README.md                          # NEW
        └── configs/                           # NEW
            ├── event_configs.yaml             # NEW
            ├── extract_UF.yaml                # NEW
            └── pre_MEDS.yaml                  # NEW

src/ethos/
├── configs/
│   └── dataset/
│       └── uf.yaml                            # NEW
├── datasets/
│   ├── uf_icu.py                             # NEW (if needed)
│   └── uf_ed.py                              # NEW (if needed)
└── tokenize/
    └── uf/                                    # NEW
        ├── __init__.py                        # NEW
        └── preprocessors.py                   # NEW
```

---

## 🎯 Adaptation Checklist

### Phase 1: Data Understanding (Before Coding)

- [ ] Receive UF data and documentation
- [ ] Document all available tables and schemas
- [ ] Map UF fields to MIMIC equivalents
- [ ] Identify coding systems (ICD, CPT, LOINC, NDC, etc.)
- [ ] Understand patient/encounter identifiers
- [ ] Document date/time formats
- [ ] Check for data quality issues
- [ ] Confirm privacy/anonymization requirements

### Phase 2: MEDS Extraction Setup

- [ ] Create `scripts/meds/uf/` directory
- [ ] Write UF-specific event configuration
- [ ] Adapt pre_MEDS.py for UF data
- [ ] Create UF extraction script
- [ ] Test on small UF subset
- [ ] Verify MEDS output format
- [ ] Check train/test split

### Phase 3: Tokenization Configuration

- [ ] Create `src/ethos/configs/dataset/uf.yaml`
- [ ] Review all preprocessing transforms
- [ ] Create UF-specific preprocessors if needed
- [ ] Test code filtering rules
- [ ] Verify vocabulary generation
- [ ] Check quantization thresholds

### Phase 4: Dataset Classes

- [ ] Update `base.py` for UF identifiers
- [ ] Create UF-specific dataset classes
- [ ] Adapt task label generation
- [ ] Test data loading

### Phase 5: Model Training

- [ ] Verify tokenized data format
- [ ] Test training with small UF data
- [ ] Monitor training metrics
- [ ] Compare to MIMIC results

### Phase 6: Inference & Evaluation

- [ ] Define UF-specific tasks
- [ ] Implement task-specific labeling
- [ ] Run inference on test set
- [ ] Calculate evaluation metrics
- [ ] Compare with baselines

---

## 🔍 Key Questions to Answer

### Data Questions:
1. What is the patient identifier in UF data?
2. What is the encounter/admission identifier?
3. Are there separate inpatient/outpatient/ED encounters?
4. How are diagnoses coded? (ICD-9, ICD-10, both?)
5. How are procedures coded? (ICD, CPT, both?)
6. How are medications coded? (NDC, RxNorm, custom?)
7. How are lab tests identified? (LOINC, local codes?)
8. What is the time span of the data?
9. How many patients are in the dataset?
10. What outcomes/labels are available?

### Clinical Questions:
1. What prediction tasks does UF need?
2. What is the prediction horizon? (24h, 48h, 30 days?)
3. What is the clinical use case?
4. Who will use the predictions?
5. What performance is clinically acceptable?
6. Are there fairness/equity requirements?

### Technical Questions:
1. How will the model be deployed?
2. What computational resources are available?
3. What is the update frequency for the model?
4. Are there real-time prediction requirements?
5. What is the acceptable latency?

---

## 📝 Documentation to Create

1. **UF_DATA_DICTIONARY.md**
   - Complete field descriptions
   - Data types and ranges
   - Missing data patterns
   - Code systems used

2. **UF_TO_MIMIC_MAPPING.md**
   - Direct field mappings
   - Equivalent concepts
   - Non-mappable elements

3. **UF_PREPROCESSING_RULES.md**
   - Data cleaning steps
   - Code normalization rules
   - Filtering criteria
   - Quality checks

4. **UF_TASK_DEFINITIONS.md**
   - Prediction task descriptions
   - Label generation logic
   - Inclusion/exclusion criteria
   - Evaluation metrics

---

## 🚦 Decision Points

### Critical Decisions to Make:

1. **Vocabulary Strategy:**
   - [ ] Option A: Use MIMIC vocabulary + UF extensions
   - [ ] Option B: Build completely new UF vocabulary
   - [ ] Option C: Use shared medical ontology (UMLS?)

2. **Model Training Strategy:**
   - [ ] Option A: Train from scratch on UF data
   - [ ] Option B: Fine-tune MIMIC-trained model
   - [ ] Option C: Multi-task learning (MIMIC + UF)

3. **Code System Handling:**
   - [ ] Option A: Keep original UF codes
   - [ ] Option B: Convert all to standard (ICD-10, ATC, LOINC)
   - [ ] Option C: Mixed approach

4. **Identifier Privacy:**
   - [ ] Confirm all identifiers are anonymized
   - [ ] Document re-identification risks
   - [ ] Implement additional privacy measures if needed

---

## 📊 Expected Differences (MIMIC vs UF)

| Aspect | MIMIC | UF (Expected) | Impact |
|--------|-------|---------------|--------|
| **Patient Population** | Academic medical center | Regional health system | Different disease prevalence |
| **Coding Practices** | ICD-9/10 mix | Likely ICD-10 only | Simpler preprocessing |
| **Data Completeness** | High | TBD | May affect model performance |
| **ICU Data** | Detailed | May be limited | Affects ICU admission task |
| **ED Data** | MIMIC-IV-ED extension | TBD | May or may not be available |
| **Medication Data** | Detailed infusion data | TBD | Different granularity |
| **Lab Data** | Rich | TBD | Different test panels |

---

## ✅ Success Criteria

**Minimum Viable Adaptation:**
- [ ] MEDS extraction works on UF data
- [ ] Tokenization produces valid timelines
- [ ] Model trains without errors
- [ ] At least one prediction task works
- [ ] Performance > random baseline

**Full Adaptation:**
- [ ] All desired tasks implemented
- [ ] Performance comparable to MIMIC results
- [ ] Clinical validation passed
- [ ] Documentation complete
- [ ] Ready for deployment

---

**Next Steps:**
1. Wait for UF data access
2. Start with MIMIC experiments (use Strategic Plan)
3. Document MIMIC pipeline thoroughly
4. Create UF-specific configurations when data arrives
5. Iterate and validate

**Last Updated:** January 24, 2026
