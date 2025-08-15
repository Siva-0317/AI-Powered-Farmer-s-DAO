#FFN MODEL 1
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib

# ===== LOAD BALANCED DATASET =====
df = pd.read_csv("model1_stress_detection_dataset_balanced.csv")

# Features and labels
X = df[['NDVI', 'SAVI', 'Chlorophyll_Content', 'Leaf_Area_Index',
        'Temperature', 'Humidity', 'Rainfall', 'Soil_Moisture']]
y = df['is_stressed']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Convert to PyTorch tensors
X_train_t = torch.tensor(X_train_scaled, dtype=torch.float32)
y_train_t = torch.tensor(y_train.values, dtype=torch.float32).view(-1, 1)
X_test_t = torch.tensor(X_test_scaled, dtype=torch.float32)
y_test_t = torch.tensor(y_test.values, dtype=torch.float32).view(-1, 1)

# ===== FFN Model =====
class FFN(nn.Module):
    def __init__(self, input_dim):
        super(FFN, self).__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_dim, 64), nn.ReLU(),
            nn.Linear(64, 32), nn.ReLU(),
            nn.Linear(32, 1), nn.Sigmoid()
        )
    def forward(self, x):
        return self.layers(x)

model = FFN(X_train.shape[1])

# Use class weighting for balanced learning
class_weight = len(y_train) / (2 * y_train.sum())
criterion = nn.BCELoss(weight=torch.full((len(y_train_t), 1), class_weight))
optimizer = optim.Adam(model.parameters(), lr=0.001)

# ===== Training =====
epochs = 80
for epoch in range(epochs):
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train_t)
    loss = criterion(outputs, y_train_t)
    loss.backward()
    optimizer.step()

# ===== Evaluation =====
model.eval()
with torch.no_grad():
    y_pred_ffn = (model(X_test_t).numpy() >= 0.5).astype(int)
acc = accuracy_score(y_test, y_pred_ffn)
print(f"\n✅ Model 1 FFN Accuracy: {acc:.4f}")
print(classification_report(y_test, y_pred_ffn))

# ===== Save model & scaler =====
torch.save({"model_state_dict": model.state_dict()}, "model1_ffn.pth")
joblib.dump(scaler, "model1_ffn_scaler.joblib")
print("\n💾 Model 1 FFN saved as 'model1_ffn.pth' and scaler as 'model1_ffn_scaler.joblib'")
