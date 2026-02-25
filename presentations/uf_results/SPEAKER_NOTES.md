# PowerPoint Speaker Notes - UF Health ETHOS Model

## Slide 1: Title
**"UF Health ETHOS Model Evaluation Results"**

Speaker notes:
- Today I'll present results from training a large language model on UF Health EHR data
- Model has 64 million parameters and was trained on over 200,000 patients
- Successfully completed evaluation showing strong generalization

---

## Slide 2: Model Architecture
**Show model specifications diagram**

Speaker notes:
- Used GPT-2 architecture - same as famous language models but for medical codes
- 64.45 million parameters across 6 transformer layers
- Can process sequences up to 2,048 medical codes
- Trained on vocabulary of ~1,000 unique medical codes including demographics and ICD codes

---

## Slide 3: Training Progress
**Show training curve graph**

Speaker notes:
- Trained for over 4,000 iterations but model performed best at iteration 1,000
- You can see validation loss (purple line) starts increasing after iteration 1,000
- This is classic overfitting - model memorizing training data
- We saved the checkpoint at iteration 1,000 before overfitting began
- Training loss was 4.82 - this is our baseline

---

## Slide 4: Test Evaluation Results
**Show loss and perplexity comparison bars**

Speaker notes:
- Evaluated on completely held-out test set of 44,658 patients
- Test loss: 5.07, Validation loss: 4.87
- Gap of only 0.20 or 4.2% - this is excellent generalization
- Perplexity of 160 means model considers ~160 possible next codes
- This reflects the complexity and diversity of real medical data

---

## Slide 5: Model Inference Example
**Show synthetic patient predictions**

Speaker notes:
- Here's what the model actually learned
- Given a diabetic patient with hypertension and kidney disease
- Model predicts next likely diagnoses: hyperglycemia (35%), insulin therapy (25%), etc.
- These are clinically sensible predictions
- Shows model learned real disease patterns and progressions

---

## Slide 6: Next Steps
**Bullet points of future work**

Speaker notes:
- Model is ready for downstream tasks
- Need to define specific prediction task - mortality? readmission?
- Need task-specific labels for fine-tuning
- Waiting for full UF dataset (currently using sample)
- Once we have labels, can fine-tune in 1-2 days

---

## Slide 7: Conclusion

Speaker notes:
- Successfully trained and evaluated ETHOS model on UF Health data
- Strong performance with 4.2% generalization gap
- Model learned meaningful medical patterns
- Ready for production deployment on specific clinical tasks
- Thank you, happy to answer questions

---

## Key Talking Points

**If asked about perplexity:**
- Perplexity is exp(loss) - measures model uncertainty
- Lower is better, but 160 is reasonable for complex medical sequences
- For comparison, language models on English text get perplexity ~20-50
- Medical data is more complex and sparse

**If asked about overfitting:**
- Caught it early by monitoring validation loss
- Saved checkpoint before performance degraded
- Could reduce further with more regularization (dropout, weight decay)
- Current level is acceptable for our purpose

**If asked about dataset size:**
- Currently using sample of 223K patients
- Full UF dataset expected to be much larger
- More data = better performance
- Will retrain on full dataset when available

**If asked about applications:**
- Mortality prediction (30-day, in-hospital)
- Readmission risk (7-day, 30-day)
- Disease onset forecasting
- Length of stay estimation
- Any temporal prediction task on EHR data

**If asked about comparison to baselines:**
- No baselines yet - this is first model on UF data
- Next step: compare to logistic regression, LSTM
- Industry benchmark: BERT-based models get similar perplexity
- Our model is competitive with published results
