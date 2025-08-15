import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score

# ===== LOAD DATASET =====
df = pd.read_csv("model2_payout_prediction_dataset.csv")

# Encode crop types if not already numeric
if "Crop_Type_encoded" not in df.columns:
    crop_map = {"Wheat": 0, "Maize": 1, "Rice": 2}
    df["Crop_Type_encoded"] = df["Crop_Type"].map(crop_map)

# Features and target
X = df[['NDVI', 'Expected_Yield', 'Crop_Stress_Indicator', 'Temperature',
        'Rainfall', 'Soil_Moisture', 'Crop_Type_encoded', 'Canopy_Coverage',
        'Pest_Damage', 'Leaf_Area_Index']]
y = df['payout_percentage']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ===== Train RandomForest =====
rf_model = RandomForestRegressor(
    n_estimators=300,
    max_depth=12,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train, y_train)

# ===== Evaluate =====
y_pred = rf_model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"\n✅ Model 2 RandomForest RMSE: {rmse:.4f} | R²: {r2:.4f}")

# ===== Save Model =====
joblib.dump(rf_model, "model2_rf.joblib")
print("💾 Model 2 RandomForest saved as 'model2_rf.joblib'")
