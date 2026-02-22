#!/bin/bash
#SBATCH --job-name=train_uf
#SBATCH --output=logs/train_uf_%j.out
#SBATCH --error=logs/train_uf_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:l4:2
#SBATCH --mem=64GB
#SBATCH --time=8:00:00
#SBATCH --partition=hpg-turin
#SBATCH --qos=yonghui.wu

# UF Data Training Job
# Training ETHOS on converted UF sequences

echo "========================================"
echo "UF TRAINING JOB"
echo "========================================"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "GPUs: $SLURM_GPUS"
echo "Start time: $(date)"
echo ""

# Setup environment
module load python/3.11
source venv/bin/activate

echo "Python version: $(python --version)"
echo "PyTorch version: $(python -c 'import torch; print(torch.__version__)')"
echo "CUDA available: $(python -c 'import torch; print(torch.cuda.is_available())')"
echo "GPU count: $(python -c 'import torch; print(torch.cuda.device_count())')"
echo "Working directory: $(pwd)"
echo ""

# Train with UF config
echo "Starting training with UF data..."
ethos_train \
    data_fp=data/tokenized/uf_converted/train \
    val_size=5000 \
    out_dir=outputs/$(date +%Y-%m-%d)/uf_training \
    max_iters=5000 \
    batch_size=32 \
    gradient_accumulation_steps=8 \
    n_layer=6 \
    n_embd=768 \
    n_head=12 \
    n_positions=2048 \
    dropout=0.3 \
    lr=0.0006 \
    min_lr=0.00001 \
    eval_interval=500 \
    log_interval=10 \
    warmup_iters=500 \
    lr_decay_iters=4500 \
    device=cuda \
    dtype=bfloat16 \
    wandb_log=false

echo ""
echo "========================================"
echo "TRAINING COMPLETE"
echo "End time: $(date)"
echo "========================================"
