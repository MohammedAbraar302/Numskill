from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
import json

db = SQLAlchemy()

class User(db.Model):
    """User model for storing login credentials"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    profiles = db.relationship('CandidateProfile', backref='user', lazy=True, cascade='all, delete-orphan')
    scores = db.relationship('AssessmentScore', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and store password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        return {'id': self.id, 'username': self.username, 'email': self.email, 'created_at': self.created_at.isoformat()}


class CandidateProfile(db.Model):
    """Store candidate profile information"""
    __tablename__ = 'candidate_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    child_name = db.Column(db.String(120), nullable=False)
    child_age = db.Column(db.Integer, nullable=False)
    parent_name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'child_name': self.child_name,
            'child_age': self.child_age,
            'parent_name': self.parent_name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class AssessmentScore(db.Model):
    """Store assessment scores and results"""
    __tablename__ = 'assessment_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    module_name = db.Column(db.String(50), nullable=False)  # magnitude, estimation, facts, etc.
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    answers_json = db.Column(db.Text)  # Store answers as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_answers(self, answers_dict):
        """Store answers as JSON"""
        self.answers_json = json.dumps(answers_dict)
    
    def get_answers(self):
        """Retrieve answers from JSON"""
        return json.loads(self.answers_json) if self.answers_json else {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'module_name': self.module_name,
            'score': self.score,
            'total_questions': self.total_questions,
            'percentage': self.percentage,
            'created_at': self.created_at.isoformat()
        }


class ChecklistResponse(db.Model):
    """Store symptom checklist responses"""
    __tablename__ = 'checklist_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    responses_json = db.Column(db.Text)  # Store all responses as JSON
    total_score = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_responses(self, responses_dict):
        """Store responses as JSON"""
        self.responses_json = json.dumps(responses_dict)
    
    def get_responses(self):
        """Retrieve responses from JSON"""
        return json.loads(self.responses_json) if self.responses_json else {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'total_score': self.total_score,
            'created_at': self.created_at.isoformat()
        }


class GameScore(db.Model):
    """Store game scores"""
    __tablename__ = 'game_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_name = db.Column(db.String(50), nullable=False)  # neon_runner, aqua_math, fact_match
    score = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'game_name': self.game_name,
            'score': self.score,
            'created_at': self.created_at.isoformat()
        }
