# 🌍 GroundWatch Local

Local-first land-subsidence early-warning screening dashboard.

## Features
- Explainable 0–100 subsidence screening score
- Zone-level analytics
- Satellite subsidence signal analysis
- Groundwater extraction analysis
- Construction and building-density signals
- Soil susceptibility analysis
- Rainfall context
- Historical subsidence signals
- Local CSV validation and scored export
- Interactive Plotly dashboards
- No external APIs

## Run
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
```

The included dataset is synthetic demonstration data. Scores are screening signals and are not engineering or safety certifications.
