"""
Database Models for Smart Drug Recommendation System
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Patient(db.Model):
    """Patient information model"""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    contact = db.Column(db.String(50))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    
    # Medical Information
    blood_group = db.Column(db.String(10))
    allergies = db.Column(db.Text)  # Comma-separated
    chronic_conditions = db.Column(db.Text)  # Past medical history
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    prescriptions = db.relationship('Prescription', backref='patient', lazy=True, cascade='all, delete-orphan')
    visits = db.relationship('PatientVisit', backref='patient', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Patient {self.patient_id} - {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'contact': self.contact,
            'email': self.email,
            'allergies': self.allergies,
            'chronic_conditions': self.chronic_conditions,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class Drug(db.Model):
    """Drug information model"""
    __tablename__ = 'drugs'
    
    id = db.Column(db.Integer, primary_key=True)
    drug_name = db.Column(db.String(200), nullable=False, unique=True, index=True)
    generic_name = db.Column(db.String(200))
    brand_names = db.Column(db.Text)  # Comma-separated
    category = db.Column(db.String(100), nullable=False, index=True)
    drug_class = db.Column(db.String(100))
    
    # Medical Information
    indication = db.Column(db.Text)  # What it treats
    mechanism_of_action = db.Column(db.Text)
    side_effects = db.Column(db.Text)
    contraindications = db.Column(db.Text)
    
    # Dosage Information
    dosage_forms = db.Column(db.String(200))  # tablet, syrup, injection
    standard_dosage = db.Column(db.String(200))  # 500mg BD
    max_daily_dose = db.Column(db.String(100))
    
    # Safety Information
    age_min = db.Column(db.Integer, default=0)
    age_max = db.Column(db.Integer, default=120)
    kidney_safe = db.Column(db.String(10), default='YES')  # YES/NO/CAUTION
    liver_safe = db.Column(db.String(10), default='YES')
    pregnancy_category = db.Column(db.String(10))  # A/B/C/D/X
    pregnancy_safe = db.Column(db.String(10), default='YES')
    lactation_safe = db.Column(db.String(10), default='YES')
    
    # Additional Info
    storage_conditions = db.Column(db.String(200))
    manufacturer = db.Column(db.String(200))
    price = db.Column(db.Float)
    prescription_required = db.Column(db.Boolean, default=True)
    
    # Food Interactions
    food_interactions = db.Column(db.Text)  # JSON format
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Drug {self.drug_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'drug_name': self.drug_name,
            'generic_name': self.generic_name,
            'brand_names': self.brand_names,
            'category': self.category,
            'indication': self.indication,
            'side_effects': self.side_effects,
            'dosage_forms': self.dosage_forms,
            'standard_dosage': self.standard_dosage,
            'price': self.price,
            'pregnancy_category': self.pregnancy_category
        }


class DrugInteraction(db.Model):
    """Drug-drug interaction model"""
    __tablename__ = 'drug_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    drug1 = db.Column(db.String(200), nullable=False, index=True)
    drug2 = db.Column(db.String(200), nullable=False, index=True)
    severity = db.Column(db.String(20), nullable=False)  # severe/moderate/minor
    description = db.Column(db.Text)
    management = db.Column(db.Text)  # How to manage the interaction
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Interaction {self.drug1} + {self.drug2} ({self.severity})>'


class Prescription(db.Model):
    """Prescription model"""
    __tablename__ = 'prescriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    
    # Prescription Details
    drug_name = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(100))  # 500mg
    frequency = db.Column(db.String(50))  # BD, TDS, QID
    duration = db.Column(db.String(50))  # 5 days, 2 weeks
    quantity = db.Column(db.Integer)  # Number of tablets
    
    # Medical Information
    diagnosis = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    clinical_notes = db.Column(db.Text)
    
    # Safety Information
    allergy_check_passed = db.Column(db.Boolean, default=True)
    interaction_check_passed = db.Column(db.Boolean, default=True)
    contraindication_check_passed = db.Column(db.Boolean, default=True)
    warnings = db.Column(db.Text)  # JSON format
    
    # Status
    status = db.Column(db.String(20), default='active')  # active/completed/cancelled
    refillable = db.Column(db.Boolean, default=False)
    refill_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    prescribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Prescription {self.prescription_id}>'
    
    def to_dict(self):
        return {
            'prescription_id': self.prescription_id,
            'patient_name': self.patient.name,
            'drug_name': self.drug_name,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'duration': self.duration,
            'diagnosis': self.diagnosis,
            'prescribed_at': self.prescribed_at.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status
        }


class PatientVisit(db.Model):
    """Patient visit history"""
    __tablename__ = 'patient_visits'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    
    # Visit Information
    visit_date = db.Column(db.DateTime, default=datetime.utcnow)
    chief_complaint = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    
    # Vital Signs
    blood_pressure = db.Column(db.String(20))
    temperature = db.Column(db.Float)
    pulse = db.Column(db.Integer)
    weight = db.Column(db.Float)
    
    # Lab Reports
    hemoglobin = db.Column(db.Float)
    blood_sugar = db.Column(db.Float)
    creatinine = db.Column(db.Float)
    liver_enzyme = db.Column(db.Float)
    
    # Clinical Notes
    diagnosis = db.Column(db.Text)
    treatment_plan = db.Column(db.Text)
    follow_up_date = db.Column(db.Date)
    
    def __repr__(self):
        return f'<Visit {self.patient.name} on {self.visit_date}>'


class DrugFoodInteraction(db.Model):
    """Drug-food interaction model"""
    __tablename__ = 'drug_food_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    drug_name = db.Column(db.String(200), nullable=False, index=True)
    food_item = db.Column(db.String(200), nullable=False)
    interaction_type = db.Column(db.String(50))  # avoid/take_with/take_without
    severity = db.Column(db.String(20))  # severe/moderate/minor
    description = db.Column(db.Text)
    recommendation = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DrugFood {self.drug_name} - {self.food_item}>'
