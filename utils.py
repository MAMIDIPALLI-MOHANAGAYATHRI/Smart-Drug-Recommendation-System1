"""
Smart Drug Recommendation System
Utility Functions for Data Processing and Safety Checks (Database Version)
"""

import pandas as pd
import numpy as np
import joblib
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from models import Drug, DrugInteraction, DrugFoodInteraction


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
        symptoms_text = patient_data.get('symptoms', '').lower().strip()
        symptoms_text = re.sub(r'[^a-zA-Z,\s]', '', symptoms_text)
        
        # Add medical history if available
        past_history = patient_data.get('past_history', '') or patient_data.get('medical_history', '')
        if past_history:
            history_text = past_history.lower().strip()
            symptoms_text += ' ' + re.sub(r'[^a-zA-Z,\s]', '', history_text)
        
        # Transform using vectorizer
        if vectorizer:
            text_features = vectorizer.transform([symptoms_text]).toarray()[0]
        else:
            # Fallback: simple feature extraction
            text_features = np.zeros(100)
        
        # Add numerical features
        age = float(patient_data.get('age', 0))
        gender_encoded = 1 if patient_data.get('gender') == 'Male' else 0
        
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
    
    # Get drug information from database
    drug = Drug.query.filter(Drug.drug_name.ilike(drug_name)).first()
    
    # Check for exact match or substring
    for allergy in allergies_list:
        if allergy in drug_lower or drug_lower in allergy:
            return {
                'is_safe': False,
                'message': f'❌ Allergy Alert: Patient allergic to {allergy}'
            }
        
        # Check drug class if available
        if drug and drug.drug_class:
            if allergy in drug.drug_class.lower():
                return {
                    'is_safe': False,
                    'message': f'❌ Allergy Alert: Patient allergic to {allergy} (drug class match)'
                }
    
    return {'is_safe': True, 'message': ''}


def check_drug_interaction_db(drug_name, current_medications):
    """
    Check for drug-drug interactions using database
    
    Args:
        drug_name: Name of the drug to check
        current_medications: String of current medications
    
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
        interactions = DrugInteraction.query.filter(
            ((DrugInteraction.drug1.ilike(drug_name)) & (DrugInteraction.drug2.ilike(med))) |
            ((DrugInteraction.drug1.ilike(med)) & (DrugInteraction.drug2.ilike(drug_name)))
        ).all()
        
        for interaction in interactions:
            severity = interaction.severity.lower()
            
            if severity == 'severe':
                severe_interactions.append({
                    'drug': med,
                    'description': interaction.description,
                    'management': interaction.management
                })
            elif severity == 'moderate':
                moderate_interactions.append({
                    'drug': med,
                    'description': interaction.description,
                    'management': interaction.management
                })
    
    # Return results
    if severe_interactions:
        drugs_list = ', '.join([i['drug'] for i in severe_interactions])
        return {
            'is_safe': False,
            'message': f'❌ Severe Interaction: {drug_name} interacts with {drugs_list}',
            'warning': '',
            'details': severe_interactions
        }
    
    if moderate_interactions:
        drugs_list = ', '.join([i['drug'] for i in moderate_interactions])
        return {
            'is_safe': True,
            'message': '',
            'warning': f'⚠️ Moderate Interaction: Monitor for effects with {drugs_list}',
            'details': moderate_interactions
        }
    
    return {'is_safe': True, 'message': '', 'warning': ''}


def check_contraindications_db(drug_obj, patient_data):
    """
    Check contraindications using Drug object from database
    
    Args:
        drug_obj: Drug model object from database
        patient_data: Dictionary with patient information
    
    Returns:
        Dictionary with is_safe boolean, message, and warning
    """
    try:
        age = int(patient_data.get('age', 0))
        
        # Check age contraindications
        if age < drug_obj.age_min or age > drug_obj.age_max:
            return {
                'is_safe': False,
                'message': f'❌ Age Contraindication: Not approved for age {age} (safe range: {drug_obj.age_min}-{drug_obj.age_max})',
                'warning': ''
            }
        
        # Check kidney function
        creatinine = patient_data.get('creatinine')
        if creatinine:
            creatinine = float(creatinine)
            if creatinine > 1.5 and drug_obj.kidney_safe == 'NO':
                return {
                    'is_safe': False,
                    'message': f'❌ Kidney Contraindication: Elevated creatinine ({creatinine}) - drug not safe for impaired kidney function',
                    'warning': ''
                }
            elif creatinine > 1.5 and drug_obj.kidney_safe == 'CAUTION':
                return {
                    'is_safe': True,
                    'message': '',
                    'warning': f'⚠️ Kidney Caution: Use with caution - creatinine elevated ({creatinine})'
                }
        
        # Check liver function
        liver_enzyme = patient_data.get('liver_enzyme')
        if liver_enzyme:
            liver_enzyme = float(liver_enzyme)
            if liver_enzyme > 60 and drug_obj.liver_safe == 'NO':
                return {
                    'is_safe': False,
                    'message': f'❌ Liver Contraindication: Elevated liver enzymes ({liver_enzyme}) - drug not safe for impaired liver function',
                    'warning': ''
                }
            elif liver_enzyme > 60 and drug_obj.liver_safe == 'CAUTION':
                return {
                    'is_safe': True,
                    'message': '',
                    'warning': f'⚠️ Liver Caution: Use with caution - liver enzymes elevated ({liver_enzyme})'
                }
        
        # Check pregnancy
        is_pregnant = patient_data.get('is_pregnant', 'no')
        if is_pregnant == 'yes':
            if drug_obj.pregnancy_safe == 'NO' or drug_obj.pregnancy_category in ['D', 'X']:
                return {
                    'is_safe': False,
                    'message': f'❌ Pregnancy Contraindication: Not safe during pregnancy (Category {drug_obj.pregnancy_category or "Unknown"})',
                    'warning': ''
                }
            elif drug_obj.pregnancy_category == 'C':
                return {
                    'is_safe': True,
                    'message': '',
                    'warning': f'⚠️ Pregnancy Caution: Use only if benefit outweighs risk (Category C)'
                }
        
        return {'is_safe': True, 'message': '', 'warning': ''}
    
    except Exception as e:
        print(f"Error checking contraindications: {str(e)}")
        return {'is_safe': True, 'message': '', 'warning': '⚠️ Unable to verify all contraindications'}


def check_drug_food_interaction_db(drug_name):
    """
    Check drug-food interactions from database (Phase 15.5)
    
    Args:
        drug_name: Name of the drug
    
    Returns:
        Dictionary with interaction information
    """
    try:
        # Query drug-food interactions
        interactions = DrugFoodInteraction.query.filter(
            DrugFoodInteraction.drug_name.ilike(drug_name)
        ).all()
        
        if not interactions:
            return {
                'has_interactions': False,
                'message': '',
                'interactions': []
            }
        
        # Categorize by severity
        severe = []
        moderate = []
        minor = []
        
        for interaction in interactions:
            interaction_data = {
                'food': interaction.food_item,
                'type': interaction.interaction_type,
                'description': interaction.description,
                'recommendation': interaction.recommendation
            }
            
            if interaction.severity == 'severe':
                severe.append(interaction_data)
            elif interaction.severity == 'moderate':
                moderate.append(interaction_data)
            else:
                minor.append(interaction_data)
        
        # Generate message
        messages = []
        if severe:
            food_list = ', '.join([i['food'] for i in severe])
            messages.append(f"❌ AVOID: {food_list}")
        
        if moderate:
            food_list = ', '.join([i['food'] for i in moderate])
            messages.append(f"⚠️ CAUTION: {food_list}")
        
        return {
            'has_interactions': True,
            'message': ' | '.join(messages) if messages else '',
            'interactions': severe + moderate + minor,
            'severe': severe,
            'moderate': moderate,
            'minor': minor
        }
    
    except Exception as e:
        print(f"Error checking drug-food interactions: {str(e)}")
        return {
            'has_interactions': False,
            'message': '',
            'interactions': []
        }


def generate_explanation(safe_drugs, rejected_drugs, patient_data):
    """
    Generate human-readable explanation for recommendations
    
    Args:
        safe_drugs: List of recommended drugs
        rejected_drugs: List of rejected drugs
        patient_data: Dictionary with patient information
    
    Returns:
        Explanation text string (HTML formatted)
    """
    explanation = []
    
    # Summary
    explanation.append(f"🔍 <strong>Analysis Summary:</strong>")
    explanation.append(f"Patient: {patient_data.get('name', 'Unknown')}, Age: {patient_data.get('age', 'N/A')}, Gender: {patient_data.get('gender', 'N/A')}")
    explanation.append(f"Symptoms: {patient_data.get('symptoms', 'Not specified')}")
    explanation.append("")
    
    # Recommended drugs
    if safe_drugs:
        explanation.append(f"✅ <strong>{len(safe_drugs)} Safe Drug(s) Recommended:</strong>")
        for drug in safe_drugs[:3]:
            explanation.append(f"• <strong>{drug['drug']}</strong> (Confidence: {drug['confidence']}%)")
            explanation.append(f"  Category: {drug['category']}")
            if drug.get('warnings'):
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
    explanation.append("✓ Drug-drug interaction detection")
    explanation.append("✓ Age contraindication checking")
    explanation.append("✓ Drug-food interaction checking")
    
    if patient_data.get('creatinine'):
        explanation.append("✓ Kidney function assessment")
    if patient_data.get('liver_enzyme'):
        explanation.append("✓ Liver function assessment")
    if patient_data.get('is_pregnant') == 'yes':
        explanation.append("✓ Pregnancy safety verification")
    
    return "<br>".join(explanation)


def extract_symptoms_nlp(text):
    """
    Extract medical symptoms from natural language text using NLP (Phase 12.5)
    Simple keyword-based extraction for now
    
    Args:
        text: Natural language text describing symptoms
    
    Returns:
        Dictionary with extracted symptoms and metadata
    """
    # Common medical symptom keywords
    symptom_keywords = {
        'pain': ['pain', 'ache', 'aching', 'sore', 'tender', 'hurt'],
        'fever': ['fever', 'temperature', 'hot', 'burning'],
        'cough': ['cough', 'coughing', 'hacking'],
        'headache': ['headache', 'head pain', 'migraine'],
        'nausea': ['nausea', 'nauseous', 'sick', 'queasy'],
        'vomiting': ['vomit', 'vomiting', 'throwing up'],
        'diarrhea': ['diarrhea', 'loose stools', 'watery stools'],
        'fatigue': ['tired', 'fatigue', 'exhausted', 'weak', 'weakness'],
        'dizziness': ['dizzy', 'dizziness', 'lightheaded', 'vertigo'],
        'rash': ['rash', 'skin irritation', 'itching', 'itchy'],
        'congestion': ['congested', 'stuffy', 'blocked nose', 'runny nose'],
        'sore_throat': ['sore throat', 'throat pain', 'scratchy throat']
    }
    
    # Duration keywords
    duration_keywords = {
        'acute': ['sudden', 'acute', 'recent', 'just started'],
        'chronic': ['chronic', 'long-term', 'ongoing', 'persistent'],
        'days': r'(\d+)\s*days?',
        'weeks': r'(\d+)\s*weeks?',
        'months': r'(\d+)\s*months?'
    }
    
    # Severity keywords
    severity_keywords = {
        'mild': ['mild', 'slight', 'minor'],
        'moderate': ['moderate'],
        'severe': ['severe', 'intense', 'extreme', 'unbearable']
    }
    
    text_lower = text.lower()
    
    # Extract symptoms
    found_symptoms = []
    for symptom, keywords in symptom_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_symptoms.append(symptom)
                break
    
    # Extract duration
    duration = None
    for dur_type, pattern in duration_keywords.items():
        if isinstance(pattern, str):
            if pattern in text_lower:
                duration = dur_type
                break
        else:
            import re
            match = re.search(pattern, text_lower)
            if match:
                duration = f"{match.group(1)} {dur_type}"
                break
    
    # Extract severity
    severity = 'moderate'  # Default
    for sev, keywords in severity_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                severity = sev
                break
    
    return {
        'symptoms': found_symptoms,
        'symptom_text': ', '.join(found_symptoms) if found_symptoms else text,
        'duration': duration,
        'severity': severity,
        'raw_text': text
    }


def format_drug_info_for_display(drug_obj):
    """
    Format drug object for display in templates
    
    Args:
        drug_obj: Drug model object
    
    Returns:
        Dictionary with formatted drug information
    """
    return {
        'name': drug_obj.drug_name,
        'generic_name': drug_obj.generic_name or 'N/A',
        'category': drug_obj.category,
        'indication': drug_obj.indication or 'Not specified',
        'side_effects': drug_obj.side_effects or 'See package insert',
        'dosage': drug_obj.standard_dosage or 'Consult physician',
        'price': f"₹{drug_obj.price:.2f}" if drug_obj.price else 'Contact pharmacy',
        'pregnancy_category': drug_obj.pregnancy_category or 'Unknown'
    }
