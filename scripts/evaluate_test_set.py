#!/usr/bin/env python3
"""
Evaluate trained model on test set.
Calculates perplexity and loss on held-out test data.
"""

import os
import sys
import torch
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ethos.model import GPT, GPTConfig
from src.ethos.data.dataloader import get_batch


def load_checkpoint(checkpoint_path):
    """Load model checkpoint."""
    print(f"Loading checkpoint from {checkpoint_path}")
    ckpt = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
    
    # Print checkpoint info
    print(f"Checkpoint info:")
    print(f"  Iteration: {ckpt.get('iter_num', 'N/A')}")
    print(f"  Best val loss: {ckpt.get('best_val_loss', 'N/A'):.4f}")
    
    return ckpt


def evaluate_on_split(model, data_dir, device, eval_iters=100, batch_size=16, block_size=2047):
    """Evaluate model on a data split."""
    model.eval()
    losses = []
    
    print(f"Evaluating on {data_dir}")
    print(f"  eval_iters: {eval_iters}")
    print(f"  batch_size: {batch_size}")
    print(f"  block_size: {block_size}")
    
    with torch.no_grad():
        for k in range(eval_iters):
            try:
                X, Y = get_batch(
                    data_dir=data_dir,
                    batch_size=batch_size,
                    block_size=block_size,
                    device=device
                )
                
                logits, loss = model(X, Y)
                losses.append(loss.item())
                
                if (k + 1) % 10 == 0:
                    print(f"  Iter {k+1}/{eval_iters}: loss = {loss.item():.4f}")
                    
            except Exception as e:
                print(f"  Error at iteration {k}: {e}")
                break
    
    if not losses:
        print("  ERROR: No valid batches evaluated!")
        return None
    
    mean_loss = np.mean(losses)
    std_loss = np.std(losses)
    perplexity = np.exp(mean_loss)
    
    print(f"\nResults:")
    print(f"  Loss: {mean_loss:.4f} ± {std_loss:.4f}")
    print(f"  Perplexity: {perplexity:.4f}")
    
    return {
        'loss': mean_loss,
        'loss_std': std_loss,
        'perplexity': perplexity,
        'num_batches': len(losses)
    }


def main():
    # Paths
    checkpoint_path = "outputs/2026-02-22/uf_training/best_model.pt"
    test_data_dir = "data/tokenized/uf_converted/test"
    val_data_dir = "data/tokenized/uf_converted/val"
    
    # Device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    # Load checkpoint
    ckpt = load_checkpoint(checkpoint_path)
    
    # Create model from checkpoint config
    model_config = ckpt['model_config']
    print(f"\nModel config:")
    for k, v in model_config.items():
        print(f"  {k}: {v}")
    
    # Initialize model
    gptconf = GPTConfig(**model_config)
    model = GPT(gptconf)
    
    # Load weights
    model.load_state_dict(ckpt['model'])
    model.to(device)
    model.eval()
    
    print(f"\nModel loaded successfully")
    print(f"Total parameters: {sum(p.numel() for p in model.parameters()) / 1e6:.2f}M")
    
    # Evaluation parameters
    eval_iters = 200  # More iterations for stable estimate
    batch_size = 16   # Same as training
    block_size = 2047  # Same as training
    
    # Evaluate on validation set (sanity check)
    print("\n" + "="*60)
    print("VALIDATION SET EVALUATION (sanity check)")
    print("="*60)
    val_results = evaluate_on_split(
        model, val_data_dir, device, 
        eval_iters=eval_iters,
        batch_size=batch_size,
        block_size=block_size
    )
    
    # Evaluate on test set
    print("\n" + "="*60)
    print("TEST SET EVALUATION (final performance)")
    print("="*60)
    test_results = evaluate_on_split(
        model, test_data_dir, device,
        eval_iters=eval_iters,
        batch_size=batch_size,
        block_size=block_size
    )
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Checkpoint: {checkpoint_path}")
    print(f"Iteration: {ckpt.get('iter_num', 'N/A')}")
    print(f"Training best val loss: {ckpt.get('best_val_loss', 'N/A'):.4f}")
    
    if val_results:
        print(f"\nValidation set (re-evaluated):")
        print(f"  Loss: {val_results['loss']:.4f} ± {val_results['loss_std']:.4f}")
        print(f"  Perplexity: {val_results['perplexity']:.4f}")
    
    if test_results:
        print(f"\nTest set (held-out):")
        print(f"  Loss: {test_results['loss']:.4f} ± {test_results['loss_std']:.4f}")
        print(f"  Perplexity: {test_results['perplexity']:.4f}")
        
        if val_results:
            gap = test_results['loss'] - val_results['loss']
            print(f"\nGeneralization gap (test - val): {gap:+.4f}")
            if abs(gap) < 0.2:
                print("  ✓ Good generalization!")
            elif gap > 0.2:
                print("  ⚠ Some overfitting detected")
            else:
                print("  ⚠ Test performance better than val (unusual)")


if __name__ == "__main__":
    main()
