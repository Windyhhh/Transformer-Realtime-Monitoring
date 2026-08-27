<div align="center">

# 📡 Transformer-Realtime-Monitoring

### Transformer-based real-time intelligent monitoring.

Anomaly detection and time-series analysis — with PV fault diagnosis.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)

</div>

---

**Transformer-Realtime-Monitoring** is a **Transformer-based real-time intelligent monitoring** system for **anomaly detection** and time-series analysis, with a PV fault-diagnosis module and trained model.

> [!NOTE]
> 中文项目：基于 Transformer 的实时智能监控系统——异常检测、时序分析（光伏故障诊断）。

---

## Quickstart

```bash
git clone https://github.com/Windyhhh/Transformer-Realtime-Monitoring.git
cd Transformer-Realtime-Monitoring

pip install -r requirements.txt

# train / diagnose
python pv_fault_diagnosis/main.py

# evaluate
python pv_fault_diagnosis/evaluate.py

# inference
python pv_fault_diagnosis/inference.py
```

A trained model (`best_model.pth`) and scaler are included.

---

## Features

- **Transformer monitoring** — anomaly detection over time series.
- **PV fault diagnosis** — real deployment case.
- **Trained model** — weights + training history included.

---

## Project Structure

```
Transformer-Realtime-Monitoring/
├── pv_fault_diagnosis/
│   ├── main.py, model.py, inference.py, evaluate.py
│   ├── data_preprocessing.py
│   ├── models/            # best_model.pth, scaler.pkl
│   └── logs/              # config, training_history
├── F0L.xlsx / F1L.xlsx    # data
└── README.md
```

---

## License

MIT — free to use, modify and distribute.
