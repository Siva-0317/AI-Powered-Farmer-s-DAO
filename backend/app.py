# backend/app.py
import os, json, uuid, time
from datetime import datetime
from flask import request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from database import create_app, db
from models import Farmer, Land, Claim
from ml import STRESS_FEATURES, predict_stress, predict_payout
from chainlink_client import push_prediction_to_chainlink
from utils import ok, err

load_dotenv()
app = create_app()
CORS(app)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_EXT = {"png","jpg","jpeg"}

def gen_registration_no():
    return f"HBL-{datetime.utcnow().year}-{uuid.uuid4().hex[:6].upper()}"

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXT

def save_upload(file_storage, prefix="file"):
    if not file_storage or file_storage.filename == "":
        return None
    if not allowed_file(file_storage.filename):
        return None
    fname = secure_filename(file_storage.filename)
    token = uuid.uuid4().hex[:8]
    outname = f"{prefix}_{token}_{fname}"
    path = os.path.join(UPLOAD_DIR, outname)
    file_storage.save(path)
    return outname

with app.app_context():
    db.create_all()

@app.get("/health")
def health():
    return jsonify(ok({"uptime": True}))

@app.post("/api/register")
def register():
    data = request.form.to_dict()
    name = data.get("name")
    if not name:
        return err("name required", 400)
    mobile = data.get("mobile")
    aadhaar = data.get("aadhaar")
    wallet_address = data.get("wallet_address")
    email = data.get("email")

    govfile = request.files.get("gov_id_file")
    selfie = request.files.get("selfie_file")
    gov_fname = save_upload(govfile, "gov") if govfile else None
    selfie_fname = save_upload(selfie, "selfie") if selfie else None

    regno = gen_registration_no()
    farmer = Farmer(registration_no=regno, name=name, mobile=mobile, aadhaar=aadhaar, email=email, wallet_address=wallet_address, gov_id_path=gov_fname, selfie_path=selfie_fname, verified=False)
    db.session.add(farmer)
    db.session.commit()

    otp = str(100000 + (uuid.uuid4().int % 900000))
    farmer.verification_meta = json.dumps({"otp": otp, "otp_ts": int(time.time())})
    db.session.commit()

    return jsonify(ok({"registration_no": regno, "otp": otp, "note": "OTP returned only for prototype"}))

@app.post("/api/verify-otp")
def verify_otp():
    data = request.get_json(force=True)
    reg = data.get("registration_no")
    otp = data.get("otp")
    if not reg or not otp:
        return err("registration_no and otp required", 400)
    farmer = Farmer.query.filter_by(registration_no=reg).first()
    if not farmer:
        return err("farmer not found", 404)
    try:
        meta = json.loads(farmer.verification_meta or "{}")
    except:
        meta = {}
    if meta.get("otp") and str(meta.get("otp")) == str(otp):
        farmer.verified = True
        meta["verified_ts"] = int(time.time())
        farmer.verification_meta = json.dumps(meta)
        db.session.commit()
        return jsonify(ok({"verified": True}))
    return err("invalid otp", 400)

@app.post("/api/add-land")
def add_land():
    data = request.form.to_dict()
    reg = data.get("registration_no")
    farmer = Farmer.query.filter_by(registration_no=reg).first()
    if not farmer:
        return err("farmer not found", 404)
    land_name = data.get("land_name") or f"{farmer.name}-land"
    size_acres = float(data.get("size_acres") or 0.0)
    crop_type = data.get("crop_type") or "Wheat"
    plots_count = int(data.get("plots_count") or 1)
    geo_lat = data.get("geo_lat")
    geo_lon = data.get("geo_lon")
    verification_image = request.files.get("verification_image")
    ver_fname = save_upload(verification_image, "land") if verification_image else None

    land = Land(farmer_id=farmer.id, land_name=land_name, size_acres=size_acres, crop_type=crop_type, plots_count=plots_count, verification_image_path=ver_fname, geo_lat=float(geo_lat) if geo_lat else None, geo_lon=float(geo_lon) if geo_lon else None)
    db.session.add(land)
    db.session.commit()
    return jsonify(ok({"land_id": land.id, "land_name": land.land_name}))

@app.post("/api/login")
def login():
    data = request.get_json(force=True)
    reg = data.get("registration_no")
    if not reg:
        return err("registration_no required", 400)
    farmer = Farmer.query.filter_by(registration_no=reg).first()
    if not farmer:
        return err("invalid registration id", 401)
    if not farmer.verified:
        return err("farmer not verified", 403)
    lands = [{"id": l.id, "land_name": l.land_name, "crop_type": l.crop_type, "location": f"{l.geo_lat},{l.geo_lon}"} for l in farmer.lands]
    return jsonify(ok({"farmer_id": farmer.id, "registration_no": farmer.registration_no, "name": farmer.name, "wallet_address": farmer.wallet_address, "lands": lands}))

# helper to fetch lands (used by frontend)
@app.get("/api/lands")
def api_lands():
    farmer_id = request.args.get("farmer_id")
    if not farmer_id:
        return err("farmer_id required", 400)
    lands = Land.query.filter_by(farmer_id=int(farmer_id)).all()
    out = [{"id": l.id, "land_name": l.land_name, "crop_type": l.crop_type, "geo_lat": l.geo_lat, "geo_lon": l.geo_lon} for l in lands]
    return jsonify(ok(out))

# web3 client import
from web3_client import submit_claim_to_chain, get_tx_status

@app.post("/api/claims/submit")
def submit_claim():
    data = request.get_json(force=True)
    reg = data.get("registration_no")
    farmer = Farmer.query.filter_by(registration_no=reg).first()
    if not farmer:
        return err("invalid farmer", 400)
    land_id = int(data.get("land_id", 0))
    land = Land.query.get(land_id)
    if not land or land.farmer_id != farmer.id:
        return err("invalid land", 400)
    m1 = data.get("model1", {}) or {}
    m2 = data.get("model2", {}) or {}
    for k in STRESS_FEATURES:
        if k in m1 and k not in m2:
            m2[k] = m1[k]
    if "Crop_Type" not in m2:
        m2["Crop_Type"] = land.crop_type
    crop_map = {'Wheat': 0, 'Maize': 1, 'Rice': 2}
    if 'Crop_Type' in m2 and 'Crop_Type_encoded' not in m2:
        m2['Crop_Type_encoded'] = crop_map.get(m2['Crop_Type'], 0)

    # ML predictions
    is_stressed, prob = predict_stress(m1)
    payout = predict_payout(m2)  # percent 0-100

    claim = Claim(land_id=land_id, farmer_id=farmer.id, status="predicted", is_stressed=is_stressed, model1_probability=prob, payout_percentage=payout, payload_json=json.dumps({"model1":m1,"model2":m2}))
    db.session.add(claim)
    db.session.commit()

    scaled = int(round((payout / 100.0) * 1_000_000))

    # submit on-chain (fire-and-forget by default)
    try:
        tx_result = submit_claim_to_chain(policy_id=claim.id, stress_level=int(is_stressed), payout_percentage_scaled=scaled, wait_for_receipt=False)
    except Exception as e:
        tx_result = {"error": str(e)}

    if isinstance(tx_result, dict):
        tx_hash = tx_result.get("tx_hash")
        if tx_hash:
            claim.onchain_tx = tx_hash
            claim.onchain_status = "pending"
            claim.status = "onchain_submitted"
            db.session.commit()
        else:
            claim.onchain_status = "failed"
            claim.status = "onchain_error"
            db.session.commit()

    push_resp = push_prediction_to_chainlink({
        "policy_id": land_id,
        "is_stressed": is_stressed,
        "payout": round(payout,2),
        "probability": round(prob,4),
        "farmer_wallet": farmer.wallet_address
    }) if os.environ.get("PUSH_TO_CHAINLINK","false").lower() == "true" else {"skipped": True}

    result = {
        "claim_id": claim.id,
        "registration_no": reg,
        "is_stressed": is_stressed,
        "probability": round(prob,4),
        "payout_percentage": round(payout,2),
        "land_id": land_id,
        "farmer_id": farmer.id,
        "onchain": tx_result,
        "ts": datetime.utcnow().isoformat() + "Z"
    }
    return jsonify(ok(result, chainlink_response=push_resp))

@app.get("/api/claims/<int:claim_id>/tx_status")
def claim_tx_status(claim_id):
    claim = Claim.query.get(claim_id)
    if not claim:
        return err("claim not found", 404)
    if not claim.onchain_tx:
        return err("no onchain tx for claim", 404)
    st = get_tx_status(claim.onchain_tx)
    if "receipt" in st and st.get("status") == 1:
        claim.onchain_status = "success"
        claim.status = "paid_out" if claim.is_stressed == 1 else "no_payout"
        db.session.commit()
    elif "receipt" in st and st.get("status") == 0:
        claim.onchain_status = "failed"
        claim.status = "onchain_failed"
        db.session.commit()
    return jsonify(ok(st))

@app.post("/api/authorize_oracle")
def authorize_oracle_route():
    data = request.get_json(force=True)
    addr = data.get("address")
    if not addr:
        return err("address required", 400)
    from web3_client import authorize_oracle
    r = authorize_oracle(addr)
    return jsonify(ok(r))

@app.get("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
