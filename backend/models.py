# backend/models.py
from datetime import datetime
from database import db

class Farmer(db.Model):
    __tablename__ = "farmers"
    id = db.Column(db.Integer, primary_key=True)
    registration_no = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    mobile = db.Column(db.String(30), nullable=True)
    aadhaar = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    wallet_address = db.Column(db.String(128), nullable=True)
    gov_id_path = db.Column(db.String(256), nullable=True)
    selfie_path = db.Column(db.String(256), nullable=True)
    verification_meta = db.Column(db.Text, nullable=True)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    lands = db.relationship("Land", backref="farmer", lazy=True)

class Land(db.Model):
    __tablename__ = "lands"
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey("farmers.id"), nullable=False)
    land_name = db.Column(db.String(128), nullable=False)
    size_acres = db.Column(db.Float, nullable=True)
    crop_type = db.Column(db.String(32), nullable=False)
    plots_count = db.Column(db.Integer, nullable=True)
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
    status = db.Column(db.String(40), default="submitted")
    is_stressed = db.Column(db.Integer, nullable=True)
    model1_probability = db.Column(db.Float, nullable=True)
    payout_percentage = db.Column(db.Float, nullable=True)  # percent 0-100
    payload_json = db.Column(db.Text, nullable=True)
    onchain_tx = db.Column(db.String(128), nullable=True)
    onchain_status = db.Column(db.String(32), nullable=True)  # 'pending','success','failed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
