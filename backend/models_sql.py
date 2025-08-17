# backend/models_sql.py
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class Farmer(db.Model):
    __tablename__ = "farmers"
    id = db.Column(db.Integer, primary_key=True)
    registration_no = db.Column(db.String(32), unique=True, index=True, nullable=False)  # generated reg no
    name = db.Column(db.String(120), nullable=False)
    mobile = db.Column(db.String(20), nullable=True)
    aadhaar = db.Column(db.String(20), nullable=True)
    wallet_address = db.Column(db.String(80), nullable=True)
    password_hash = db.Column(db.String(256), nullable=True)  # optional if you want password fallback
    verified = db.Column(db.Boolean, default=False)

    gov_id_path = db.Column(db.String(256), nullable=True)   # uploaded govt id image
    selfie_path = db.Column(db.String(256), nullable=True)
    verification_meta = db.Column(db.Text, nullable=True)    # JSON: otp timestamps, face-match result etc.

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    lands = db.relationship("Land", backref="farmer", lazy=True)

    def set_password(self, pw: str):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw: str) -> bool:
        return check_password_hash(self.password_hash, pw)

class Land(db.Model):
    __tablename__ = "lands"
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey("farmers.id"), nullable=False)
    land_name = db.Column(db.String(120), nullable=False)
    size_acres = db.Column(db.Float, nullable=True)
    crop_type = db.Column(db.String(32), nullable=False)   # Wheat/Maize/Rice
    plots_count = db.Column(db.Integer, nullable=True)     # how many subplots
    verification_image_path = db.Column(db.String(256), nullable=True)
    geo_lat = db.Column(db.Float, nullable=True)
    geo_lon = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    claims = db.relationship("Claim", backref="land", lazy=True)

class Claim(db.Model):
    __tablename__ = "claims"
    id = db.Column(db.Integer, primary_key=True)
    land_id = db.Column(db.Integer, db.ForeignKey("lands.id"), nullable=False)
    farmer_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(40), default="submitted")  # submitted|predicted|pushed|paid|rejected
    is_stressed = db.Column(db.Integer, nullable=True)      # 0/1
    payout_percentage = db.Column(db.Float, nullable=True)
    model1_probability = db.Column(db.Float, nullable=True)
    payout_amount = db.Column(db.Float, nullable=True)      # computed based on insured amount; optional
    payload_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
