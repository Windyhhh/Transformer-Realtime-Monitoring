"""
光伏故障诊断主程序
完整的训练、评估和可视化流程
"""

import os
import sys
import json
import torch
from model import TransformerClassifier
from train import train_model
from evaluate import (
    evaluate_model, plot_training_history, plot_confusion_matrix,
    plot_roc_curve, print_evaluation_report, save_evaluation_results
)


def main():
    """主函数"""
    print("\n" + "="*70)
    print("光伏故障诊断系统 - Transformer深度学习方案")
    print("="*70)
    
    # 配置参数
    config = {
        'normal_file': '../F0L.xlsx',
        'fault_file': '../F1L.xlsx',
        'epochs': 50,
        'batch_size': 32,
        'time_steps': 30,
        'd_model': 64,
        'nhead': 4,
        'num_layers': 2,
        'learning_rate': 1e-4
    }
    
    print("\n配置参数:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    # 创建必要的目录
    os.makedirs('models', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    
    # 保存配置
    with open('logs/config.json', 'w') as f:
        json.dump(config, f, indent=4)
    
    # 1. 训练模型
    print("\n" + "="*70)
    print("第一步：模型训练")
    print("="*70)
    
    model, test_loader, device, history = train_model(
        normal_file=config['normal_file'],
        fault_file=config['fault_file'],
        epochs=config['epochs'],
        batch_size=config['batch_size'],
        time_steps=config['time_steps'],
        d_model=config['d_model'],
        nhead=config['nhead'],
        num_layers=config['num_layers']
    )
    
    # 2. 加载最佳模型
    print("\n" + "="*70)
    print("第二步：加载最佳模型")
    print("="*70)
    
    model.load_state_dict(torch.load('models/best_model.pth'))
    print("✓ Best model loaded")
    
    # 3. 评估模型
    print("\n" + "="*70)
    print("第三步：模型评估")
    print("="*70)
    
    y_true, y_pred, y_pred_proba = evaluate_model(model, test_loader, device)
    print_evaluation_report(y_true, y_pred, y_pred_proba)
    
    # 4. 可视化
    print("\n" + "="*70)
    print("第四步：结果可视化")
    print("="*70)
    
    plot_training_history(history)
    plot_confusion_matrix(y_true, y_pred)
    roc_auc = plot_roc_curve(y_true, y_pred_proba)
    
    # 5. 保存评估结果
    results = save_evaluation_results(y_true, y_pred, y_pred_proba)
    
    # 6. 总结
    print("\n" + "="*70)
    print("训练完成总结")
    print("="*70)
    print(f"✓ 最佳验证准确率: {max(history['val_accs']):.4f}")
    print(f"✓ 测试集准确率: {results['accuracy']:.4f}")
    print(f"✓ ROC AUC: {results['roc_auc']:.4f}")
    print(f"✓ 灵敏度 (Recall): {results['sensitivity']:.4f}")
    print(f"✓ 特异性 (Specificity): {results['specificity']:.4f}")
    print(f"\n✓ 模型已保存到: models/best_model.pth")
    print(f"✓ 训练曲线已保存到: results/training_curves.png")
    print(f"✓ 混淆矩阵已保存到: results/confusion_matrix.png")
    print(f"✓ ROC曲线已保存到: results/roc_curve.png")
    print(f"✓ 评估结果已保存到: results/evaluation_results.json")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

