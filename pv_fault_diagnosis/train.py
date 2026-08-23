"""
模型训练脚本
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
from tqdm import tqdm
import os
import json

from data_preprocessing import preprocess_data, save_scaler
from model import TransformerClassifier


def train_epoch(model, train_loader, criterion, optimizer, device):
    """训练一个epoch"""
    model.train()
    train_loss = 0.0
    train_correct = 0
    total_samples = 0
    
    for X_batch, y_batch in tqdm(train_loader, desc="Training", leave=False):
        X_batch = X_batch.to(device)
        y_batch = y_batch.to(device).unsqueeze(1)
        
        optimizer.zero_grad()
        outputs = model(X_batch)
        loss = criterion(outputs, y_batch)
        loss.backward()
        optimizer.step()
        
        train_loss += loss.item() * X_batch.size(0)
        preds = (outputs > 0.5).float()
        train_correct += (preds == y_batch).sum().item()
        total_samples += X_batch.size(0)
    
    return train_loss / total_samples, train_correct / total_samples


def validate(model, val_loader, criterion, device):
    """验证"""
    model.eval()
    val_loss = 0.0
    val_correct = 0
    total_samples = 0
    
    with torch.no_grad():
        for X_batch, y_batch in val_loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device).unsqueeze(1)
            
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            
            val_loss += loss.item() * X_batch.size(0)
            preds = (outputs > 0.5).float()
            val_correct += (preds == y_batch).sum().item()
            total_samples += X_batch.size(0)
    
    return val_loss / total_samples, val_correct / total_samples


def train_model(normal_file, fault_file, epochs=50, batch_size=32, 
                time_steps=30, d_model=64, nhead=4, num_layers=2):
    """
    完整的训练流程
    """
    # 设置设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # 1. 数据预处理
    print("\n=== Data Preprocessing ===")
    X_train, X_val, X_test, y_train, y_val, y_test, scaler = preprocess_data(
        normal_file, fault_file, time_steps=time_steps
    )
    
    # 保存scaler
    os.makedirs("models", exist_ok=True)
    save_scaler(scaler, "models/scaler.pkl")
    
    # 2. 转换为Tensor
    X_train_t = torch.tensor(X_train, dtype=torch.float32)
    X_val_t = torch.tensor(X_val, dtype=torch.float32)
    X_test_t = torch.tensor(X_test, dtype=torch.float32)
    y_train_t = torch.tensor(y_train, dtype=torch.float32)
    y_val_t = torch.tensor(y_val, dtype=torch.float32)
    y_test_t = torch.tensor(y_test, dtype=torch.float32)
    
    # 3. 构建DataLoader
    train_dataset = TensorDataset(X_train_t, y_train_t)
    val_dataset = TensorDataset(X_val_t, y_val_t)
    test_dataset = TensorDataset(X_test_t, y_test_t)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)
    
    # 4. 初始化模型
    print("\n=== Model Initialization ===")
    input_dim = X_train.shape[2]  # 特征维度
    model = TransformerClassifier(
        input_dim=input_dim,
        d_model=d_model,
        nhead=nhead,
        num_layers=num_layers
    )
    model.to(device)
    print(f"Model: {model}")
    print(f"Input dimension: {input_dim}")
    
    # 5. 训练配置
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    
    # 6. 训练循环
    print("\n=== Training ===")
    best_val_acc = 0.0
    patience = 10
    patience_counter = 0
    
    train_losses, val_losses = [], []
    train_accs, val_accs = [], []
    
    for epoch in range(epochs):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = validate(model, val_loader, criterion, device)
        
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        train_accs.append(train_acc)
        val_accs.append(val_acc)
        
        print(f"Epoch {epoch+1}/{epochs}: "
              f"Train Loss {train_loss:.4f}, Acc {train_acc:.4f} | "
              f"Val Loss {val_loss:.4f}, Acc {val_acc:.4f}")
        
        # 保存最佳模型
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            torch.save(model.state_dict(), "models/best_model.pth")
            print(f"  ✓ Best model saved (Val Acc: {val_acc:.4f})")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch+1}")
                break
    
    # 7. 保存训练历史
    history = {
        'train_losses': train_losses,
        'val_losses': val_losses,
        'train_accs': train_accs,
        'val_accs': val_accs
    }
    with open("logs/training_history.json", "w") as f:
        json.dump(history, f)
    
    return model, test_loader, device, history


if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    
    model, test_loader, device, history = train_model(
        normal_file="../F0L.xlsx",
        fault_file="../F1L.xlsx",
        epochs=50,
        batch_size=32,
        time_steps=30,
        d_model=64,
        nhead=4,
        num_layers=2
    )
    
    print("\n=== Training Complete ===")
    print(f"Best validation accuracy: {max(history['val_accs']):.4f}")

