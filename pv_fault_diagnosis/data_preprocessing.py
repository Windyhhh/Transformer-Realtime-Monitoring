"""
光伏故障诊断数据预处理模块
处理Excel格式的光伏时序数据，支持F0L（正常）和F1L（故障）数据
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pickle
import os


def load_and_label_data(file_path, label):
    """
    加载Excel数据并添加标签
    
    Args:
        file_path: Excel文件路径
        label: 数据标签 (0=正常, 1=故障)
    
    Returns:
        df: 包含标签的DataFrame
    """
    df = pd.read_excel(file_path)
    df['label'] = label
    return df


def preprocess_data(normal_file, fault_file, time_steps=30, test_size=0.1, val_size=0.1):
    """
    通用数据预处理函数
    
    Args:
        normal_file: 正常数据文件路径 (F0L.xlsx)
        fault_file: 故障数据文件路径 (F1L.xlsx)
        time_steps: 每个样本包含的时间步数
        test_size: 测试集比例
        val_size: 验证集比例
    
    Returns:
        X_train, X_val, X_test, y_train, y_val, y_test, scaler
    """
    print("Loading data...")
    # 1. 加载数据
    df_normal = load_and_label_data(normal_file, label=0)
    df_fault = load_and_label_data(fault_file, label=1)
    
    # 合并数据
    df = pd.concat([df_normal, df_fault], ignore_index=True)
    
    # 提取特征（排除Time和label列）
    feature_cols = [col for col in df.columns if col not in ['Time', 'label']]
    X = df[feature_cols].values  # (总样本数, 特征数)
    y = df['label'].values  # (总样本数,)
    
    print(f"Data shape: {X.shape}, Features: {len(feature_cols)}")
    print(f"Feature columns: {feature_cols}")
    print(f"Label distribution: Normal={np.sum(y==0)}, Fault={np.sum(y==1)}")
    
    # 2. 标准化
    print("Standardizing data...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 3. 构建时序样本
    print(f"Building time series samples with time_steps={time_steps}...")
    X_seq, y_seq = [], []
    for i in range(len(X_scaled) - time_steps):
        X_seq.append(X_scaled[i:i+time_steps, :])  # (time_steps, num_features)
        y_seq.append(y[i+time_steps-1])  # 用最后一个时刻的标签
    
    X_seq = np.array(X_seq)  # (样本数, time_steps, num_features)
    y_seq = np.array(y_seq)  # (样本数,)
    
    print(f"Sequence data shape: {X_seq.shape}")
    print(f"Sequence label distribution: Normal={np.sum(y_seq==0)}, Fault={np.sum(y_seq==1)}")
    
    # 4. 划分训练集、验证集、测试集
    print("Splitting data...")
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X_seq, y_seq, test_size=test_size, random_state=42, stratify=y_seq
    )
    
    val_size_adjusted = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=val_size_adjusted, 
        random_state=42, stratify=y_train_val
    )
    
    print(f"Train set: {X_train.shape}, Val set: {X_val.shape}, Test set: {X_test.shape}")
    print(f"Train labels: Normal={np.sum(y_train==0)}, Fault={np.sum(y_train==1)}")
    print(f"Val labels: Normal={np.sum(y_val==0)}, Fault={np.sum(y_val==1)}")
    print(f"Test labels: Normal={np.sum(y_test==0)}, Fault={np.sum(y_test==1)}")
    
    return X_train, X_val, X_test, y_train, y_val, y_test, scaler


def save_scaler(scaler, path):
    """保存标准化器"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"Scaler saved to {path}")


def load_scaler(path):
    """加载标准化器"""
    with open(path, 'rb') as f:
        scaler = pickle.load(f)
    return scaler

