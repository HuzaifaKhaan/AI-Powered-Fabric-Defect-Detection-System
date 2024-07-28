# app/models.py
from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=False, nullable=False)
    userid = db.Column(db.String(256), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    fabrics = db.relationship('Fabric', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Defect(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    defect = db.Column(db.Text, unique=True)

class Fabric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fabric_id = db.Column(db.Text, unique=True)
    total_defects = db.Column(db.Integer)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    userid = db.Column(db.String(256), db.ForeignKey('user.userid'))

class FabricDefects(db.Model):
    __tablename__ = 'FabricDefects'
    id = db.Column(db.Integer, primary_key=True)
    defect = db.Column(db.Text, db.ForeignKey('defect.defect'), nullable=False)
    fabric_id = db.Column(db.Text, db.ForeignKey(Fabric.fabric_id), nullable=False)
    defectimage = db.Column(db.LargeBinary)
    defectGray = db.Column(db.LargeBinary)  # New column for grayscale image
    defectBoundary = db.Column(db.LargeBinary)
    coordinates = db.Column(db.Text)  # Column to store coordinates as string
    meters = db.Column(db.Float)  # Column to store meters as float value
    
    Fabric = db.relationship(Fabric, backref='FabricDefects')
    Defect = db.relationship(Defect, backref='FabricDefects')
