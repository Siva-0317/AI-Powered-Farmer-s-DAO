import os, json
from datetime import datetime
from dotenv import load_dotenv
from flask import request, jsonify
from flask_cors import CORS

from database import create_app, db
from models_sql import Farmer, Land, Claim
from utils import ok, err
from ml import STRESS_FEATURES, predict_stress, predict_payout
from chainlink_client import push_prediction_to_chainlink

app = create_app()
CORS(app)
load_dotenv()

# ---------- bootstrap ----------
with app.app_context():
    db.create_all()

# ---------- Auth (very simple tokenless demo) ----------
@app.post("/api/register")
def register():
    data = request.get_json(force=True)
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    wallet_address = data.get("wallet_address", "")

    if not (name and email and password):
        return err("name, email, password required")

    if Farmer.query.filter_by(email=email).first():
        return err("email already registered", 409)

    f = Farmer(name=name, email=email, wallet_address=wallet_address)
    f.set_password(password)
    db.session.add(f)
    db.session.commit()
    return jsonify(ok({"farmer_id": f.id}))

@app.post("/api/login")
def login():
    data = request.get_json(force=True)
    email = data.get("email")
    password = data.get("password")
    f = Farmer.query.filter_by(email=email).first()
    if not f or not f.check_password(password):
        return err("invalid credentials", 401)
    # return farmer profile and lands; in prod return JWT
    lands = [{"id": l.id, "land_name": l.land_name, "crop_type": l.crop_type, "location": l.location} for l in f.lands]
    return jsonify(ok({"farmer_id": f.id, "name": f.name, "wallet_address": f.wallet_address, "lands": lands}))

# ---------- Land management ----------
@app.post("/api/lands")
def add_land():
    data = request.get_json(force=True)
    farmer_id = int(data.get("farmer_id"))
    land_name = data.get("land_name")
    crop_type = data.get("crop_type")  # Wheat/Maize/Rice
    location = data.get("location", "")

    if not (farmer_id and land_name and crop_type):
        return err("farmer_id, land_name, crop_type required")

    l = Land(farmer_id=farmer_id, land_name=land_name, crop_type=crop_type, location=location)
    db.session.add(l)
    db.session.commit()
    return jsonify(ok({"land_id": l.id}))

@app.get("/api/lands")
def list_lands():
    farmer_id = int(request.args.get("farmer_id", 0))
    lands = Land.query.filter_by(farmer_id=farmer_id).all()
    out = [{"id": l.id, "land_name": l.land_name, "crop_type": l.crop_type, "location": l.location} for l in lands]
    return jsonify(ok(out))

# ---------- Claim + ML flow ----------
@app.post("/api/claims/submit")
def submit_claim():
    """
    Frontend sends:
    {
      "farmer_id": 1,
      "land_id": 10,
      "model1": { NDVI, SAVI, Chlorophyll_Content, Leaf_Area_Index, Temperature, Humidity, Rainfall, Soil_Moisture },
      "model2": { Expected_Yield, Crop_Stress_Indicator, Canopy_Coverage, Pest_Damage, Leaf_Area_Index, Crop_Type? }  // shares some keys with model1
    }
    We merge shared keys automatically so user doesn't retype.
    """
    data = request.get_json(force=True)
    farmer_id = int(data.get("farmer_id", 0))
    land_id = int(data.get("land_id", 0))
    m1 = data.get("model1", {}) or {}
    m2 = data.get("model2", {}) or {}

    land = Land.query.get(land_id)
    if not land or land.farmer_id != farmer_id:
        return err("invalid land/farmer")

    # fill shared fields into model2 if missing
    merged = dict(m2)
    for k in ["NDVI","SAVI","Chlorophyll_Content","Leaf_Area_Index","Temperature","Humidity","Rainfall","Soil_Moisture"]:
        if k in m1 and k not in merged:
            merged[k] = m1[k]

    # auto set crop type from land if not provided
    if "Crop_Type" not in merged and "Crop_Type_encoded" not in merged:
        merged["Crop_Type"] = land.crop_type

    # ---- Run model 1
    try:
        # ensure m1 contains full stress features
        for k in STRESS_FEATURES:
            if k not in m1:
                raise ValueError(f"missing {k} in model1")
        is_stressed, prob = predict_stress(m1)
    except Exception as e:
        return err(f"model1 error: {e}")

    # ---- Run model 2 (payout)
    try:
        payout = predict_payout(merged)
    except Exception as e:
        return err(f"model2 error: {e}")

    # create claim record
    claim = Claim(
        land_id=land_id,
        status="predicted",
        is_stressed=is_stressed,
        payout_percentage=payout,
        model1_probability=prob,
        payload_json=json.dumps({"model1": m1, "model2": merged})
    )
    db.session.add(claim)
    db.session.commit()

    result = {
        "claim_id": claim.id,
        "is_stressed": is_stressed,
        "probability": round(prob, 4),
        "payout_percentage": round(payout, 2),
        "land_id": land_id,
        "farmer_id": farmer_id,
        "ts": datetime.utcnow().isoformat() + "Z"
    }

    # optional: push to chainlink node (webhook job)
    push_resp = push_prediction_to_chainlink({
        "policy_id": land_id,  # or your own policy mapping
        "is_stressed": is_stressed,
        "payout": round(payout, 2),
        "probability": round(prob, 4),
        "farmer_wallet": land.farmer.wallet_address
    })

    # if successfully pushed, update state
    if isinstance(push_resp, dict) and push_resp.get("status_code", 0) in (200, 201, 202):
        claim.status = "pushed"
        db.session.commit()

    return jsonify(ok(result, chainlink_response=push_resp))

@app.get("/api/claims/<int:claim_id>")
def get_claim(claim_id):
    c = Claim.query.get_or_404(claim_id)
    return jsonify(ok({
        "claim_id": c.id,
        "land_id": c.land_id,
        "status": c.status,
        "is_stressed": c.is_stressed,
        "payout_percentage": c.payout_percentage,
        "model1_probability": c.model1_probability,
        "created_at": c.created_at.isoformat(),
        "updated_at": c.updated_at.isoformat() if c.updated_at else None
    }))

@app.get("/health")
def health():
    return jsonify(ok(ts=datetime.utcnow().isoformat() + "Z"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
