# Orchestro-Style Data Pipeline Demo

This project is a small data-engineering and data-quality pipeline built in Python.
It simulates workflows similar to Reveals’ Orchestro:

- Data ingestion (CSV → dataframe)
- Cleaning & normalization
- Data quality checks
- Transformation (Key Performance Indicators computation)
- Report generation

## How to run
pip install -r requirements.txt
python src/main.py

### How to define the cleaning
Go to the config file > src/config.py
