"""
Natural Language Processing Utilities
Phase 12.5: Extract medical symptoms from natural language text
"""

import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
import spacy

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)

# Load Spacy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    print("⚠ Spacy model not found. Install with: python -m spacy download en_core_web_sm")
    nlp = None


# Medical symptom dictionary (expanded)
SYMPTOM_DICTIONARY = {
    # Pain-related
    'pain': ['pain', 'ache', 'aching', 'sore', 'tender', 'hurt', 'hurting', 'painful', 'discomfort'],
    'headache': ['headache', 'head pain', 'migraine', 'head ache'],
    'chest_pain': ['chest pain', 'chest discomfort', 'angina'],
    'abdominal_pain': ['stomach pain', 'belly pain', 'abdominal pain', 'tummy ache'],
    'back_pain': ['back pain', 'backache', 'lower back pain'],
    'joint_pain': ['joint pain', 'arthralgia', 'joints hurt'],
    
    # Fever and temperature
    'fever': ['fever', 'febrile', 'high temperature', 'pyrexia', 'hot', 'burning up'],
    'chills': ['chills', 'shivering', 'rigors', 'shaking'],
    
    # Respiratory
    'cough': ['cough', 'coughing', 'hacking', 'productive cough', 'dry cough'],
    'shortness_of_breath': ['shortness of breath', 'breathless', 'dyspnea', 'difficulty breathing', 'cant breathe'],
    'wheezing': ['wheezing', 'wheeze', 'whistling breath'],
    'sore_throat': ['sore throat', 'throat pain', 'pharyngitis', 'scratchy throat'],
    'runny_nose': ['runny nose', 'rhinorrhea', 'nasal discharge', 'stuffy nose', 'congestion'],
    'sneezing': ['sneezing', 'sneeze', 'achoo'],
    
    # Gastrointestinal
    'nausea': ['nausea', 'nauseous', 'queasy', 'sick to stomach', 'feel sick'],
    'vomiting': ['vomiting', 'vomit', 'throwing up', 'emesis', 'puking'],
    'diarrhea': ['diarrhea', 'loose stools', 'watery stools', 'frequent stools', 'loose motions'],
    'constipation': ['constipation', 'hard stools', 'difficulty passing stools', 'cant poop'],
    'heartburn': ['heartburn', 'acid reflux', 'gerd', 'indigestion', 'burning chest'],
    'bloating': ['bloating', 'bloated', 'gas', 'flatulence', 'distension'],
    
    # Neurological
    'dizziness': ['dizzy', 'dizziness', 'lightheaded', 'vertigo', 'spinning sensation'],
    'confusion': ['confusion', 'confused', 'disoriented', 'mental fog'],
    'seizure': ['seizure', 'convulsion', 'fit', 'epilepsy'],
    'numbness': ['numbness', 'numb', 'tingling', 'pins and needles'],
    
    # General symptoms
    'fatigue': ['tired', 'fatigue', 'exhausted', 'weak', 'weakness', 'lethargic', 'no energy'],
    'malaise': ['malaise', 'unwell', 'feeling bad', 'not feeling good'],
    'weight_loss': ['weight loss', 'losing weight', 'lost weight'],
    'weight_gain': ['weight gain', 'gaining weight', 'gained weight'],
    'loss_of_appetite': ['loss of appetite', 'not hungry', 'no appetite', 'dont want to eat'],
    
    # Skin
    'rash': ['rash', 'skin rash', 'eruption', 'hives', 'urticaria'],
    'itching': ['itching', 'itchy', 'pruritus', 'scratching'],
    'swelling': ['swelling', 'swollen', 'edema', 'puffiness', 'puffy'],
    
    # Cardiovascular
    'palpitations': ['palpitations', 'heart racing', 'rapid heartbeat', 'pounding heart'],
    'hypertension': ['high blood pressure', 'hypertension', 'elevated bp'],
    'hypotension': ['low blood pressure', 'hypotension', 'low bp'],
    
    # Urinary
    'frequent_urination': ['frequent urination', 'urinating often', 'polyuria', 'peeing a lot'],
    'burning_urination': ['burning urination', 'painful urination', 'dysuria', 'burns when peeing'],
    'blood_in_urine': ['blood in urine', 'hematuria', 'red urine'],
    
    # Ear/Nose/Throat
    'ear_pain': ['ear pain', 'earache', 'otalgia'],
    'hearing_loss': ['hearing loss', 'cant hear', 'deaf', 'hard of hearing'],
    'tinnitus': ['ringing in ears', 'tinnitus', 'ear ringing'],
    'hoarseness': ['hoarse voice', 'hoarseness', 'voice change'],
    
    # Eye symptoms
    'blurred_vision': ['blurred vision', 'blurry vision', 'cant see clearly', 'vision problems'],
    'eye_pain': ['eye pain', 'eye ache', 'sore eyes'],
    'red_eyes': ['red eyes', 'bloodshot eyes', 'pink eye'],
    
    # Sleep-related
    'insomnia': ['insomnia', 'cant sleep', 'difficulty sleeping', 'sleeplessness'],
    'excessive_sleep': ['sleeping too much', 'hypersomnia', 'always tired'],
    
    # Psychological
    'anxiety': ['anxiety', 'anxious', 'worried', 'panic', 'nervous'],
    'depression': ['depression', 'depressed', 'sad', 'low mood', 'hopeless'],
}

# Duration patterns
DURATION_PATTERNS = {
    'hours': r'(\d+)\s*(?:hour|hr)s?',
    'days': r'(\d+)\s*days?',
    'weeks': r'(\d+)\s*(?:week|wk)s?',
    'months': r'(\d+)\s*(?:month|mo)s?',
    'years': r'(\d+)\s*(?:year|yr)s?',
    'since': r'since\s+(\d+)\s+(\w+)',
    'for': r'for\s+(\d+)\s+(\w+)',
}

# Severity keywords
SEVERITY_KEYWORDS = {
    'mild': ['mild', 'slight', 'minor', 'little', 'bit of'],
    'moderate': ['moderate', 'medium', 'considerable'],
    'severe': ['severe', 'intense', 'extreme', 'unbearable', 'terrible', 'awful', 'very bad', 'excruciating'],
}

# Temporal keywords
TEMPORAL_KEYWORDS = {
    'acute': ['sudden', 'acute', 'abrupt', 'just started', 'recently', 'new'],
    'chronic': ['chronic', 'long-term', 'ongoing', 'persistent', 'always', 'for months', 'for years'],
    'intermittent': ['intermittent', 'comes and goes', 'on and off', 'occasional', 'sometimes'],
    'constant': ['constant', 'continuous', 'persistent', 'all the time', 'always present'],
}


def extract_symptoms_nlp(text):
    """
    Extract medical symptoms from natural language using NLP
    
    Args:
        text: Natural language description of symptoms
    
    Returns:
        Dictionary with extracted information
    """
    if not text or not text.strip():
        return {
            'symptoms': [],
            'symptom_text': '',
            'duration': None,
            'severity': 'moderate',
            'temporal_pattern': None,
            'associated_symptoms': [],
            'cleaned_text': '',
            'confidence': 0.0
        }
    
    text_lower = text.lower().strip()
    
    # Extract symptoms
    found_symptoms = []
    symptom_matches = []
    
    for symptom_name, keywords in SYMPTOM_DICTIONARY.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_symptoms.append(symptom_name)
                symptom_matches.append({
                    'symptom': symptom_name,
                    'matched_keyword': keyword,
                    'display_name': symptom_name.replace('_', ' ').title()
                })
                break  # Found match, move to next symptom
    
    # Remove duplicates
    found_symptoms = list(set(found_symptoms))
    
    # Extract duration
    duration = extract_duration(text_lower)
    
    # Extract severity
    severity = extract_severity(text_lower)
    
    # Extract temporal pattern
    temporal_pattern = extract_temporal_pattern(text_lower)
    
    # Use Spacy for entity recognition (if available)
    entities = []
    if nlp:
        try:
            doc = nlp(text)
            entities = [(ent.text, ent.label_) for ent in doc.ents]
        except:
            pass
    
    # Generate symptom text
    symptom_text = ', '.join([s.replace('_', ' ') for s in found_symptoms]) if found_symptoms else text
    
    # Calculate confidence score
    confidence = calculate_confidence(text_lower, found_symptoms, duration, severity)
    
    # Clean text for display
    cleaned_text = clean_text_for_display(text)
    
    return {
        'symptoms': found_symptoms,
        'symptom_matches': symptom_matches,
        'symptom_text': symptom_text,
        'duration': duration,
        'severity': severity,
        'temporal_pattern': temporal_pattern,
        'entities': entities,
        'cleaned_text': cleaned_text,
        'confidence': confidence,
        'raw_text': text
    }


def extract_duration(text):
    """Extract duration information from text"""
    for duration_type, pattern in DURATION_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if duration_type in ['since', 'for']:
                return f"{match.group(1)} {match.group(2)}"
            else:
                return f"{match.group(1)} {duration_type}"
    return None


def extract_severity(text):
    """Extract severity from text"""
    for severity_level, keywords in SEVERITY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return severity_level
    return 'moderate'  # Default


def extract_temporal_pattern(text):
    """Extract temporal pattern"""
    for pattern_type, keywords in TEMPORAL_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return pattern_type
    return None


def calculate_confidence(text, symptoms, duration, severity):
    """Calculate confidence score for extraction"""
    score = 0.0
    
    # Base score for finding symptoms
    if symptoms:
        score += 0.5
    
    # Additional points for specific details
    if duration:
        score += 0.2
    
    if severity != 'moderate':  # Non-default severity mentioned
        score += 0.1
    
    # Points for medical terms found
    medical_terms = ['patient', 'complaining', 'presenting', 'history', 'reports']
    if any(term in text for term in medical_terms):
        score += 0.1
    
    # Points for proper grammar/structure
    if len(text.split()) > 5:
        score += 0.1
    
    return min(score, 1.0)  # Cap at 1.0


def clean_text_for_display(text):
    """Clean text for better display"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Capitalize first letter
    if text:
        text = text[0].upper() + text[1:]
    
    return text


def generate_symptom_summary(extraction_result):
    """
    Generate a human-readable summary of extracted symptoms
    
    Args:
        extraction_result: Result from extract_symptoms_nlp()
    
    Returns:
        HTML formatted summary string
    """
    if not extraction_result['symptoms']:
        return "<p class='text-muted'>No specific symptoms identified.</p>"
    
    html = []
    
    # Main symptoms
    html.append("<strong>🔍 Identified Symptoms:</strong>")
    html.append("<ul class='mb-2'>")
    for match in extraction_result.get('symptom_matches', []):
        html.append(f"<li>{match['display_name']}</li>")
    html.append("</ul>")
    
    # Duration
    if extraction_result['duration']:
        html.append(f"<strong>⏱️ Duration:</strong> {extraction_result['duration']}<br>")
    
    # Severity
    if extraction_result['severity']:
        severity_icon = {
            'mild': '🟢',
            'moderate': '🟡',
            'severe': '🔴'
        }
        icon = severity_icon.get(extraction_result['severity'], '⚪')
        html.append(f"<strong>📊 Severity:</strong> {icon} {extraction_result['severity'].title()}<br>")
    
    # Temporal pattern
    if extraction_result['temporal_pattern']:
        html.append(f"<strong>📅 Pattern:</strong> {extraction_result['temporal_pattern'].title()}<br>")
    
    # Confidence
    confidence_pct = int(extraction_result['confidence'] * 100)
    confidence_color = 'success' if confidence_pct >= 70 else 'warning' if confidence_pct >= 40 else 'danger'
    html.append(f"<div class='mt-2'><span class='badge bg-{confidence_color}'>Extraction Confidence: {confidence_pct}%</span></div>")
    
    return "".join(html)


def suggest_missing_information(extraction_result):
    """
    Suggest what information is missing for better diagnosis
    
    Args:
        extraction_result: Result from extract_symptoms_nlp()
    
    Returns:
        List of suggestions
    """
    suggestions = []
    
    if not extraction_result['duration']:
        suggestions.append("Consider adding how long the symptoms have been present")
    
    if not extraction_result['severity']:
        suggestions.append("Specify the severity of symptoms (mild/moderate/severe)")
    
    if not extraction_result['temporal_pattern']:
        suggestions.append("Mention if symptoms are constant or intermittent")
    
    if len(extraction_result['symptoms']) < 2:
        suggestions.append("Include any associated symptoms")
    
    return suggestions
