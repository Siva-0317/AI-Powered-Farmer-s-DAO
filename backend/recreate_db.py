# filepath: d:\hackbeyolimit\Hack-Beyond-Limits\backend\recreate_db.py
from database import db, create_app
from models import Farmer

app = create_app()
with app.app_context():
    Farmer.query.update({Farmer.verified: True})
    db.session.commit()
print("All farmers verified.")