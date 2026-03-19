from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class AttendanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    ministry_of_service = db.Column(db.String(50), nullable=False) # Niños, Damas, Intercesión, etc.
    service_type = db.Column(db.String(50), nullable=False) # Local, Zona, Provincial, Nacional
    shift = db.Column(db.String(50), nullable=False) # Mañana, Tarde, Noche
    
    # Counts
    kids = db.Column(db.Integer, default=0)
    teens = db.Column(db.Integer, default=0)
    youth = db.Column(db.Integer, default=0)
    women = db.Column(db.Integer, default=0)
    men = db.Column(db.Integer, default=0)
    visits = db.Column(db.Integer, default=0)
    testimonies = db.Column(db.Integer, default=0)
    
    # Converts (Convertidos)
    converts_total = db.Column(db.Integer, default=0)
    converts_kids = db.Column(db.Integer, default=0)
    converts_teens = db.Column(db.Integer, default=0)
    converts_youth = db.Column(db.Integer, default=0)
    converts_men = db.Column(db.Integer, default=0)
    converts_women = db.Column(db.Integer, default=0)
    
    # Reconciled (Reconciliados)
    reconciled_kids = db.Column(db.Integer, default=0)
    reconciled_teens = db.Column(db.Integer, default=0)
    reconciled_youth = db.Column(db.Integer, default=0)
    reconciled_men = db.Column(db.Integer, default=0)
    reconciled_women = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
