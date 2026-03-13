from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from datetime import datetime

db = SQLAlchemy()

class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pais = db.Column(db.String(5))
    estado = db.Column(db.String(20)) # PENDING, CONFIRMED
    email_cifrado = db.Column(db.String(255))
    telefono_cifrado = db.Column(db.String(255))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class ReservaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Reserva
        load_instance = True
