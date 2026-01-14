"""
Smart Drug Recommendation System
Utility Functions for Data Processing and Safety Checks
"""

import pandas as pd
import numpy as np
import joblib
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer


def load_model():
    """Load trained ML model and vectorizer"""
    try:
        model_path = 'models/drug_model.pkl'
        vectorizer_path = 'models/vectorizer.pkl'
        
        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            model = joblib.load(model_path)
            vectorizer = joblib.load(vectorizer_path)
            return model, vectorizer
        else:
            print("⚠ Model files not found. Please train the model first.")
            return None, None
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return None, None


def preprocess_patient_data(patient_data, vectorizer):
    """
    Preprocess patient data for ML model input
    
    Args:
        patient_data: Dictionary with patient information
        vectorizer: Fitted TF-IDF vectorizer
    
    Returns:
        Processed feature vector
    """
    try:
        # Extract and clean symptoms
        symptoms_text = patient_data['symptoms'].lower().strip()
        symptoms_text = re.sub(r'[^a-zA-Z,\s]', '', symptoms_text)
        
        # Add medical history if available
        if patient_data['medical_history']:
            history_text = patient_data['medical_history'].lower().strip()
            symptoms_text += ' ' + re.sub(r'[^a-zA-Z,\s]', '', history_text)
        
        # Transform using vectorizer
        if vectorizer:
            text_features = vectorizer.transform([symptoms_text]).toarray()[0]
        else:
            # Fallback: simple feature extraction
            text_features = np.zeros(100)
        
        # Add numerical features
        age = float(patient_data['age'])
        gender_encoded = 1 if patient_data['gender'] == 'Male' else 0
        
        # Combine features
        feature_vector = np.concatenate([
            text_features,
            [age, gender_encoded]
        ])
        
        return feature_vector
    
    except Exception as e:
        print(f"Error in preprocessing: {str(e)}")
        return np.zeros(102)  # Return zero vector as fallback


def check_allergy(drug_name, allergies_string):
    """
    Check if drug triggers patient allergies
    
    Args:
        drug_name: Name of the drug
        allergies_string: Comma-separated allergy list
    
    Returns:
        Dictionary with is_safe boolean and message
    """
    if not allergies_string or allergies_string.strip() == '':
        return {'is_safe': True, 'message': ''}
    
    # Parse allergies
    allergies_list = [a.strip().lower() for a in allergies_string.split(',')]
    drug_lower = drug_name.lower()
    
    # Check for exact match or substring
    for allergy in allergies_list:
        if allergy in drug_lower or drug_lower in allergy:
            return {
                'is_safe': False,
                'message': f'❌ Allergy Alert: Patient allergic to {allergy}'
            }
    
    return {'is_safe': True, 'message': ''}


def check_drug_interaction(drug_name, current_medications, interactions_df):
    """
    Check for drug-drug interactions
    
    Args:
        drug_name: Name of the drug to check
        current_medications: String of current medications
        interactions_df: DataFrame with interaction data
    
    Returns:
        Dictionary with is_safe boolean, message, and warning
    """
    if not current_medications or current_medications.strip() == '':
        return {'is_safe': True, 'message': '', 'warning': ''}
    
    # Parse current medications
    current_meds = [m.strip().lower() for m in current_medications.split(',')]
    drug_lower = drug_name.lower()
    
    severe_interactions = []
    moderate_interactions = []
    
    # Check interactions database
    for med in current_meds:
        # Check both directions (drug1-drug2 and drug2-drug1)
        interaction = interactions_df[
            ((interactions_df['drug1'].str.lower() == drug_lower) & 
             (interactions_df['drug2'].str.lower() == med)) |
            ((interactions_df['drug1'].str.lower() == med) & 
             (interactions_df['drug2'].str.lower() == drug_lower))
        ]
        
        if not interaction.empty:
            severity = interaction.iloc[0]['severity'].lower()
            
            if severity == 'severe':
                severe_interactions.append(med)
            elif severity == 'moderate':
                moderate_interactions.append(med)
    
    # Return results
    if severe_interactions:
        return {
            'is_safe': False,
            'message': f'❌ Severe Interaction: {drug_name} interacts with {", ".join(severe_interactions)}',
            'warning': ''
        }
    
    if moderate_interactions:
        return {
            'is_safe': True,
            'message': '',
            'warning': f'⚠️ Moderate Interaction: Monitor for effects with {", ".join(moderate_interactions)}'
        }
    
    return {'is_safe': True, 'message': '', 'warning': ''}


def check_contraindications(drug_name, patient_data, medicines_df):
    """
    Check age, kidney, liver, and pregnancy contraindications
    
    Args:
        drug_name: Name of the drug
        patient_data: Dictionary with patient information
        medicines_df: DataFrame with medicines data
    
    Returns:
        Dictionary with is_safe boolean, message, and warning
    """
    # Get drug information
    drug_info = medicines_df[medicines_df['drug_name'] == drug_name]
    
    if drug_info.empty:
        return {'is_safe': True, 'message': '', 'warning': '⚠️ Drug information not in database'}
    
    drug_info = drug_info.iloc[0]
    age = int(patient_data['age'])
    
    # Check age contraindications
    age_min = drug_info.get('age_min', 0)
    age_max = drug_info.get('age_max', 120)
    
    if age < age_min or age > age_max:
        return {
            'is_safe': False,
            'message': f'❌ Age Contraindication: Not approved for age {age} (safe range: {age_min}-{age_max})',
            'warning': ''
        }
    
    # Check kidney function
    if patient_data.get('creatinine'):
        creatinine = float(patient_data['creatinine'])
        kidney_safe = drug_info.get('kidney_safe', 'YES')
        
        if creatinine > 1.5 and kidney_safe == 'NO':
            return {
                'is_safe': False,
                'message': f'❌ Kidney Contraindication: Elevated creatinine ({creatinine}) - drug not safe',
                'warning': ''
            }
    
    # Check liver function
    if patient_data.get('liver_enzyme'):
        liver_enzyme = float(patient_data['liver_enzyme'])
        liver_safe = drug_info.get('liver_safe', 'YES')
        
        if liver_enzyme > 60 and liver_safe == 'NO':
            return {
                'is_safe': False,
                'message': f'❌ Liver Contraindication: Elevated liver enzymes ({liver_enzyme}) - drug not safe',
                'warning': ''
            }
    
    # Check pregnancy
    is_pregnant = patient_data.get('is_pregnant', 'no')
    pregnancy_safe = drug_info.get('pregnancy_safe', 'YES')
    
    if is_pregnant == 'yes' and pregnancy_safe == 'NO':
        return {
            'is_safe': False,
            'message': f'❌ Pregnancy Contraindication: Not safe during pregnancy',
            'warning': ''
        }
    
    return {'is_safe': True, 'message': '', 'warning': ''}


def generate_explanation(safe_drugs, rejected_drugs, patient_data):
    """
    Generate human-readable explanation for recommendations
    
    Args:
        safe_drugs: List of recommended drugs
        rejected_drugs: List of rejected drugs
        patient_data: Dictionary with patient information
    
    Returns:
        Explanation text string
    """
    explanation = []
    
    # Summary
    explanation.append(f"🔍 <strong>Analysis Summary:</strong>")
    explanation.append(f"Patient: {patient_data['name']}, Age: {patient_data['age']}, Gender: {patient_data['gender']}")
    explanation.append(f"Symptoms: {patient_data['symptoms']}")
    explanation.append("")
    
    # Recommended drugs
    if safe_drugs:
        explanation.append(f"✅ <strong>{len(safe_drugs)} Safe Drug(s) Recommended:</strong>")
        for drug in safe_drugs[:3]:
            explanation.append(f"• <strong>{drug['drug']}</strong> (Confidence: {drug['confidence']}%)")
            explanation.append(f"  Category: {drug['category']}")
            if drug['warnings']:
                explanation.append(f"  Warnings: {'; '.join(drug['warnings'])}")
        explanation.append("")
    
    # Rejected drugs
    if rejected_drugs:
        explanation.append(f"❌ <strong>{len(rejected_drugs)} Drug(s) Rejected:</strong>")
        for drug in rejected_drugs:
            explanation.append(f"• {drug['drug']}: {drug['reason']}")
        explanation.append("")
    
    # Safety checks performed
    explanation.append("🛡️ <strong>Safety Checks Performed:</strong>")
    explanation.append("✓ Allergy verification")
    explanation.append("✓ Drug interaction detection")
    explanation.append("✓ Age contraindication checking")
    if patient_data.get('creatinine'):
        explanation.append("✓ Kidney function assessment")
    if patient_data.get('liver_enzyme'):
        explanation.append("✓ Liver function assessment")
    
    return "<br>".join(explanation)
