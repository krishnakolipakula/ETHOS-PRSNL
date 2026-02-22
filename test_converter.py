#!/usr/bin/env python3
"""
Test the UF to ETHOS converter with sample data
"""

import numpy as np
from convert_uf_to_ethos_format import UFToETHOSConverter

# Create sample triplet data matching UF format
# Patient 11 example: [patient_id, age_days, code]
sample_data = np.array([
    [11, 0, 1],      # Healthy (outcome)
    [11, 0, 2],      # M (gender)
    [11, 31594, 100], # ICD code at age 86.5 years
    [11, 31594, 101], # Another code same day
    [11, 31670, 200], # Code 76 days later
    [11, 31670, 201],
    [11, 31670, 202],
    [11, 32169, 300], # Code 499 days after previous
], dtype=np.uint32)

print("Sample triplet data:")
print(sample_data)
print(f"\nShape: {sample_data.shape}")

# Simulate the converter's grouping and sequencing
from collections import defaultdict

# Group by patient
patient_records = []
for row in sample_data:
    patient_id, age_days, code = row
    patient_records.append((age_days, code))

print(f"\nPatient {patient_id} records:")
for age, code in patient_records:
    print(f"  Age: {age:6d}, Code: {code}")

# Separate demographics and events
demographics = []
events = []

for age_days, code in patient_records:
    if age_days == 0:
        demographics.append(code)
    else:
        events.append((age_days, code))

events.sort(key=lambda x: x[0])

print(f"\nDemographics: {demographics}")
print(f"Events: {events}")

# Build sequence with time interval bins
TIME_BINS = [
    (0, 1, "TIME_0-1DAY"),
    (1, 7, "TIME_1-7DAY"),
    (7, 30, "TIME_7-30DAY"),
    (30, 365, "TIME_30-365DAY"),
    (365, 730, "TIME_1-2YEAR"),
    (730, float('inf'), "TIME_2+YEAR")
]

def quantize_time_delta(days_delta):
    for min_days, max_days, name in TIME_BINS:
        if min_days <= days_delta < max_days:
            return name
    return "TIME_2+YEAR"

sequence = []
sequence.extend(demographics)

# Group events by age
encounters = defaultdict(list)
for age_days, code in events:
    encounters[age_days].append(code)

print(f"\nEncounters grouped by age:")
for age, codes in sorted(encounters.items()):
    print(f"  Age {age}: {codes}")

# Add encounters with time intervals
prev_age = 0
print(f"\nBuilding sequence:")
print(f"  Demographics: {demographics}")

for age_days in sorted(encounters.keys()):
    time_delta = age_days - prev_age
    time_token = quantize_time_delta(time_delta)
    
    print(f"  Time delta: {time_delta} days → {time_token}")
    print(f"    Codes at age {age_days}: {encounters[age_days]}")
    
    sequence.append(time_token)
    sequence.extend(encounters[age_days])
    
    prev_age = age_days

print(f"\nFinal sequence:")
print(sequence)
print(f"Length: {len(sequence)}")

print("\nExpected structure:")
print("[demographics, TIME_TOKEN1, codes..., TIME_TOKEN2, codes..., TIME_TOKEN3, codes...]")
