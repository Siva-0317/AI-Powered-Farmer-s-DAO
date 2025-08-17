# backend/ml.py
import os, json
import numpy as np

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models") if os.path.exists(os.path.join(os.path.dirname(__file__), "..", "models")) else os.path.join(os.path.dirname(__file__), "models")
STRESS_FEATURES = ['NDVI','SAVI','Chlorophyll_Content','Leaf_Area_Index','Temperature','Humidity','Rainfall','Soil_Moisture']
PAYOUT_FEATURES = ['NDVI','Expected_Yield','Crop_Stress_Indicator','Temperature','Rainfall','Soil_Moisture','Crop_Type_encoded','Canopy_Coverage','Pest_Damage','Leaf_Area_Index']

clf = None
scaler = None
reg = None

try:
    import joblib
    scaler_path = os.path.join(MODELS_DIR, "model1_ffn_scaler.joblib")
    reg_path = os.path.join(MODELS_DIR, "model2_rf.joblib")
    clf_joblib = os.path.join(MODELS_DIR, "model1_clf.joblib")
    if os.path.exists(scaler_path):
        scaler = joblib.load(scaler_path)
    if os.path.exists(reg_path):
        reg = joblib.load(reg_path)
    if os.path.exists(clf_joblib):
        clf = joblib.load(clf_joblib)
except Exception as e:
    print("ML load warning:", e)

def predict_stress(feature_dict):
    try:
        arr = np.array([feature_dict.get(k, 0.0) for k in STRESS_FEATURES], dtype=float).reshape(1,-1)
        if scaler is not None:
            arr = scaler.transform(arr)
        if clf is not None:
            proba = clf.predict_proba(arr)[0,1]
            return (1 if proba>=0.5 else 0, float(proba))
        ndvi = feature_dict.get('NDVI', 0.5)
        stress_indicator = feature_dict.get('Crop_Stress_Indicator', 0)
        prob = max(0.0, min(1.0, 1.0 - ndvi*0.8 + (stress_indicator/200.0)))
        return (1 if prob>=0.5 else 0, float(prob))
    except Exception as e:
        return (0, 0.0)

def predict_payout(feature_dict):
    try:
        arr = np.array([feature_dict.get(k, 0.0) for k in PAYOUT_FEATURES], dtype=float).reshape(1,-1)
        if reg is not None:
            out = reg.predict(arr)[0]
            return float(np.clip(out, 0.0, 100.0))
        stress = feature_dict.get('Crop_Stress_Indicator', 0)
        ndvi = feature_dict.get('NDVI', 0.5)
        base = max(0.0, (stress/100.0)*80.0 + (1.0-ndvi)*20.0)
        return float(np.clip(base, 0.0, 100.0))
    except Exception as e:
        return 0.0
