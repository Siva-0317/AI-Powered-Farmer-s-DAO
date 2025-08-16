from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class Farmer(db.Model):
    __tablename__ = "farmers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    wallet_address = db.Column(db.String(80), nullable=True)
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
    land_name = db.Column(db.String(120), nullable=False)  # e.g., "siva-land1"
    crop_type = db.Column(db.String(40), nullable=False)   # Wheat/Maize/Rice
    location = db.Column(db.String(160), nullable=True)    # free text / latlon
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    claims = db.relationship("Claim", backref="land", lazy=True)

class Claim(db.Model):
    __tablename__ = "claims"
    id = db.Column(db.Integer, primary_key=True)
    land_id = db.Column(db.Integer, db.ForeignKey("lands.id"), nullable=False)
    status = db.Column(db.String(40), default="submitted")  # submitted|predicted|pushed|paid|rejected
    is_stressed = db.Column(db.Integer, nullable=True)      # 0/1
    payout_percentage = db.Column(db.Float, nullable=True)
    model1_probability = db.Column(db.Float, nullable=True)

    # raw payload snapshot (optional)
    payload_json = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
