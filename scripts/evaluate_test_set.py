#!/usr/bin/env python3
"""
Evaluate trained model on test set.
Calculates perplexity and loss on held-out test data.
"""

import torch
import numpy as np
from torch.utils.data import DataLoader

from ethos.utils import load_model_checkpoint
from ethos.datasets import TimelineDataset


def evaluate_on_dataset(model, dataloader, device, eval_iters=200):
    """Evaluate model on a dataset."""
    model.eval()
    losses = []
    
    print(f"Evaluating with {eval_iters} iterations")
    
    with torch.no_grad():
        for k, (x, y) in enumerate(dataloader):
            if k >= eval_iters:
                break
                
            try:
                # Move to device
                y = y.to(device, non_blocking=True)
                if isinstance(x, list):
                    x = (x[0].to(device, non_blocking=True), x[1].to(device, non_blocking=True))
                else:
                    x = x.to(device, non_blocking=True)
                
                output = model(x, y)
                loss = output.loss
                losses.append(loss.item())
                
                if (k + 1) % 20 == 0:
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
    train_data_dir = "data/tokenized/uf_converted/train"
    test_data_dir = "data/tokenized/uf_converted/test"
    
    # Config
    batch_size = 16
    n_positions = 2047
    eval_iters = 200
    
    # Device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    # Load checkpoint using ETHOS utility
    print(f"\nLoading checkpoint from {checkpoint_path}")
    model, checkpoint = load_model_checkpoint(checkpoint_path, map_location=device)
    
    # Print checkpoint info
    print(f"\nCheckpoint info:")
    print(f"  Iteration: {checkpoint.get('iter_num', 'N/A')}")
    print(f"  Best val loss: {checkpoint.get('best_val_loss', 'N/A'):.4f}")
    print(f"  Model parameters: {model.num_parameters() / 1e6:.2f}M")
    
    model.to(device)
    model.eval()
    
    # Load datasets
    print(f"\nLoading datasets...")
    print(f"  Train dir: {train_data_dir}")
    print(f"  Test dir: {test_data_dir}")
    
    # Load train dataset to get vocab
    train_dataset = TimelineDataset(
        train_data_dir,
        n_positions=n_positions,
        is_encoder_decoder=False,
    )
    
    vocab = train_dataset.vocab
    print(f"  Vocabulary size: {len(vocab)}")
    
    # Split train into train/val (same as training)
    val_size = 0.04  # Same as training
    train_dataset, val_dataset = train_dataset.train_test_split(val_size)
    
    # Load test dataset with the same vocab
    # Copy vocab file to test directory if needed
    import shutil
    from pathlib import Path
    test_path = Path(test_data_dir)
    train_path = Path(train_data_dir)
    
    # Find vocab file in train directory
    vocab_files = list(train_path.glob("vocab_t*.csv"))
    if vocab_files:
        vocab_src = vocab_files[0]
        vocab_dst = test_path / vocab_src.name
        if not vocab_dst.exists():
            print(f"  Copying vocab file to test directory...")
            shutil.copy(vocab_src, vocab_dst)
    
    test_dataset = TimelineDataset(
        test_data_dir,
        n_positions=n_positions,
        is_encoder_decoder=False,
    )
    
    # Create dataloaders
    val_dataloader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
    )
    
    test_dataloader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
    )
    
    print(f"\nDataset sizes:")
    print(f"  Validation: {len(val_dataset)} samples")
    print(f"  Test: {len(test_dataset)} samples")
    
    # Evaluate on validation set (sanity check)
    print("\n" + "="*60)
    print("VALIDATION SET EVALUATION (sanity check)")
    print("="*60)
    val_results = evaluate_on_dataset(model, val_dataloader, device, eval_iters=eval_iters)
    
    # Evaluate on test set
    print("\n" + "="*60)
    print("TEST SET EVALUATION (final performance)")
    print("="*60)
    test_results = evaluate_on_dataset(model, test_dataloader, device, eval_iters=eval_iters)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Checkpoint: {checkpoint_path}")
    print(f"Iteration: {checkpoint.get('iter_num', 'N/A')}")
    print(f"Training best val loss: {checkpoint.get('best_val_loss', 'N/A'):.4f}")
    
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
