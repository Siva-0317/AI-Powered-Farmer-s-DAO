import os
import numpy as np
import joblib
import torch
import torch.nn as nn

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

# Model 1 FFN (binary stress) + scaler
MODEL1_PTH = os.path.join(MODELS_DIR, "model1_ffn.pth")
MODEL1_SCALER = os.path.join(MODELS_DIR, "model1_ffn_scaler.joblib")

# Model 2 RandomForest (payout)
MODEL2_RF = os.path.join(MODELS_DIR, "model2_rf.joblib")

# ---- FFN definition must match training ----
class FFN(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64), nn.ReLU(),
            nn.Linear(64, 32), nn.ReLU(),
            nn.Linear(32, 1), nn.Sigmoid()
        )
    def forward(self, x):
        return self.net(x)

# load artifacts once
scaler1 = joblib.load(MODEL1_SCALER)
model1_state = torch.load(MODEL1_PTH, map_location="cpu")
model1 = FFN(8)
model1.load_state_dict(model1_state["model_state_dict"])
model1.eval()

model2 = joblib.load(MODEL2_RF)

STRESS_FEATURES = [
    "NDVI","SAVI","Chlorophyll_Content","Leaf_Area_Index",
    "Temperature","Humidity","Rainfall","Soil_Moisture"
]

def ensure_crop_encoded(payload):
    if "Crop_Type_encoded" in payload:
        return int(payload["Crop_Type_encoded"])
    if "Crop_Type" in payload:
        return {"Wheat":0,"Maize":1,"Rice":2}.get(payload["Crop_Type"], 0)
    raise ValueError("Provide Crop_Type or Crop_Type_encoded")

def predict_stress(feat_dict):
    # expects keys in STRESS_FEATURES
    x = np.array([[float(feat_dict[k]) for k in STRESS_FEATURES]], dtype=np.float32)
    x_scaled = scaler1.transform(x)
    with torch.no_grad():
        prob = float(model1(torch.tensor(x_scaled)).numpy()[0][0])
    return int(prob >= 0.5), prob

def predict_payout(feat_dict):
    # model 2 needs:
    # NDVI, Expected_Yield, Crop_Stress_Indicator, Temperature, Rainfall,
    # Soil_Moisture, Crop_Type_encoded, Canopy_Coverage, Pest_Damage, Leaf_Area_Index
    crop_enc = ensure_crop_encoded(feat_dict)
    feats = [
        float(feat_dict["NDVI"]),
        float(feat_dict["Expected_Yield"]),
        float(feat_dict["Crop_Stress_Indicator"]),
        float(feat_dict["Temperature"]),
        float(feat_dict["Rainfall"]),
        float(feat_dict["Soil_Moisture"]),
        float(crop_enc),
        float(feat_dict["Canopy_Coverage"]),
        float(feat_dict["Pest_Damage"]),
        float(feat_dict["Leaf_Area_Index"]),
    ]
    pred = float(model2.predict(np.array([feats]))[0])
    return max(0.0, min(100.0, pred))
