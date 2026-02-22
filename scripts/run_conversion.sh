#!/bin/bash
#SBATCH --job-name=convert_uf
#SBATCH --output=logs/convert_uf_%j.out
#SBATCH --error=logs/convert_uf_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64GB
#SBATCH --time=4:00:00
#SBATCH --partition=hpg-default
#SBATCH --qos=yonghui.wu

# UF to ETHOS Converter Job
# Converts UF triplet format to ETHOS sequences with time interval quantization

echo "========================================"
echo "UF TO ETHOS CONVERSION JOB"
echo "========================================"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start time: $(date)"
echo ""

# Setup environment
module load python/3.11
source venv/bin/activate

echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo ""

# Install required packages if needed
pip install --quiet safetensors tqdm pandas numpy torch

# Run conversion
echo "Starting conversion..."
python convert_uf_to_ethos_format.py \
    --input_dir /orange/yonghui.wu/chenziyi/Note_Structure/Delphi_0515/data/mimic \
    --output_dir /blue/yonghui.wu/kolipakulak/ethos-ares/data/tokenized/uf_converted \
    --vocab_map /orange/yonghui.wu/chenziyi/Note_Structure/Delphi_0515/data/mimic/mimic_map.csv \
    --max_seq_length 2048 \
    --shard_size 10000

echo ""
echo "========================================"
echo "CONVERSION COMPLETE"
echo "End time: $(date)"
echo "========================================"
