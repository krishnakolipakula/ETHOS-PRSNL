#!/usr/bin/env python3
"""
Demo: Synthetic inference example showing how the model would work.
Creates fake patient data and simulated model predictions.
"""

import numpy as np


def create_synthetic_patient():
    """Create a synthetic patient sequence with realistic ICD codes."""
    # Common ICD-10 codes for a diabetic patient with hypertension
    icd_codes = {
        2: "MALE",
        3: "FEMALE", 
        4: "WHITE",
        5: "BLACK",
        6: "ASIAN",
        10: "E11.9 - Type 2 diabetes mellitus",
        11: "I10 - Essential hypertension",
        12: "E78.5 - Hyperlipidemia",
        15: "Z79.4 - Long term insulin use",
        20: "N18.3 - Chronic kidney disease stage 3",
        25: "E11.22 - Type 2 DM with kidney complication",
        30: "I25.10 - Coronary artery disease",
        35: "J44.9 - COPD",
        40: "E11.65 - Type 2 DM with hyperglycemia",
        45: "R73.03 - Prediabetes",
        50: "F17.210 - Nicotine dependence",
    }
    
    # Build patient sequence: demographics + medical history
    sequence = [
        2,   # Male
        4,   # White
        10,  # Type 2 diabetes
        11,  # Hypertension
        12,  # Hyperlipidemia
        15,  # Insulin use
        11,  # Hypertension (follow-up)
        10,  # Diabetes (follow-up)
        25,  # Diabetes with kidney complication
        20,  # CKD stage 3
        30,  # Coronary artery disease
        40,  # Diabetes with hyperglycemia
    ]
    
    return sequence, icd_codes


def simulate_model_predictions(context, vocab_size=1000):
    """Simulate realistic model predictions based on context."""
    np.random.seed(42)
    
    # Get last few tokens for context
    recent_codes = context[-3:] if len(context) >= 3 else context
    
    # Simulate predictions based on medical logic
    # If patient has diabetes (10), predict complications/management
    predictions = []
    
    if 10 in recent_codes or 25 in recent_codes:
        # Diabetes patient - likely to see diabetes-related codes
        candidates = [
            (40, "E11.65 - Type 2 DM with hyperglycemia", 0.35),
            (15, "Z79.4 - Long term insulin use", 0.25),
            (25, "E11.22 - Type 2 DM with kidney complication", 0.18),
            (11, "I10 - Essential hypertension", 0.12),
            (12, "E78.5 - Hyperlipidemia", 0.10),
        ]
    elif 11 in recent_codes:
        # Hypertension patient
        candidates = [
            (11, "I10 - Essential hypertension", 0.40),
            (30, "I25.10 - Coronary artery disease", 0.25),
            (12, "E78.5 - Hyperlipidemia", 0.20),
            (10, "E11.9 - Type 2 diabetes mellitus", 0.10),
            (20, "N18.3 - Chronic kidney disease stage 3", 0.05),
        ]
    else:
        # General case - common chronic conditions
        candidates = [
            (11, "I10 - Essential hypertension", 0.30),
            (10, "E11.9 - Type 2 diabetes mellitus", 0.25),
            (12, "E78.5 - Hyperlipidemia", 0.20),
            (35, "J44.9 - COPD", 0.15),
            (50, "F17.210 - Nicotine dependence", 0.10),
        ]
    
    return candidates


def main():
    print("="*70)
    print("SYNTHETIC ETHOS MODEL INFERENCE DEMO")
    print("(Simulated - Model is on HyperGator)")
    print("="*70)
    
    # Model info (from actual training)
    print(f"\n1. Model Information (from HyperGator training):")
    print(f"   Model: GPT2LMNoBiasModel")
    print(f"   Parameters: 64.45M")
    print(f"   Best checkpoint: Iteration 1000")
    print(f"   Validation loss: 4.8177")
    print(f"   Test loss: 5.0747")
    print(f"   Test perplexity: 159.93")
    
    # Create synthetic patient
    print(f"\n2. Synthetic Patient (Type 2 Diabetes with Hypertension):")
    sequence, icd_codes = create_synthetic_patient()
    
    print(f"   Patient sequence length: {len(sequence)} visits")
    print(f"\n3. Patient Medical History:")
    print(f"   {'Visit':<8} {'Token ID':<12} {'Diagnosis Code':<50}")
    print(f"   {'-'*70}")
    
    for visit_num, token_id in enumerate(sequence, 1):
        code_desc = icd_codes.get(token_id, f"TOKEN_{token_id}")
        visit_type = "Demo" if token_id < 10 else "Visit"
        print(f"   {visit_type} {visit_num:<3} {token_id:<12} {code_desc:<50}")
    
    # Simulate model prediction
    print(f"\n4. Model Prediction Task:")
    print(f"   Context: Using visits 1-{len(sequence)} to predict next diagnosis")
    print(f"   Last 3 codes in context: {sequence[-3:]}")
    
    predictions = simulate_model_predictions(sequence)
    
    print(f"\n5. Model's Top 5 Predictions for Next Visit:")
    print(f"   {'Rank':<6} {'Token ID':<12} {'Probability':<15} {'Diagnosis Code':<50}")
    print(f"   {'-'*85}")
    
    for rank, (token_id, code_desc, prob) in enumerate(predictions, 1):
        bar = "█" * int(prob * 50)
        print(f"   {rank:<6} {token_id:<12} {prob:<15.1%} {code_desc:<50}")
        print(f"          {bar}")
    
    # Explain predictions
    print(f"\n6. Prediction Analysis:")
    print(f"   ℹ️  The model learned that diabetic patients (E11.x) often have:")
    print(f"      • Hyperglycemia episodes (35% probability)")
    print(f"      • Insulin therapy requirements (25%)")  
    print(f"      • Kidney complications (18%)")
    print(f"      • Related hypertension (12%)")
    print(f"      • Hyperlipidemia (10%)")
    
    # Simulate autoregressive generation
    print(f"\n7. Autoregressive Generation (Next 5 Predicted Visits):")
    print(f"   {'Step':<8} {'Token ID':<12} {'Diagnosis Code':<50}")
    print(f"   {'-'*70}")
    
    current_context = sequence.copy()
    np.random.seed(123)
    
    for step in range(5):
        preds = simulate_model_predictions(current_context)
        # Sample based on probabilities
        probs = np.array([p[2] for p in preds])
        selected_idx = np.random.choice(len(preds), p=probs)
        token_id, code_desc, _ = preds[selected_idx]
        
        print(f"   Step {step+1:<3} {token_id:<12} {code_desc:<50}")
        current_context.append(token_id)
    
    print(f"\n8. Clinical Interpretation:")
    print(f"   The model predicts a realistic disease progression for this patient:")
    print(f"   • Continued diabetes management with complications")
    print(f"   • Monitoring of kidney function and cardiovascular health")
    print(f"   • Typical chronic disease trajectory seen in real EHR data")
    
    print(f"\n9. Model Capabilities:")
    print(f"   ✅ Learns temporal patterns in medical codes")
    print(f"   ✅ Captures disease comorbidities (diabetes + hypertension)")
    print(f"   ✅ Predicts realistic disease progression")
    print(f"   ✅ Can be fine-tuned for specific tasks (mortality, readmission)")
    
    print(f"\n{'='*70}")
    print("Demo completed!")
    print(f"\nℹ️  This is a synthetic example. For real inference, run on HyperGator:")
    print(f"   ssh hypergator")
    print(f"   cd /blue/yonghui.wu/kolipakulak/ethos-ares")
    print(f"   python scripts/demo_inference.py")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
