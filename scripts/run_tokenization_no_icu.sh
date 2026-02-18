#!/bin/bash
#SBATCH --job-name=tokenize_no_icu
#SBATCH --output=/blue/yonghui.wu/kolipakulak/ethos-ares/logs/tokenize_no_icu_%j.log
#SBATCH --error=/blue/yonghui.wu/kolipakulak/ethos-ares/logs/tokenize_no_icu_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64gb
#SBATCH --time=06:00:00
#SBATCH --partition=hpg-default
#SBATCH --qos=yonghui.wu

# Initialize conda
module load conda
eval "$(conda shell.bash hook)"
conda activate ethos-ares

# Set paths
INPUT_DIR=/blue/yonghui.wu/kolipakulak/ethos-ares/data/mimic-meds-ziyi/data
OUTPUT_DIR=/blue/yonghui.wu/kolipakulak/ethos-ares/data/tokenized_datasets/mimic-ziyi-no-icu

# Log start time
echo "Started: $(date)"
echo "Tokenizing WITHOUT ICU stage (no icustay_id required)"

# Tokenize train data with custom config that skips ICU processing
ethos_tokenize -m \
    worker='range(0,8)' \
    input_dir=${INPUT_DIR}/train \
    output_dir=${OUTPUT_DIR} \
    out_fn=train \
    dataset=mimic_no_icu

echo ""
echo "Train tokenization complete. Starting test..."
echo ""

# Tokenize test data using vocabulary from train
ethos_tokenize -m \
    worker='range(0,2)' \
    input_dir=${INPUT_DIR}/test \
    vocab=${OUTPUT_DIR}/train \
    output_dir=${OUTPUT_DIR} \
    out_fn=test \
    dataset=mimic_no_icu

echo ""
echo "Completed: $(date)"
