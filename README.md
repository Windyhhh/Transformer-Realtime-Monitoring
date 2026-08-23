# ⚡ Transformer Realtime Monitoring | 基于 Transformer 的实时智能监测系统

> **Real-time intelligent monitoring system using Transformer models for time series anomaly detection. Streaming data ingestion, Transformer encoder for pattern learning, real-time anomaly scoring, alerting, and visualization.**
>
> 基于 Transformer 模型的实时智能监测系统，用于时间序列异常检测。流式数据接入、Transformer 编码器模式学习、实时异常评分、告警和可视化。

---

## 🌟 Features | 核心特性

- **Transformer Encoder** — Self-attention for time series
- **Real-time Inference** — Streaming anomaly detection
- **Multi-Variate** — Support for multiple sensor channels
- **Anomaly Scoring** — Reconstruction error + attention-based
- **Alerting** — Threshold-based real-time alerts
- **Visualization** — Live dashboard with anomaly overlays
- **Data Ingestion** — Kafka / MQTT / CSV streaming

---

## 🚀 Quick Start | 快速开始

```bash
pip install torch numpy pandas matplotlib flask

# Train on historical data
python train.py --data sensor_data.csv --epochs 50

# Start real-time monitoring
python monitor.py --model best_model.pt --stream mqtt://localhost:1883

# Dashboard
# http://localhost:5000
```

---

## 🔬 Architecture | 架构

```
Sensor Data → Preprocessing → Transformer Encoder → Reconstruction → Anomaly Score → Alert
```

---

## 📄 License | 许可证

MIT License.

[GitHub](https://github.com/Windyhhh/Transformer-Realtime-Monitoring)
