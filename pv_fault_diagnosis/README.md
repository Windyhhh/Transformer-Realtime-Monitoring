# 光伏故障诊断深度学习方案（基于Transformer）

基于Transformer架构的光伏模块故障分类系统，支持时序数据处理和实时诊断。

## 项目结构

```
pv_fault_diagnosis/
├── data_preprocessing.py    # 数据预处理模块
├── model.py                 # Transformer模型定义
├── train.py                 # 训练脚本
├── evaluate.py              # 评估和可视化
├── inference.py             # 推理脚本
├── main.py                  # 主程序
├── requirements.txt         # 依赖包
├── models/                  # 保存训练好的模型
├── logs/                    # 训练日志
└── results/                 # 评估结果和可视化图表
```

## 快速开始

### 1. 环境配置

```bash
# 创建conda环境（已完成）
conda activate pv_diagnosis

# 安装依赖（已完成）
pip install -r requirements.txt
```

### 2. 运行完整流程

```bash
cd pv_fault_diagnosis
python main.py
```

这将执行：
- 数据预处理（加载F0L.xlsx和F1L.xlsx）
- 模型训练（50个epoch）
- 模型评估（测试集）
- 结果可视化（训练曲线、混淆矩阵、ROC曲线）

### 3. 单独运行各模块

#### 仅训练模型
```bash
python train.py
```

#### 推理预测
```bash
python inference.py
```

## 数据格式说明

### 输入数据格式
- **文件格式**: Excel (.xlsx)
- **特征列**: 13个变量（Ipv, Vpv, Vdc, ia, ib, ic, va, vb, vc, Iabc, If, Vabc, Vf）
- **时间步**: 每个样本包含30个连续时刻的采样
- **标签**: 0（正常）/ 1（故障）

### 数据文件
- `F0L.xlsx`: 正常工作数据（143,715行）
- `F1L.xlsx`: 故障数据（129,013行）

## 模型配置

### 默认参数
```python
d_model = 64          # Transformer内部维度
nhead = 4             # 多头注意力头数
num_layers = 2        # Transformer编码器层数
time_steps = 30       # 时间步数
batch_size = 32       # 批大小
epochs = 50           # 训练轮数
learning_rate = 1e-4  # 学习率
```

### 参数调整指南

修改 `main.py` 中的 `config` 字典：

```python
config = {
    'epochs': 100,        # 增加训练轮数
    'd_model': 128,       # 增加模型容量
    'nhead': 8,           # 增加注意力头数
    'num_layers': 3,      # 增加编码器层数
    'batch_size': 64,     # 增加批大小
}
```

## 输出文件

### 模型文件
- `models/best_model.pth`: 最佳模型权重
- `models/scaler.pkl`: 数据标准化器

### 日志和结果
- `logs/config.json`: 训练配置
- `logs/training_history.json`: 训练历史（损失和准确率）
- `results/training_curves.png`: 训练曲线图
- `results/confusion_matrix.png`: 混淆矩阵
- `results/roc_curve.png`: ROC曲线
- `results/evaluation_results.json`: 详细评估指标

## 新数据适配指南

### 步骤1：准备数据
确保新数据格式与F0L.xlsx/F1L.xlsx一致：
- 包含相同的特征列
- 包含Time列和label列

### 步骤2：修改数据路径
在 `main.py` 中修改：
```python
config = {
    'normal_file': 'path/to/your/normal_data.xlsx',
    'fault_file': 'path/to/your/fault_data.xlsx',
    ...
}
```

### 步骤3：调整时间步（可选）
根据采样频率调整 `time_steps`：
```python
config = {
    'time_steps': 60,  # 如果需要更长的时间窗口
    ...
}
```

### 步骤4：调整特征维度（如果特征数变化）
如果新数据特征数不同，需要修改 `model.py`：
```python
# 在train.py中自动检测，无需手动修改
input_dim = X_train.shape[2]  # 自动获取特征维度
```

## 性能指标

### 评估指标
- **准确率 (Accuracy)**: 正确分类的样本比例
- **精确率 (Precision)**: 预测为故障中实际故障的比例
- **召回率 (Recall/Sensitivity)**: 实际故障中被正确识别的比例
- **特异性 (Specificity)**: 实际正常中被正确识别的比例
- **F1-Score**: 精确率和召回率的调和平均数
- **ROC AUC**: ROC曲线下面积

## 故障排除

### 显存不足
减小 `batch_size`：
```python
config = {'batch_size': 16}
```

### 训练过拟合
增加 `dropout` 或减少 `num_layers`：
```python
# 在model.py中修改
dropout=0.5  # 增加dropout比例
```

### 数据加载错误
检查数据文件路径和格式是否正确

## 参考文献

- Vaswani et al. (2017): "Attention Is All You Need"
- 光伏系统故障诊断相关研究

## 许可证

MIT License

