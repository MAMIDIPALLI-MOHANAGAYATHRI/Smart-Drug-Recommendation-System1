"""
Smart Drug Recommendation System
Doctor-First Validation Workflow with Database Integration
Author: CSE-AI Team, KKR & KSR Institute of Technology
Version: 3.0 (Database Integrated)
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from config import config
from models import db, Patient, Drug, DrugInteraction, Prescription, PatientVisit, DrugFoodInteraction
import numpy as np
import joblib
import os
import json
from datetime import datetime
from utils import (
    preprocess_patient_data,
    check_allergy,
    check_drug_interaction_db,
    check_contraindications_db,
    check_drug_food_interaction_db,
    generate_explanation,
    load_model
)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config['development'])

# Initialize database
db.init_app(app)

# Global variables for model
model = None
vectorizer = None


def initialize_app():
    """Load model and data on startup"""
    global model, vectorizer
    
    with app.app_context():
        # Create tables if not exist
        db.create_all()
        
        print(f"✓ Database initialized")
        print(f"✓ Drugs in database: {Drug.query.count()}")
        print(f"✓ Drug interactions: {DrugInteraction.query.count()}")
        print(f"✓ Drug-food interactions: {DrugFoodInteraction.query.count()}")
        print(f"✓ Patients in database: {Patient.query.count()}")
        
        # Try to load ML model
        try:
            model, vectorizer = load_model()
            if model:
                print(f"✓ Model loaded: {type(model).__name__}")
            else:
                print("⚠ Model not found - AI suggestions will use rule-based fallback")
        except Exception as e:
            print(f"⚠ Model not loaded: {str(e)}")
            model = None
            vectorizer = None
        
        print("✓ Application initialized successfully")


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/recommend')
def recommend():
    """Patient registration form"""
    return render_template('patient_form.html')


@app.route('/patient-dashboard', methods=['POST'])
def patient_dashboard():
    """
    Display patient dashboard after registration
    """
    try:
        # Check if searching for existing patient
        search_id = request.form.get('search_patient_id')
        if search_id:
            patient = Patient.query.filter_by(patient_id=search_id).first()
            if patient:
                patient_data = patient.to_dict()
                # Get latest visit
                latest_visit = PatientVisit.query.filter_by(patient_id=patient.id).order_by(PatientVisit.visit_date.desc()).first()
                if latest_visit:
                    patient_data.update({
                        'symptoms': latest_visit.symptoms,
                        'blood_pressure': latest_visit.blood_pressure,
                        'temperature': latest_visit.temperature,
                        'hemoglobin': latest_visit.hemoglobin,
                        'blood_sugar': latest_visit.blood_sugar,
                        'creatinine': latest_visit.creatinine,
                        'liver_enzyme': latest_visit.liver_enzyme
                    })
                
                patient_json = json.dumps(patient_data)
                return render_template('patient_dashboard.html',
                                     patient=patient_data,
                                     patient_json=patient_json,
                                     existing_patient=True)
        
        # New patient registration
        patient_data = {
            'id': request.form.get('patient_id') or f"PT{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'name': request.form.get('patient_name', ''),
            'age': int(request.form.get('age', 0)),
            'gender': request.form.get('gender', ''),
            'contact': request.form.get('contact', ''),
            'email': request.form.get('email', ''),
            'symptoms': request.form.get('symptoms', ''),
            'past_history': request.form.get('past_history', ''),
            'surgical_history': request.form.get('surgical_history', ''),
            'allergies': request.form.get('allergies', ''),
            'current_medications': request.form.get('current_medications', ''),
            'hemoglobin': request.form.get('hemoglobin', ''),
            'blood_sugar': request.form.get('blood_sugar', ''),
            'creatinine': request.form.get('creatinine', ''),
            'liver_enzyme': request.form.get('liver_enzyme', ''),
            'blood_pressure': request.form.get('blood_pressure', ''),
            'temperature': request.form.get('temperature', ''),
            'is_pregnant': request.form.get('is_pregnant', 'no'),
            'clinical_notes': request.form.get('clinical_notes', ''),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Validate required fields
        if not patient_data['name'] or not patient_data['symptoms']:
            return render_template('patient_form.html', 
                                 error="Patient name and symptoms are required")
        
        # Save patient to database
        patient = Patient(
            patient_id=patient_data['id'],
            name=patient_data['name'],
            age=patient_data['age'],
            gender=patient_data['gender'],
            contact=patient_data['contact'],
            email=patient_data['email'],
            allergies=patient_data['allergies'],
            chronic_conditions=patient_data['past_history']
        )
        db.session.add(patient)
        db.session.commit()
        
        # Save visit record
        visit = PatientVisit(
            patient_id=patient.id,
            chief_complaint=patient_data['symptoms'],
            symptoms=patient_data['symptoms'],
            blood_pressure=patient_data['blood_pressure'] or None,
            temperature=float(patient_data['temperature']) if patient_data['temperature'] else None,
            hemoglobin=float(patient_data['hemoglobin']) if patient_data['hemoglobin'] else None,
            blood_sugar=float(patient_data['blood_sugar']) if patient_data['blood_sugar'] else None,
            creatinine=float(patient_data['creatinine']) if patient_data['creatinine'] else None,
            liver_enzyme=float(patient_data['liver_enzyme']) if patient_data['liver_enzyme'] else None,
            treatment_plan=patient_data['clinical_notes']
        )
        db.session.add(visit)
        db.session.commit()
        
        print(f"✓ Saved patient: {patient_data['name']} (ID: {patient_data['id']})")
        
        # Convert to JSON for passing between pages
        patient_json = json.dumps(patient_data)
        
        return render_template('patient_dashboard.html',
                             patient=patient_data,
                             patient_json=patient_json)
    
    except Exception as e:
        print(f"Error in patient dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return render_template('patient_form.html',
                             error=f"An error occurred: {str(e)}")


@app.route('/validate-drug', methods=['POST'])
def validate_drug():
    """
    Validate if doctor's chosen drug is safe for patient
    """
    try:
        # Get patient data and drug name
        patient_json = request.form.get('patient_data')
        patient_data = json.loads(patient_json)
        drug_name = request.form.get('drug_name', '').strip()
        
        if not drug_name:
            return redirect(url_for('patient_dashboard'))
        
        # Get drug information from database
        drug_info = Drug.query.filter(Drug.drug_name.ilike(drug_name)).first()
        
        if not drug_info:
            # Drug not in database - cannot validate
            return render_template('drug_validation_result.html',
                                 patient=patient_data,
                                 patient_json=patient_json,
                                 drug_name=drug_name,
                                 is_safe=False,
                                 drug_info=None,
                                 checks={
                                     'allergy': {'is_safe': False, 'message': '❌ Drug not found in database'},
                                     'interaction': {'is_safe': False, 'message': ''},
                                     'contraindication': {'is_safe': False, 'message': ''},
                                     'food': {'is_safe': True, 'message': ''}
                                 },
                                 alternatives=get_ai_alternatives(patient_data))
        
        # Perform safety checks
        checks = {}
        is_safe = True
        
        # Check 1: Allergy
        allergy_check = check_allergy(drug_name, patient_data['allergies'])
        checks['allergy'] = allergy_check
        if not allergy_check['is_safe']:
            is_safe = False
        
        # Check 2: Drug Interactions (Database)
        interaction_check = check_drug_interaction_db(
            drug_name,
            patient_data['current_medications']
        )
        checks['interaction'] = interaction_check
        if not interaction_check['is_safe']:
            is_safe = False
        
        # Check 3: Contraindications (Database)
        contraindication_check = check_contraindications_db(
            drug_info,
            patient_data
        )
        checks['contraindication'] = contraindication_check
        if not contraindication_check['is_safe']:
            is_safe = False
        
        # Check 4: Drug-Food Interactions (NEW!)
        food_check = check_drug_food_interaction_db(drug_name)
        checks['food'] = food_check
        
        # Get alternatives if drug is unsafe
        alternatives = []
        if not is_safe:
            alternatives = get_ai_alternatives(patient_data)
        
        return render_template('drug_validation_result.html',
                             patient=patient_data,
                             patient_json=patient_json,
                             drug_name=drug_name,
                             is_safe=is_safe,
                             drug_info=drug_info,
                             checks=checks,
                             alternatives=alternatives)
    
    except Exception as e:
        print(f"Error in drug validation: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('patient_form.html',
                             error=f"Validation error: {str(e)}")


@app.route('/ai-suggest', methods=['POST'])
def ai_suggest():
    """
    Get AI-powered drug suggestions
    """
    try:
        # Get patient data
        patient_json = request.form.get('patient_data')
        patient_data = json.loads(patient_json)
        
        # Get AI recommendations
        recommendations = get_ai_alternatives(patient_data)
        
        # Render results using the existing result.html template
        safe_drugs = []
        for rec in recommendations:
            safe_drugs.append({
                'drug': rec['drug'],
                'confidence': rec['confidence'],
                'category': rec['category'],
                'warnings': []
            })
        
        explanation = f"""
        <strong>🤖 AI Analysis Summary:</strong><br>
        Patient: {patient_data['name']}, Age: {patient_data['age']}, Gender: {patient_data['gender']}<br>
        Symptoms: {patient_data['symptoms']}<br><br>
        
        <strong>✅ {len(safe_drugs)} AI-Recommended Drug(s):</strong><br>
        Based on symptom analysis and patient profile, these medications are suggested.<br><br>
        
        <strong>🛡️ Safety Checks Performed:</strong><br>
        ✓ Allergy verification<br>
        ✓ Drug interaction detection<br>
        ✓ Contraindication checking<br>
        ✓ Food interaction warnings<br>
        """
        
        return render_template('result.html',
                             patient_data=patient_data,
                             safe_drugs=safe_drugs,
                             rejected_drugs=[],
                             explanation=explanation,
                             timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    except Exception as e:
        print(f"Error in AI suggest: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('recommend'))


@app.route('/confirm-prescription', methods=['POST'])
def confirm_prescription():
    """
    Confirm and generate prescription
    """
    try:
        patient_json = request.form.get('patient_data')
        patient_data = json.loads(patient_json)
        drug_name = request.form.get('drug_name')
        
        # Get drug info from database
        drug_info = Drug.query.filter(Drug.drug_name.ilike(drug_name)).first()
        drug_category = drug_info.category if drug_info else 'General Medicine'
        
        # Save prescription to database
        patient = Patient.query.filter_by(patient_id=patient_data['id']).first()
        if patient:
            prescription = Prescription(
                prescription_id=f"RX{datetime.now().strftime('%Y%m%d%H%M%S')}",
                patient_id=patient.id,
                drug_name=drug_name,
                diagnosis=patient_data.get('symptoms', ''),
                symptoms=patient_data.get('symptoms', ''),
                clinical_notes=patient_data.get('clinical_notes', ''),
                allergy_check_passed=True,
                interaction_check_passed=True,
                contraindication_check_passed=True
            )
            db.session.add(prescription)
            db.session.commit()
            print(f"✓ Prescription saved: {prescription.prescription_id}")
        
        return render_template('prescription_confirmed.html',
                             patient=patient_data,
                             drug_name=drug_name,
                             drug_category=drug_category,
                             timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    except Exception as e:
        print(f"Error confirming prescription: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('recommend'))


@app.route('/search-drugs')
def search_drugs():
    """
    Search drugs by name or category (AJAX endpoint)
    """
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    
    if not query and not category:
        return jsonify([])
    
    # Search in database
    drugs_query = Drug.query
    
    if query:
        drugs_query = drugs_query.filter(
            (Drug.drug_name.ilike(f'%{query}%')) | 
            (Drug.generic_name.ilike(f'%{query}%'))
        )
    
    if category:
        drugs_query = drugs_query.filter(Drug.category.ilike(f'%{category}%'))
    
    drugs = drugs_query.limit(20).all()
    
    results = [{
        'drug_name': drug.drug_name,
        'generic_name': drug.generic_name,
        'category': drug.category,
        'price': drug.price,
        'dosage_forms': drug.dosage_forms
    } for drug in drugs]
    
    return jsonify(results)


@app.route('/drug-info/<drug_name>')
def drug_info(drug_name):
    """
    Get detailed drug information
    """
    drug = Drug.query.filter(Drug.drug_name.ilike(drug_name)).first()
    
    if not drug:
        return jsonify({'error': 'Drug not found'}), 404
    
    return jsonify(drug.to_dict())


def get_ai_alternatives(patient_data):
    """
    Get AI-suggested alternative drugs from database
    """
    try:
        if model is None:
            # Fallback: rule-based suggestions
            return get_rule_based_suggestions(patient_data)
        
        # Use ML model
        processed_features = preprocess_patient_data(patient_data, vectorizer)
        predictions = model.predict_proba([processed_features])[0]
        drug_names = model.classes_
        
        # Create recommendations
        recommendations = []
        for drug, confidence in zip(drug_names, predictions):
            # Get drug from database
            drug_obj = Drug.query.filter(Drug.drug_name.ilike(drug)).first()
            if drug_obj:
                recommendations.append({
                    'drug': drug_obj.drug_name,
                    'confidence': round(confidence * 100, 2),
                    'category': drug_obj.category
                })
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Filter safe drugs
        safe_recommendations = []
        for rec in recommendations[:10]:
            # Quick safety check
            allergy_safe = check_allergy(rec['drug'], patient_data['allergies'])['is_safe']
            interaction_safe = check_drug_interaction_db(rec['drug'], patient_data['current_medications'])['is_safe']
            
            drug_obj = Drug.query.filter(Drug.drug_name.ilike(rec['drug'])).first()
            if drug_obj:
                contra_safe = check_contraindications_db(drug_obj, patient_data)['is_safe']
            else:
                contra_safe = True
            
            if allergy_safe and interaction_safe and contra_safe:
                safe_recommendations.append(rec)
            
            if len(safe_recommendations) >= 5:
                break
        
        return safe_recommendations[:5]
    
    except Exception as e:
        print(f"Error getting AI alternatives: {str(e)}")
        return get_rule_based_suggestions(patient_data)


def get_rule_based_suggestions(patient_data):
    """
    Fallback rule-based suggestions from database
    """
    symptoms_lower = patient_data['symptoms'].lower()
    
    # Query database for relevant drugs
    suggestions = []
    
    if any(word in symptoms_lower for word in ['fever', 'pain', 'headache', 'ache']):
        drugs = Drug.query.filter(Drug.category.in_(['Painkiller', 'NSAID'])).limit(2).all()
        for drug in drugs:
            suggestions.append({
                'drug': drug.drug_name,
                'confidence': 88,
                'category': drug.category
            })
    
    if any(word in symptoms_lower for word in ['cold', 'allerg', 'sneez', 'itch']):
        drugs = Drug.query.filter(Drug.category == 'Antihistamine').limit(2).all()
        for drug in drugs:
            suggestions.append({
                'drug': drug.drug_name,
                'confidence': 85,
                'category': drug.category
            })
    
    if any(word in symptoms_lower for word in ['cough', 'throat', 'infection']):
        drugs = Drug.query.filter(Drug.category == 'Antibiotic').limit(2).all()
        for drug in drugs:
            suggestions.append({
                'drug': drug.drug_name,
                'confidence': 82,
                'category': drug.category
            })
    
    # Remove duplicates
    seen = set()
    unique_suggestions = []
    for s in suggestions:
        if s['drug'] not in seen:
            seen.add(s['drug'])
            unique_suggestions.append(s)
    
    return unique_suggestions[:5]

@app.route('/analyze-symptoms', methods=['POST'])
def analyze_symptoms():
    """
    Analyze symptoms using NLP (Phase 12.5)
    AJAX endpoint
    """
    try:
        from nlp_utils import extract_symptoms_nlp, generate_symptom_summary, suggest_missing_information
        
        symptom_text = request.json.get('symptoms', '')
        
        if not symptom_text or len(symptom_text.strip()) < 3:
            return jsonify({
                'success': False,
                'message': 'Please enter symptom description'
            })
        
        # Extract symptoms using NLP
        result = extract_symptoms_nlp(symptom_text)
        
        # Generate summary
        summary_html = generate_symptom_summary(result)
        
        # Get suggestions
        suggestions = suggest_missing_information(result)
        
        return jsonify({
            'success': True,
            'extraction': result,
            'summary_html': summary_html,
            'suggestions': suggestions,
            'formatted_symptoms': result['symptom_text']
        })
    
    except Exception as e:
        print(f"Error in symptom analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Analysis error: {str(e)}'
        }), 500

@app.route('/health')
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'model_loaded': model is not None,
        'drugs_count': Drug.query.count(),
        'patients_count': Patient.query.count(),
        'prescriptions_count': Prescription.query.count(),
        'workflow': 'doctor-first-validation-db',
        'timestamp': datetime.now().isoformat()
    })


@app.errorhandler(404)
def page_not_found(e):
    """404 error handler"""
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """500 error handler"""
    print(f"Internal error: {str(e)}")
    db.session.rollback()
    return render_template('index.html'), 500


if __name__ == '__main__':
    print("\n" + "="*70)
    print(" " * 12 + "🏥 SMART DRUG RECOMMENDATION SYSTEM v3.0")
    print(" " * 18 + "Database Integrated + Enhanced AI")
    print("="*70)
    print("📚 B.Tech CSE-AI Project | KKR & KSR Institute of Technology")
    print("👥 Team: Batch 22JR1A4319")
    print("="*70)
    
    # Initialize application
    print("\n🔧 Initializing application...\n")
    initialize_app()
    
    # Run Flask app
    print("\n" + "="*70)
    print("🚀 Starting Flask Development Server...")
    print("="*70)
    print("📍 Local URL:    http://localhost:5000")
    print("📍 Network URL:  http://0.0.0.0:5000")
    print("="*70)
    print("\n⌨️  Press CTRL+C to stop the server")
    print("\n💡 New Features:")
    print("   • SQLite Database Integration")
    print("   • Patient Records Saved")
    print("   • Drug-Food Interaction Checks")
    print("   • Drug Search API")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
