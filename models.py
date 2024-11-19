from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True, default=1)
    amountVehicles = db.Column(db.Integer)
    capacity = db.Column(db.Integer)
    depotx = db.Column(db.Float)
    depoty = db.Column(db.Float)
    horizon = db.Column(db.Integer)

class Node(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.Integer, db.ForeignKey('config.id'), nullable=False)
    latitud = db.Column(db.Float)
    longitud = db.Column(db.Float)
    demanda = db.Column(db.Integer)
    tiempoInicio = db.Column(db.Integer)
    tiempoFin = db.Column(db.Integer)
    config = db.relationship('Config', backref=db.backref('nodes', lazy=True))