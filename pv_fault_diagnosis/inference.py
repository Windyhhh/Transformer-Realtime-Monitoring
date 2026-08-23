"""
推理脚本：用于新数据的故障诊断预测
"""

import torch
import numpy as np
import pandas as pd
from model import TransformerClassifier
from data_preprocessing import load_scaler


class FaultDiagnosisPredictor:
    """故障诊断预测器"""
    
    def __init__(self, model_path='models/best_model.pth', 
                 scaler_path='models/scaler.pkl',
                 input_dim=13, d_model=64, nhead=4, num_layers=2):
        """
        初始化预测器
        
        Args:
            model_path: 模型权重路径
            scaler_path: 标准化器路径
            input_dim: 输入特征维度
            d_model: Transformer维度
            nhead: 多头注意力头数
            num_layers: Transformer层数
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # 加载模型
        self.model = TransformerClassifier(
            input_dim=input_dim,
            d_model=d_model,
            nhead=nhead,
            num_layers=num_layers
        )
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        
        # 加载标准化器
        self.scaler = load_scaler(scaler_path)
        
        print(f"✓ Model loaded from {model_path}")
        print(f"✓ Scaler loaded from {scaler_path}")
        print(f"✓ Using device: {self.device}")
    
    def predict(self, X, time_steps=30):
        """
        预测
        
        Args:
            X: 输入数据 (样本数, 特征数) 或 (样本数, time_steps, 特征数)
            time_steps: 时间步数
        
        Returns:
            predictions: 预测结果 (样本数,)
            probabilities: 预测概率 (样本数,)
        """
        # 标准化
        if X.ndim == 2:
            X_scaled = self.scaler.transform(X)
            # 构建时序样本
            X_seq = []
            for i in range(len(X_scaled) - time_steps + 1):
                X_seq.append(X_scaled[i:i+time_steps, :])
            X_seq = np.array(X_seq)
        else:
            X_scaled = self.scaler.transform(X.reshape(-1, X.shape[-1]))
            X_seq = X_scaled.reshape(X.shape)
        
        # 转换为Tensor
        X_tensor = torch.tensor(X_seq, dtype=torch.float32).to(self.device)
        
        # 预测
        with torch.no_grad():
            outputs = self.model(X_tensor)
            probabilities = outputs.cpu().numpy().flatten()
            predictions = (probabilities > 0.5).astype(int)
        
        return predictions, probabilities
    
    def predict_from_file(self, file_path, time_steps=30):
        """
        从Excel文件预测
        
        Args:
            file_path: Excel文件路径
            time_steps: 时间步数
        
        Returns:
            predictions, probabilities
        """
        df = pd.read_excel(file_path)
        feature_cols = [col for col in df.columns if col not in ['Time', 'label']]
        X = df[feature_cols].values
        
        return self.predict(X, time_steps=time_steps)


def main():
    """示例：使用预测器进行推理"""
    print("\n" + "="*70)
    print("故障诊断推理示例")
    print("="*70)
    
    # 初始化预测器
    predictor = FaultDiagnosisPredictor()
    
    # 从测试数据预测
    print("\n从F0L.xlsx（正常数据）预测:")
    predictions, probs = predictor.predict_from_file('../F0L.xlsx')
    print(f"  预测结果: {predictions[:10]}")
    print(f"  预测概率: {probs[:10]}")
    print(f"  故障率: {np.mean(predictions):.2%}")
    
    print("\n从F1L.xlsx（故障数据）预测:")
    predictions, probs = predictor.predict_from_file('../F1L.xlsx')
    print(f"  预测结果: {predictions[:10]}")
    print(f"  预测概率: {probs[:10]}")
    print(f"  故障率: {np.mean(predictions):.2%}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()

