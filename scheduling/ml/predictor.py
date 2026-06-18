import os
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "ml", "logistic_model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "ml", "vectorizer.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "ml", "encoder.pkl")


model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)
encoder = joblib.load(ENCODER_PATH)


def predict_difficulty(course_title):
    X = vectorizer.transform([course_title])
    probs = model.predict_proba(X)[0]
    pred = model.predict(X)[0]
    label = encoder.inverse_transform([pred])[0]

    label_map = {"Easy": 0.2, "Medium": 0.55, "Hard": 0.85}
    score = 0.0
    for idx, prob in enumerate(probs):
        raw_label = encoder.inverse_transform([idx])[0]
        score += prob * label_map.get(raw_label, 0.5)

    return label, round(score, 4)