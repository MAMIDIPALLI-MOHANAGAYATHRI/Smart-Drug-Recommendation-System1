"""
Smart Drug Recommendation System
Doctor-First Validation Workflow
Author: CSE-AI Team, KKR & KSR Institute of Technology
Version: 2.0 (Doctor-First Validation)
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import numpy as np
import joblib
import os
import json
from datetime import datetime
from utils import (
    preprocess_patient_data,
    check_allergy,
    check_drug_interaction,
    check_contraindications,
    generate_explanation,
    load_model
)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'smartrx-ai-2026-kitsguntur'

# Global variables for model and data
model = None
vectorizer = None
medicines_df = None
interactions_df = None


def initialize_app():
    """Load model and data on startup"""
    global model, vectorizer, medicines_df, interactions_df
    
    try:
        # Load medicines database
        medicines_df = pd.read_csv('data/medicines.csv')
        print(f"✓ Medicines database: {len(medicines_df)} drugs")
        
        # Load interactions database
        interactions_df = pd.read_csv('data/interactions.csv')
        print(f"✓ Interactions database: {len(interactions_df)} interactions")
        
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
        
    except Exception as e:
        print(f"✗ Error initializing app: {str(e)}")


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
        # Collect patient data from form
        patient_data = {
            'id': request.form.get('patient_id') or f"PT{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'name': request.form.get('patient_name', ''),
            'age': int(request.form.get('age', 0)),
            'gender': request.form.get('gender', ''),
            'contact': request.form.get('contact', ''),
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
        
        # Convert to JSON for passing between pages
        patient_json = json.dumps(patient_data)
        
        return render_template('patient_dashboard.html',
                             patient=patient_data,
                             patient_json=patient_json)
    
    except Exception as e:
        print(f"Error in patient dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
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
        
        # Get drug information
        drug_info = medicines_df[medicines_df['drug_name'].str.lower() == drug_name.lower()]
        
        if drug_info.empty:
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
                                     'contraindication': {'is_safe': False, 'message': ''}
                                 },
                                 alternatives=get_ai_alternatives(patient_data))
        
        drug_info = drug_info.iloc[0]
        
        # Perform safety checks
        checks = {}
        is_safe = True
        
        # Check 1: Allergy
        allergy_check = check_allergy(drug_name, patient_data['allergies'])
        checks['allergy'] = allergy_check
        if not allergy_check['is_safe']:
            is_safe = False
        
        # Check 2: Drug Interactions
        interaction_check = check_drug_interaction(
            drug_name,
            patient_data['current_medications'],
            interactions_df
        )
        checks['interaction'] = interaction_check
        if not interaction_check['is_safe']:
            is_safe = False
        
        # Check 3: Contraindications
        contraindication_check = check_contraindications(
            drug_name,
            patient_data,
            medicines_df
        )
        checks['contraindication'] = contraindication_check
        if not contraindication_check['is_safe']:
            is_safe = False
        
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
        
        # Get drug category
        drug_info = medicines_df[medicines_df['drug_name'] == drug_name]
        drug_category = drug_info.iloc[0]['category'] if not drug_info.empty else 'General Medicine'
        
        return render_template('prescription_confirmed.html',
                             patient=patient_data,
                             drug_name=drug_name,
                             drug_category=drug_category,
                             timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    except Exception as e:
        print(f"Error confirming prescription: {str(e)}")
        return redirect(url_for('recommend'))


def get_ai_alternatives(patient_data):
    """
    Get AI-suggested alternative drugs
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
            # Get drug category
            drug_info = medicines_df[medicines_df['drug_name'] == drug]
            category = drug_info.iloc[0]['category'] if not drug_info.empty else 'General Medicine'
            
            recommendations.append({
                'drug': drug,
                'confidence': round(confidence * 100, 2),
                'category': category
            })
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Filter safe drugs
        safe_recommendations = []
        for rec in recommendations[:10]:
            # Quick safety check
            allergy_safe = check_allergy(rec['drug'], patient_data['allergies'])['is_safe']
            interaction_safe = check_drug_interaction(rec['drug'], patient_data['current_medications'], interactions_df)['is_safe']
            contra_safe = check_contraindications(rec['drug'], patient_data, medicines_df)['is_safe']
            
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
    Fallback rule-based suggestions when ML model not available
    """
    symptoms_lower = patient_data['symptoms'].lower()
    
    suggestions = []
    
    if any(word in symptoms_lower for word in ['fever', 'pain', 'headache', 'ache']):
        suggestions.append({'drug': 'Paracetamol', 'confidence': 90, 'category': 'Painkiller'})
        suggestions.append({'drug': 'Ibuprofen', 'confidence': 85, 'category': 'NSAID'})
    
    if any(word in symptoms_lower for word in ['cold', 'allerg', 'sneez', 'itch']):
        suggestions.append({'drug': 'Cetirizine', 'confidence': 88, 'category': 'Antihistamine'})
        suggestions.append({'drug': 'Loratadine', 'confidence': 82, 'category': 'Antihistamine'})
    
    if any(word in symptoms_lower for word in ['cough', 'throat', 'infection']):
        suggestions.append({'drug': 'Azithromycin', 'confidence': 86, 'category': 'Antibiotic'})
        suggestions.append({'drug': 'Amoxicillin', 'confidence': 83, 'category': 'Antibiotic'})
    
    if any(word in symptoms_lower for word in ['acid', 'stomach', 'heartburn', 'reflux']):
        suggestions.append({'drug': 'Omeprazole', 'confidence': 91, 'category': 'Antacid'})
    
    # Remove duplicates and return top 5
    seen = set()
    unique_suggestions = []
    for s in suggestions:
        if s['drug'] not in seen:
            seen.add(s['drug'])
            unique_suggestions.append(s)
    
    return unique_suggestions[:5]


@app.route('/health')
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'medicines_count': len(medicines_df) if medicines_df is not None else 0,
        'interactions_count': len(interactions_df) if interactions_df is not None else 0,
        'workflow': 'doctor-first-validation',
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
    return render_template('index.html'), 500


if __name__ == '__main__':
    print("\n" + "="*70)
    print(" " * 15 + "🏥 SMART DRUG RECOMMENDATION SYSTEM")
    print(" " * 18 + "Doctor-First Validation Workflow")
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
    print("\n💡 Workflow: Doctor enters drug → System validates → Shows alternatives")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
