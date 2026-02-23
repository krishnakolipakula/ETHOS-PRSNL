#!/bin/bash
#SBATCH --job-name=eval_uf_gpu
#SBATCH --output=logs/eval_uf_gpu_%j.out
#SBATCH --error=logs/eval_uf_gpu_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16gb
#SBATCH --time=0:30:00
#SBATCH --partition=hpg-turin
#SBATCH --gres=gpu:l4:1
#SBATCH --qos=yonghui.wu-b

cd /blue/yonghui.wu/kolipakulak/ethos-ares
source venv/bin/activate

echo "Starting GPU evaluation at $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Running on: $(hostname)"
echo "GPU: $CUDA_VISIBLE_DEVICES"

python scripts/evaluate_test_set.py

echo "Evaluation completed at $(date)"
