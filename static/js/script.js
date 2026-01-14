// ===================================
// Smart Drug Recommendation System
// Form Validation & UI Interactions
// ===================================

// Form Validation
function validateForm() {
    // Get form values
    const name = document.getElementById('patientName').value.trim();
    const age = parseInt(document.getElementById('age').value);
    const gender = document.getElementById('gender').value;
    const symptoms = document.getElementById('symptoms').value.trim();
    
    // Validate name
    if (name.length < 2) {
        showAlert('Please enter a valid patient name', 'danger');
        return false;
    }
    
    // Validate age
    if (age < 1 || age > 120 || isNaN(age)) {
        showAlert('Please enter a valid age (1-120)', 'danger');
        return false;
    }
    
    // Validate gender
    if (!gender) {
        showAlert('Please select gender', 'danger');
        return false;
    }
    
    // Validate symptoms
    if (symptoms.length < 3) {
        showAlert('Please enter at least one symptom', 'danger');
        return false;
    }
    
    // Show loading spinner
    showLoadingSpinner();
    
    return true;
}

// Show loading spinner
function showLoadingSpinner() {
    const spinner = document.getElementById('loadingSpinner');
    const form = document.getElementById('patientForm');
    
    if (spinner && form) {
        form.style.display = 'none';
        spinner.style.display = 'block';
    }
}

// Show alert message
function showAlert(message, type) {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="fas fa-exclamation-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of form container
    const formContainer = document.querySelector('.form-container');
    if (formContainer) {
        formContainer.insertBefore(alertDiv, formContainer.firstChild);
        
        // Scroll to alert
        alertDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// Symptom suggestions (autocomplete-like feature)
const commonSymptoms = [
    'fever', 'headache', 'cough', 'cold', 'body pain', 'nausea',
    'vomiting', 'diarrhea', 'sore throat', 'runny nose', 'fatigue',
    'dizziness', 'chest pain', 'shortness of breath', 'joint pain'
];

// Add tooltip for symptoms
document.addEventListener('DOMContentLoaded', function() {
    const symptomsField = document.getElementById('symptoms');
    
    if (symptomsField) {
        symptomsField.addEventListener('focus', function() {
            showTooltip(symptomsField, 'Common symptoms: ' + commonSymptoms.slice(0, 5).join(', ') + '...');
        });
    }
    
    // Add character counter for text areas
    const textAreas = document.querySelectorAll('textarea');
    textAreas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            const maxLength = 500;
            const currentLength = this.value.length;
            
            if (currentLength > maxLength) {
                this.value = this.value.substring(0, maxLength);
            }
        });
    });
});

// Show tooltip helper
function showTooltip(element, message) {
    // Check if Bootstrap tooltip is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltip = new bootstrap.Tooltip(element, {
            title: message,
            trigger: 'manual',
            placement: 'top'
        });
        tooltip.show();
        
        setTimeout(() => {
            tooltip.hide();
        }, 3000);
    }
}

// Real-time age validation
document.addEventListener('DOMContentLoaded', function() {
    const ageInput = document.getElementById('age');
    
    if (ageInput) {
        ageInput.addEventListener('input', function() {
            const age = parseInt(this.value);
            
            if (age < 0) {
                this.value = 0;
            } else if (age > 120) {
                this.value = 120;
            }
            
            // Visual feedback for pediatric/geriatric patients
            if (age > 0 && age < 18) {
                this.style.borderColor = '#FFA500';
            } else if (age >= 65) {
                this.style.borderColor = '#DC3545';
            } else {
                this.style.borderColor = '#00A651';
            }
        });
    }
});

// Pregnancy field auto-hide for males
document.addEventListener('DOMContentLoaded', function() {
    const genderSelect = document.getElementById('gender');
    const pregnancyField = document.getElementById('isPregnant');
    
    if (genderSelect && pregnancyField) {
        genderSelect.addEventListener('change', function() {
            const pregnancyContainer = pregnancyField.closest('.col-md-4');
            
            if (this.value === 'Male') {
                pregnancyContainer.style.display = 'none';
                pregnancyField.value = 'no';
            } else {
                pregnancyContainer.style.display = 'block';
            }
        });
    }
});

// Print functionality for results page
function printResults() {
    window.print();
}

// Copy results to clipboard
function copyResults() {
    const resultsText = document.querySelector('.result-container').innerText;
    
    navigator.clipboard.writeText(resultsText).then(() => {
        showAlert('Results copied to clipboard!', 'success');
    }).catch(() => {
        showAlert('Failed to copy results', 'danger');
    });
}

// Smooth scroll for navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add animation on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.addEventListener('DOMContentLoaded', function() {
    const animatedElements = document.querySelectorAll('.feature-card, .result-card');
    
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});
