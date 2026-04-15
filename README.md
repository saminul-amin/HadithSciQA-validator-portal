# HadithSciQA — Scholar Validation Portal

A professional Streamlit web application for **expert scholar validation** of the HadithSciQA benchmark dataset (ICML 2026).

## 🚀 Live Demo

Deploy on [Streamlit Community Cloud](https://share.streamlit.io) by connecting this repository.

## 📋 Features

- **150 benchmark questions** across 3 tasks displayed with full Arabic text support
- **Task 1 — Terminology MCQ** (60 questions): Hadith science terminology definitions
- **Task 2 — Narrator Grading** (50 questions): Ibn Ḥajar's narrator evaluation phrases
- **Task 3 — Isnad Reasoning** (40 questions): Open-ended chain of narration analysis
- **Scholar validation form** for each question (Correct / Needs Revision / Incorrect + quality rating + comments)
- **Filtering** by task type, difficulty, and validation status
- **Progress tracking** with per-task breakdowns
- **Export** validated results as JSON for research records
- **Validation report** with summary statistics

## 🏗️ Local Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Deploy on Streamlit Cloud

1. Push this folder to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account and select this repository
4. Set **Main file path** to `app.py`
5. Click **Deploy**

## 📁 Structure

```
HadithSciQA-Validator/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .streamlit/
│   └── config.toml           # Streamlit theme configuration
└── data/
    └── full_benchmark.json   # Benchmark dataset (150 questions)
```

## 📝 Notes

- Validation results are saved locally in `data/validation_results.json`
- On Streamlit Cloud, validation state persists only within a session (use the export button to save)
- Arabic text is rendered with the Amiri font for optimal readability
