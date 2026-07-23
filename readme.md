---
title: AthleteID
emoji: 🏆
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
app_port: 7860
---

# AthleteID — Sports Celebrity Image Classification

Classify photos of five athletes using OpenCV face detection, wavelet features, and a scikit-learn model served by Flask.

**Supported athletes**

1. Maria Sharapova  
2. Serena Williams  
3. Virat Kohli  
4. Roger Federer  
5. Lionel Messi  

## Folder structure

| Folder | Purpose |
| --- | --- |
| `UI/` | Frontend (HTML / CSS / JS) |
| `server/` | Flask API + trained model artifacts |
| `model/` | Jupyter notebooks for training |
| `image-dataset/` | Raw images used for training |

## Technologies

- Python, NumPy, OpenCV  
- Matplotlib & Seaborn (training visualization)  
- scikit-learn (model building)  
- Flask (HTTP server; also serves the UI)  
- HTML / CSS / JavaScript  

## Quick start (local)

```bash
cd server
pip install -r requirements.txt
python server.py
```

Open **http://127.0.0.1:5000/** in your browser.

You only need one process — Flask serves both the UI and `/classify_image`.

## Deploy on Hugging Face Spaces (free, no card)

1. Create a **Docker** Space on Hugging Face.
2. Push this repo to the Space (steps below in chat / docs).
3. Wait for the Docker build, then open the Space URL.

## Notes

- Run `server.py` from any working directory; artifact paths are resolved relative to the `server/` folder.
- `server/artifacts/class_dictionary.json` uses short class names (`lionel_messi`, …).
- Wavelet preprocessing matches the training notebook so the shipped `saved_model.pkl` stays consistent.
- Retrain from `model/sports_celebrity_classification.ipynb` if you change features or add athletes, then copy the new model into `server/artifacts/`.
