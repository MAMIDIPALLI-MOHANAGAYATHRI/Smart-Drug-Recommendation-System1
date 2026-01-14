"""
Smart Drug Recommendation System
Main Flask Application
Author: CSE-AI Team, KKR & KSR Institute of Technology
Version: 1.0 (Test Mode Enabled)
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import joblib
import os
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
        
        # Try to load ML model (optional for testing)
        try:
            model, vectorizer = load_model()
            if model:
                print(f"✓ Model loaded: {type(model).__name__}")
            else:
                print("⚠ Model not found - will use dummy predictions for testing")
        except Exception as e:
            print(f"⚠ Model not loaded - using test mode: {str(e)}")
            model = None
            vectorizer = None
        
        print("✓ Application initialized successfully")
        
    except Exception as e:
        print(f"✗ Error initializing app: {str(e)}")
        print("Please ensure data files exist in data/ folder")


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/recommend')
def recommend():
    """Patient form page"""
    return render_template('patient_form.html')


@app.route('/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint
    Process patient data and return drug recommendations
    """
    try:
        # Get form data
        patient_data = {
            'name': request.form.get('patient_name', ''),
            'age': int(request.form.get('age', 0)),
            'gender': request.form.get('gender', ''),
            'symptoms': request.form.get('symptoms', ''),
            'medical_history': request.form.get('medical_history', ''),
            'allergies': request.form.get('allergies', ''),
            'current_medications': request.form.get('current_medications', ''),
            'creatinine': request.form.get('creatinine', ''),
            'liver_enzyme': request.form.get('liver_enzyme', ''),
            'is_pregnant': request.form.get('is_pregnant', 'no')
        }
        
        # Validate required fields
        if not patient_data['symptoms']:
            return render_template('patient_form.html', 
                                 error="Please enter at least one symptom")
        
        # Check if model is loaded
        if model is None:
            # TEMPORARY: Use dummy predictions for testing
            print("⚠ Using dummy predictions (test mode)")
            
            # Simple symptom-based dummy recommendations
            symptoms_lower = patient_data['symptoms'].lower()
            
            # Smart dummy predictions based on symptoms
            if 'fever' in symptoms_lower or 'pain' in symptoms_lower or 'headache' in symptoms_lower:
                top_candidates = [
                    {'drug': 'Paracetamol', 'confidence': 92.5},
                    {'drug': 'Ibuprofen', 'confidence': 85.3},
                    {'drug': 'Aspirin', 'confidence': 78.9},
                    {'drug': 'Cetirizine', 'confidence': 72.1},
                    {'drug': 'Amoxicillin', 'confidence': 65.8}
                ]
            elif 'cold' in symptoms_lower or 'allerg' in symptoms_lower or 'sneez' in symptoms_lower:
                top_candidates = [
                    {'drug': 'Cetirizine', 'confidence': 91.2},
                    {'drug': 'Loratadine', 'confidence': 87.4},
                    {'drug': 'Paracetamol', 'confidence': 76.8},
                    {'drug': 'Azithromycin', 'confidence': 68.3},
                    {'drug': 'Amoxicillin', 'confidence': 62.5}
                ]
            elif 'cough' in symptoms_lower or 'throat' in symptoms_lower:
                top_candidates = [
                    {'drug': 'Azithromycin', 'confidence': 89.7},
                    {'drug': 'Amoxicillin', 'confidence': 84.2},
                    {'drug': 'Paracetamol', 'confidence': 77.6},
                    {'drug': 'Cetirizine', 'confidence': 71.3},
                    {'drug': 'Omeprazole', 'confidence': 64.8}
                ]
            elif 'acid' in symptoms_lower or 'stomach' in symptoms_lower or 'heartburn' in symptoms_lower:
                top_candidates = [
                    {'drug': 'Omeprazole', 'confidence': 93.4},
                    {'drug': 'Paracetamol', 'confidence': 79.2},
                    {'drug': 'Cetirizine', 'confidence': 68.7},
                    {'drug': 'Amoxicillin', 'confidence': 62.1},
                    {'drug': 'Azithromycin', 'confidence': 58.9}
                ]
            else:
                # Default recommendations
                top_candidates = [
                    {'drug': 'Paracetamol', 'confidence': 88.5},
                    {'drug': 'Cetirizine', 'confidence': 82.3},
                    {'drug': 'Amoxicillin', 'confidence': 75.9},
                    {'drug': 'Ibuprofen', 'confidence': 69.4},
                    {'drug': 'Omeprazole', 'confidence': 63.7}
                ]
        else:
            # Use real ML predictions
            print("✓ Using trained ML model")
            processed_features = preprocess_patient_data(patient_data, vectorizer)
            predictions = model.predict_proba([processed_features])[0]
            drug_names = model.classes_
            
            # Create recommendations list
            recommendations = []
            for drug, confidence in zip(drug_names, predictions):
                recommendations.append({
                    'drug': drug,
                    'confidence': round(confidence * 100, 2)
                })
            
            # Sort by confidence (descending)
            recommendations.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Take top 5 candidates
            top_candidates = recommendations[:5]
        
        # Apply safety checks to all candidates
        safe_drugs = []
        rejected_drugs = []
        
        for candidate in top_candidates:
            drug_name = candidate['drug']
            confidence = candidate['confidence']
            warnings = []
            
            # Safety Check 1: Allergy verification
            allergy_check = check_allergy(drug_name, patient_data['allergies'])
            if not allergy_check['is_safe']:
                rejected_drugs.append({
                    'drug': drug_name,
                    'confidence': confidence,
                    'reason': allergy_check['message']
                })
                continue
            
            # Safety Check 2: Drug interaction detection
            interaction_check = check_drug_interaction(
                drug_name, 
                patient_data['current_medications'],
                interactions_df
            )
            if not interaction_check['is_safe']:
                rejected_drugs.append({
                    'drug': drug_name,
                    'confidence': confidence,
                    'reason': interaction_check['message']
                })
                continue
            elif interaction_check['warning']:
                warnings.append(interaction_check['warning'])
            
            # Safety Check 3: Contraindication checking
            contraindication_check = check_contraindications(
                drug_name,
                patient_data,
                medicines_df
            )
            if not contraindication_check['is_safe']:
                rejected_drugs.append({
                    'drug': drug_name,
                    'confidence': confidence,
                    'reason': contraindication_check['message']
                })
                continue
            elif contraindication_check['warning']:
                warnings.append(contraindication_check['warning'])
            
            # Drug passed all safety checks - add to safe recommendations
            safe_drugs.append({
                'drug': drug_name,
                'confidence': confidence,
                'warnings': warnings,
                'category': get_drug_category(drug_name, medicines_df)
            })
        
        # Generate explanation
        explanation = generate_explanation(
            safe_drugs,
            rejected_drugs,
            patient_data
        )
        
        # Log results
        print(f"\n{'='*60}")
        print(f"Patient: {patient_data['name']}, Age: {patient_data['age']}")
        print(f"Symptoms: {patient_data['symptoms']}")
        print(f"Safe Drugs: {len(safe_drugs)}, Rejected: {len(rejected_drugs)}")
        print(f"{'='*60}\n")
        
        # Render results page
        return render_template('result.html',
                             patient_data=patient_data,
                             safe_drugs=safe_drugs,
                             rejected_drugs=rejected_drugs,
                             explanation=explanation,
                             timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    except Exception as e:
        print(f"\n✗ Error in prediction: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('patient_form.html',
                             error=f"An error occurred: {str(e)}")


def get_drug_category(drug_name, medicines_df):
    """Get drug category from medicines database"""
    try:
        drug_info = medicines_df[medicines_df['drug_name'] == drug_name]
        if not drug_info.empty:
            return drug_info.iloc[0]['category']
        else:
            return 'General Medicine'
    except Exception as e:
        print(f"Error getting drug category: {str(e)}")
        return 'General Medicine'


@app.route('/about')
def about():
    """About page"""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'medicines_count': len(medicines_df) if medicines_df is not None else 0,
        'interactions_count': len(interactions_df) if interactions_df is not None else 0,
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


# Context processor to inject variables into all templates
@app.context_processor
def inject_system_info():
    """Make system info available to all templates"""
    return {
        'system_name': 'SmartRx',
        'version': '1.0',
        'year': datetime.now().year
    }


if __name__ == '__main__':
    print("\n" + "="*70)
    print(" " * 15 + "🏥 SMART DRUG RECOMMENDATION SYSTEM")
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
    print("\n💡 Test Mode: Using dummy predictions (train model for real predictions)")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
