#!/bin/bash
#SBATCH --job-name=eval_uf
#SBATCH --output=logs/eval_uf_%j.out
#SBATCH --error=logs/eval_uf_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32gb
#SBATCH --time=1:00:00
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --qos=yonghui.wu-b

cd /blue/yonghui.wu/kolipakulak/ethos-ares
source venv/bin/activate

echo "Starting evaluation at $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Running on: $(hostname)"

python scripts/evaluate_test_set.py

echo "Evaluation completed at $(date)"
