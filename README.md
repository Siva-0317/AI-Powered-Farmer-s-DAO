
---

# 🌱 AI-Powered Farmer’s DAO

A decentralized platform that empowers farmers through **blockchain governance** and **AI-driven insights**.  
The system integrates **smart contracts (DAO + Treasury)**, a **web frontend for voting and proposals**, and an **AI backend** that assists with **crop stress detection** and **payout prediction**.

---

## ✨ Features

- 🗳 **DAO Governance** – Farmers can propose, discuss, and vote on decisions.  
- 💰 **Treasury Management** – Transparent fund allocation via smart contracts.  
- 🤖 **AI Insights** – 
  - *Stress Detection* (classification model)  
  - *Payout Prediction* (regression model)  
- 🌐 **Full-Stack Setup** – Solidity contracts, Python AI backend, and Web-based frontend.  
- 📊 **Datasets & Visuals** – Preprocessed datasets and residual analysis plots included.  

---

## 📂 Repository Structure



AI-Powered-Farmer-s-DAO/
├─ backend/                 # Python API server (AI predictions)
├─ contracts/               # Solidity smart contracts (DAO, treasury)
├─ front/                   # Web frontend (dApp for proposals & voting)
├─ model\_training/          # Scripts & notebooks for ML model training
├─ models/                  # Saved model artifacts
├─ agriculture\_dataset.csv
├─ model1\_stress\_detection\_dataset\_balanced.csv
├─ model2\_payout\_prediction\_dataset.csv
├─ residual\_analysis\_model1.png
├─ Residual\_analysis\_model2.png
├─ requirements.txt
└─ LICENSE

`

---

## 🛠 Tech Stack

- **Smart Contracts:** Solidity  
- **Frontend:** JavaScript (React/Vite)  
- **Backend (AI API):** Python (FastAPI / Flask)  
- **ML Training:** Scikit-learn, Pandas, NumPy  
- **Blockchain Tools:** Hardhat / Foundry  

---

## ⚡ Quick Start

### 1) Clone the Repository
bash
git clone https://github.com/Siva-0317/AI-Powered-Farmer-s-DAO.git
cd AI-Powered-Farmer-s-DAO
`

### 2) Backend (AI Service)

bash
python -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate
pip install -r requirements.txt


Run backend:

bash
python backend/main.py
# or (if using FastAPI/uvicorn)
uvicorn backend.app:app --reload --port 8000


### 3) Contracts

Using **Hardhat**:

bash
cd contracts
npm install
npx hardhat compile
npx hardhat test
npx hardhat run scripts/deploy.js --network localhost


### 4) Frontend

bash
cd front
npm install
npm run dev

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🧪 Example API Usage

**Stress Detection**

bash
curl -X POST http://localhost:8000/predict/stress \
-H "Content-Type: application/json" \
-d '{"soil_moisture":0.22,"temperature_c":33.1,"humidity":58,"ndvi":0.41,"rainfall_mm":2.0}'


**Payout Prediction**

bash
curl -X POST http://localhost:8000/predict/payout \
-H "Content-Type: application/json" \
-d '{"acreage":2.5,"crop_type":"paddy","season":"kharif","stress_score":0.36,"historical_yield":2100}'


---

## 📊 Datasets

* `agriculture_dataset.csv` – Base dataset
* `model1_stress_detection_dataset_balanced.csv` – For classification
* `model2_payout_prediction_dataset.csv` – For regression
* `residual_analysis_model1.png` / `Residual_analysis_model2.png` – Model diagnostics

---

## 🚀 Roadmap

* [ ] Integrate on-chain oracles for AI results
* [ ] Multi-language farmer-friendly UI
* [ ] Mobile-first design for rural accessibility
* [ ] AI model drift monitoring and retraining

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch
3. Commit changes
4. Open a PR

---

## 📄 License

This project is licensed under the **Apache-2.0 License**.
See [LICENSE](./LICENSE) for details.

---

## 🙏 Acknowledgements

Inspired by the need for **transparent, inclusive, and AI-powered rural governance**.

