"""
Transformer模型用于光伏故障分类
"""

import torch
import torch.nn as nn
import numpy as np


class PositionalEncoding(nn.Module):
    """
    位置编码：向时序数据中加入时间位置信息
    """
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)  # 偶数维度用正弦
        if d_model % 2 == 1:
            pe[:, 0, 1::2] = torch.cos(position * div_term[:-1])  # 奇数维度用余弦
        else:
            pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x):
        """
        Args:
            x: (time_steps, batch_size, d_model)
        Returns:
            x + positional encoding
        """
        x = x + self.pe[:x.size(0)]
        return x


class TransformerClassifier(nn.Module):
    """
    Transformer故障分类器
    """
    def __init__(self, input_dim=13, d_model=64, nhead=4, num_layers=2, 
                 dim_feedforward=128, dropout=0.3, num_classes=1):
        """
        Args:
            input_dim: 输入特征维度
            d_model: Transformer内部维度
            nhead: 多头注意力头数
            num_layers: Transformer编码器层数
            dim_feedforward: 前馈网络维度
            dropout: Dropout比例
            num_classes: 分类类数（二分类=1）
        """
        super().__init__()
        self.d_model = d_model
        
        # 1. 将输入特征维度映射到d_model
        self.linear_in = nn.Linear(input_dim, d_model)
        
        # 2. 位置编码
        self.pos_encoder = PositionalEncoding(d_model)
        
        # 3. Transformer编码器
        encoder_layers = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=False
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layers, 
            num_layers=num_layers
        )
        
        # 4. 分类头
        self.classifier = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, num_classes),
            nn.Sigmoid()  # 输出0-1概率
        )

    def forward(self, x):
        """
        Args:
            x: (batch_size, time_steps, input_dim)
        Returns:
            output: (batch_size, 1) 二分类概率
        """
        batch_size, time_steps, _ = x.shape
        
        # 转换为Transformer需要的格式：(time_steps, batch_size, d_model)
        x = self.linear_in(x)  # (batch_size, time_steps, d_model)
        x = x.permute(1, 0, 2)  # (time_steps, batch_size, d_model)
        
        # 加入位置编码
        x = self.pos_encoder(x)
        
        # Transformer编码
        x = self.transformer_encoder(x)  # (time_steps, batch_size, d_model)
        
        # 聚合时序特征（全局平均池化）
        x = x.mean(dim=0)  # (batch_size, d_model)
        
        # 分类
        out = self.classifier(x)  # (batch_size, 1)
        return out

