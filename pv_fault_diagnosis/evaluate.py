"""
模型评估和可视化
"""

import torch
import numpy as np
import matplotlib.pyplot as plt
import json
from sklearn.metrics import (
    classification_report, confusion_matrix, 
    ConfusionMatrixDisplay, roc_curve, auc, roc_auc_score
)
import os

from model import TransformerClassifier


def evaluate_model(model, test_loader, device):
    """
    在测试集上评估模型
    """
    model.eval()
    y_true = []
    y_pred_proba = []
    y_pred = []
    
    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            X_batch = X_batch.to(device)
            outputs = model(X_batch)
            
            y_true.extend(y_batch.cpu().numpy())
            y_pred_proba.extend(outputs.cpu().numpy().flatten())
            y_pred.extend((outputs > 0.5).float().cpu().numpy().flatten())
    
    y_true = np.array(y_true)
    y_pred_proba = np.array(y_pred_proba)
    y_pred = np.array(y_pred)
    
    return y_true, y_pred, y_pred_proba


def plot_training_history(history, save_path="results/training_curves.png"):
    """绘制训练曲线"""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 损失曲线
    axes[0].plot(history['train_losses'], label='Train Loss', linewidth=2)
    axes[0].plot(history['val_losses'], label='Val Loss', linewidth=2)
    axes[0].set_xlabel('Epoch', fontsize=12)
    axes[0].set_ylabel('Loss', fontsize=12)
    axes[0].set_title('Training and Validation Loss', fontsize=14, fontweight='bold')
    axes[0].legend(fontsize=11)
    axes[0].grid(True, alpha=0.3)
    
    # 准确率曲线
    axes[1].plot(history['train_accs'], label='Train Accuracy', linewidth=2)
    axes[1].plot(history['val_accs'], label='Val Accuracy', linewidth=2)
    axes[1].set_xlabel('Epoch', fontsize=12)
    axes[1].set_ylabel('Accuracy', fontsize=12)
    axes[1].set_title('Training and Validation Accuracy', fontsize=14, fontweight='bold')
    axes[1].legend(fontsize=11)
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Training curves saved to {save_path}")
    plt.close()


def plot_confusion_matrix(y_true, y_pred, save_path="results/confusion_matrix.png"):
    """绘制混淆矩阵"""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    cm = confusion_matrix(y_true, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Normal', 'Fault'])
    
    fig, ax = plt.subplots(figsize=(8, 6))
    disp.plot(ax=ax, cmap='Blues', values_format='d')
    ax.set_title('Confusion Matrix', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Confusion matrix saved to {save_path}")
    plt.close()


def plot_roc_curve(y_true, y_pred_proba, save_path="results/roc_curve.png"):
    """绘制ROC曲线"""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
    roc_auc = auc(fpr, tpr)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.3f})')
    ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate', fontsize=12)
    ax.set_ylabel('True Positive Rate', fontsize=12)
    ax.set_title('ROC Curve', fontsize=14, fontweight='bold')
    ax.legend(loc="lower right", fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"ROC curve saved to {save_path}")
    plt.close()
    
    return roc_auc


def print_evaluation_report(y_true, y_pred, y_pred_proba):
    """打印评估报告"""
    print("\n" + "="*60)
    print("EVALUATION REPORT")
    print("="*60)
    
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=['Normal', 'Fault']))
    
    roc_auc = roc_auc_score(y_true, y_pred_proba)
    print(f"ROC AUC Score: {roc_auc:.4f}")
    
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    print(f"\nSensitivity (Recall): {sensitivity:.4f}")
    print(f"Specificity: {specificity:.4f}")
    print("="*60 + "\n")


def save_evaluation_results(y_true, y_pred, y_pred_proba, save_path="results/evaluation_results.json"):
    """保存评估结果"""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    results = {
        'accuracy': float(np.mean(y_true == y_pred)),
        'precision': float(tp / (tp + fp)),
        'recall': float(tp / (tp + fn)),
        'f1_score': float(2 * tp / (2 * tp + fp + fn)),
        'roc_auc': float(roc_auc_score(y_true, y_pred_proba)),
        'sensitivity': float(tp / (tp + fn)),
        'specificity': float(tn / (tn + fp)),
        'confusion_matrix': cm.tolist()
    }
    
    with open(save_path, 'w') as f:
        json.dump(results, f, indent=4)
    
    print(f"Evaluation results saved to {save_path}")
    return results

