"""
Database Models for Diabetes Predictor Application
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and profile management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    language = db.Column(db.String(10), default='en')
    theme = db.Column(db.String(10), default='light')  # 'light' or 'dark'
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    predictions = db.relationship('PredictionHistory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Override get_id for Flask-Login"""
        return str(self.id)
    
    def __repr__(self):
        return f'<User {self.username}>'


class PredictionHistory(db.Model):
    """Model to store prediction history for trend analysis"""
    __tablename__ = 'prediction_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Input features
    pregnancies = db.Column(db.Integer)
    glucose = db.Column(db.Float)
    blood_pressure = db.Column(db.Float)
    skin_thickness = db.Column(db.Float)
    insulin = db.Column(db.Float)
    bmi = db.Column(db.Float)
    dpf = db.Column(db.Float)
    age = db.Column(db.Integer)
    
    # Prediction results
    prediction = db.Column(db.Integer)  # 0 or 1
    confidence = db.Column(db.Float)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'pregnancies': self.pregnancies,
            'glucose': self.glucose,
            'blood_pressure': self.blood_pressure,
            'skin_thickness': self.skin_thickness,
            'insulin': self.insulin,
            'bmi': self.bmi,
            'dpf': self.dpf,
            'age': self.age,
            'prediction': self.prediction,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat(),
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<PredictionHistory {self.id} - User {self.user_id}>'


class ChatMessage(db.Model):
    """Model to store chatbot conversations"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', backref='chat_messages')
    
    def __repr__(self):
        return f'<ChatMessage {self.id}>'
