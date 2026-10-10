"""
<<<<<<< Updated upstream
Database Models for Smart Drug Recommendation System
=======
Enhanced Database Models for Smart Drug Recommendation System
NEW FEATURES:
- Dosage calculator support
- Drug shortage tracking
- Lab report storage
- User authentication (doctors/staff)
>>>>>>> Stashed changes
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User accounts for doctors/staff"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='doctor')  # doctor, admin, staff
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


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
<<<<<<< Updated upstream
    allergies = db.Column(db.Text)  # Comma-separated
    chronic_conditions = db.Column(db.Text)  # Past medical history
    
=======
    allergies = db.Column(db.Text)
    chronic_conditions = db.Column(db.Text)

    # 🆕 NEW: Weight for dosage calculation
    weight_kg = db.Column(db.Float)  # For mg/kg dosing
    height_cm = db.Column(db.Float)  # For BSA calculation

>>>>>>> Stashed changes
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    prescriptions = db.relationship('Prescription', backref='patient', lazy=True, cascade='all, delete-orphan')
    visits = db.relationship('PatientVisit', backref='patient', lazy=True, cascade='all, delete-orphan')
<<<<<<< Updated upstream
    
=======
    lab_reports = db.relationship('LabReport', backref='patient', lazy=True, cascade='all, delete-orphan')

>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
    
=======

    # 🆕 NEW: Advanced Dosage Calculation Fields
    weight_based_dosing = db.Column(db.Boolean, default=False)  # Is dosing weight-based?
    dose_per_kg = db.Column(db.String(100))  # e.g., "10-15 mg/kg/day"
    dose_calculation_formula = db.Column(db.Text)  # Custom formula if needed

    # 🆕 NEW: Administration Instructions
    administration_route = db.Column(db.String(100))  # Oral, IV, IM, etc.
    take_with_food = db.Column(db.String(20))  # YES/NO/EITHER
    special_instructions = db.Column(db.Text)  # e.g., "Take 30 min before meals"

>>>>>>> Stashed changes
    # Safety Information
    age_min = db.Column(db.Integer, default=0)
    age_max = db.Column(db.Integer, default=120)
    kidney_safe = db.Column(db.String(10), default='YES')  # YES/NO/CAUTION
    liver_safe = db.Column(db.String(10), default='YES')
    pregnancy_category = db.Column(db.String(10))  # A/B/C/D/X
    pregnancy_safe = db.Column(db.String(10), default='YES')
    lactation_safe = db.Column(db.String(10), default='YES')
<<<<<<< Updated upstream
    
=======

    # 🆕 NEW: Renal/Hepatic Dose Adjustments
    renal_dose_adjustment = db.Column(db.Text)  # Dosing for renal impairment
    hepatic_dose_adjustment = db.Column(db.Text)  # Dosing for hepatic impairment

    # 🆕 NEW: Drug Shortage Tracking
    in_stock = db.Column(db.Boolean, default=True)
    stock_level = db.Column(db.Integer, default=100)  # Percentage
    shortage_reason = db.Column(db.Text)
    alternative_drugs = db.Column(db.Text)  # JSON array of alternative drug IDs
    last_stock_update = db.Column(db.DateTime)

>>>>>>> Stashed changes
    # Additional Info
    storage_conditions = db.Column(db.String(200))
    manufacturer = db.Column(db.String(200))
    price = db.Column(db.Float)
    prescription_required = db.Column(db.Boolean, default=True)
<<<<<<< Updated upstream
    
    # Food Interactions
    food_interactions = db.Column(db.Text)  # JSON format
    
=======
    food_interactions = db.Column(db.Text)

>>>>>>> Stashed changes
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Drug {self.drug_name}>'
<<<<<<< Updated upstream
    
=======

    def get_alternatives(self):
        """Get alternative drugs for this drug"""
        if not self.alternative_drugs:
            return []
        try:
            alt_ids = json.loads(self.alternative_drugs)
            return Drug.query.filter(Drug.id.in_(alt_ids)).all()
        except:
            return []

>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
=======

    def to_dict(self):
        return {
            'drug1': self.drug1,
            'drug2': self.drug2,
            'severity': self.severity,
            'description': self.description,
            'mechanism': self.mechanism,
            'clinical_significance': self.clinical_significance,
            'management': self.management
        }
>>>>>>> Stashed changes


class Prescription(db.Model):
    """Prescription model"""
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    # Prescription Details
    drug_name = db.Column(db.String(200), nullable=False)
<<<<<<< Updated upstream
    dosage = db.Column(db.String(100))  # 500mg
    frequency = db.Column(db.String(50))  # BD, TDS, QID
    duration = db.Column(db.String(50))  # 5 days, 2 weeks
    quantity = db.Column(db.Integer)  # Number of tablets
    
=======
    dosage = db.Column(db.String(100))
    frequency = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    quantity = db.Column(db.Integer)

    # 🆕 NEW: Calculated Dosage Information
    calculated_dose = db.Column(db.String(200))  # Auto-calculated based on weight
    patient_weight_at_prescription = db.Column(db.Float)  # Weight used for calculation
    dosage_instructions = db.Column(db.Text)  # Detailed administration instructions

>>>>>>> Stashed changes
    # Medical Information
    diagnosis = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    clinical_notes = db.Column(db.Text)

    # Safety Information
    allergy_check_passed = db.Column(db.Boolean, default=True)
    interaction_check_passed = db.Column(db.Boolean, default=True)
    contraindication_check_passed = db.Column(db.Boolean, default=True)
<<<<<<< Updated upstream
    warnings = db.Column(db.Text)  # JSON format
    
=======
    warnings = db.Column(db.Text)

>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
    
    # Visit Information
=======

>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
=======

    def to_dict(self):
        return {
            'drug_name': self.drug_name,
            'food_item': self.food_item,
            'interaction_type': self.interaction_type,
            'severity': self.severity,
            'description': self.description,
            'recommendation': self.recommendation
        }


# 🆕 NEW: Lab Report Model for OCR feature
class LabReport(db.Model):
    """Lab report storage and OCR results"""
    __tablename__ = 'lab_reports'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    # File Information
    report_id = db.Column(db.String(50), unique=True, nullable=False)
    filename = db.Column(db.String(255))
    file_path = db.Column(db.String(500))
    file_type = db.Column(db.String(20))  # PDF, JPG, PNG

    # Report Details
    report_type = db.Column(db.String(100))  # Blood Test, X-Ray, etc.
    report_date = db.Column(db.Date)

    # Extracted Values (OCR)
    extracted_text = db.Column(db.Text)  # Raw OCR text
    hemoglobin = db.Column(db.Float)
    blood_sugar = db.Column(db.Float)
    creatinine = db.Column(db.Float)
    liver_enzyme = db.Column(db.Float)
    wbc_count = db.Column(db.Float)
    platelet_count = db.Column(db.Float)

    # OCR Metadata
    ocr_confidence = db.Column(db.Float)  # Confidence score
    extraction_status = db.Column(db.String(20))  # SUCCESS, FAILED, PARTIAL
    extraction_errors = db.Column(db.Text)  # JSON of errors

    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<LabReport {self.report_id} for Patient {self.patient_id}>'

    def to_dict(self):
        return {
            'report_id': self.report_id,
            'patient_id': self.patient_id,
            'filename': self.filename,
            'report_type': self.report_type,
            'report_date': self.report_date.strftime('%Y-%m-%d') if self.report_date else None,
            'hemoglobin': self.hemoglobin,
            'blood_sugar': self.blood_sugar,
            'creatinine': self.creatinine,
            'liver_enzyme': self.liver_enzyme,
            'ocr_confidence': self.ocr_confidence,
            'extraction_status': self.extraction_status,
            'uploaded_at': self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
        }


# 🆕 NEW: Drug Shortage Alert Model
class DrugShortageAlert(db.Model):
    """Track drug shortages and notify doctors"""
    __tablename__ = 'drug_shortage_alerts'

    id = db.Column(db.Integer, primary_key=True)
    drug_id = db.Column(db.Integer, db.ForeignKey('drugs.id'), nullable=False)

    # Shortage Details
    severity = db.Column(db.String(20))  # CRITICAL, HIGH, MEDIUM, LOW
    reason = db.Column(db.Text)
    estimated_availability_date = db.Column(db.Date)

    # Notification
    notification_sent = db.Column(db.Boolean, default=False)
    affected_prescriptions_count = db.Column(db.Integer, default=0)

    # Status
    status = db.Column(db.String(20), default='active')  # active, resolved
    resolved_at = db.Column(db.DateTime)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<DrugShortageAlert for Drug {self.drug_id}>'
>>>>>>> Stashed changes
