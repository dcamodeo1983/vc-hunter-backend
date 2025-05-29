# VC Hunter Backend

This repository contains the backend AI agents for the VC Hunter application.

## 📦 Modules Included
- `vc_scraper_agent.py`: Scrapes VC firm websites and shallow portfolio data
- `run.py`: Orchestrator script for scraping
- `requirements.txt`: Python dependencies

## 📂 Structure

vc-hunter-v2/
├── agents/
│   └── vc_scraper_agent.py
├── data/
│   └── raw/
├── run.py
├── requirements.txt
└── README.md

## 🚀 How to Run

```bash
python run.py
```

Make sure to activate your virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
