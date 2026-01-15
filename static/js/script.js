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
/**
 * Drug Search and Autocomplete Functionality
 * Phase 11.2 & 11.3 Implementation
 */

document.addEventListener('DOMContentLoaded', function() {
    const searchBox = document.getElementById('drugSearchBox');
    const searchResults = document.getElementById('searchResults');
    const categoryFilter = document.getElementById('categoryFilter');
    const drugNameInput = document.getElementById('drug_name');
    const drugInfoCard = document.getElementById('drugInfoCard');
    const drugInfoContent = document.getElementById('drugInfoContent');
    
    let searchTimeout;
    
    // Search drugs as user types
    if (searchBox) {
        searchBox.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            
            const query = this.value.trim();
            const category = categoryFilter.value;
            
            if (query.length < 2) {
                searchResults.style.display = 'none';
                return;
            }
            
            // Debounce search
            searchTimeout = setTimeout(() => {
                searchDrugs(query, category);
            }, 300);
        });
        
        // Close search results when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchBox.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });
    }
    
    // Category filter change
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            const query = searchBox.value.trim();
            if (query.length >= 2) {
                searchDrugs(query, this.value);
            }
        });
    }
    
    /**
     * Search drugs via AJAX
     */
    function searchDrugs(query, category) {
        const params = new URLSearchParams({
            q: query,
            category: category
        });
        
        fetch(`/search-drugs?${params}`)
            .then(response => response.json())
            .then(data => {
                displaySearchResults(data);
            })
            .catch(error => {
                console.error('Search error:', error);
            });
    }
    
    /**
     * Display search results dropdown
     */
    function displaySearchResults(drugs) {
        searchResults.innerHTML = '';
        
        if (drugs.length === 0) {
            searchResults.innerHTML = `
                <div class="list-group-item text-muted">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    No drugs found
                </div>
            `;
            searchResults.style.display = 'block';
            return;
        }
        
        drugs.forEach(drug => {
            const item = document.createElement('a');
            item.href = '#';
            item.className = 'list-group-item list-group-item-action';
            item.innerHTML = `
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">${drug.drug_name}</h6>
                        <small class="text-muted">
                            ${drug.generic_name ? drug.generic_name + ' • ' : ''}
                            ${drug.category}
                            ${drug.dosage_forms ? ' • ' + drug.dosage_forms : ''}
                        </small>
                    </div>
                    <span class="badge bg-primary">₹${drug.price || 'N/A'}</span>
                </div>
            `;
            
            // Click to select drug
            item.addEventListener('click', function(e) {
                e.preventDefault();
                selectDrug(drug.drug_name);
                searchResults.style.display = 'none';
            });
            
            // Double-click to view info
            item.addEventListener('dblclick', function(e) {
                e.preventDefault();
                viewDrugInfo(drug.drug_name);
            });
            
            searchResults.appendChild(item);
        });
        
        // Add footer
        const footer = document.createElement('div');
        footer.className = 'list-group-item bg-light';
        footer.innerHTML = `
            <small class="text-muted">
                <i class="fas fa-info-circle me-1"></i>
                Click to select • Double-click for details
            </small>
        `;
        searchResults.appendChild(footer);
        
        searchResults.style.display = 'block';
    }
    
    /**
     * Select drug for validation
     */
    function selectDrug(drugName) {
        if (drugNameInput) {
            drugNameInput.value = drugName;
            searchBox.value = drugName;
            
            // Highlight the input briefly
            drugNameInput.classList.add('bg-success-subtle');
            setTimeout(() => {
                drugNameInput.classList.remove('bg-success-subtle');
            }, 1000);
        }
    }
    
    /**
     * View detailed drug information
     */
    function viewDrugInfo(drugName) {
        fetch(`/drug-info/${encodeURIComponent(drugName)}`)
            .then(response => response.json())
            .then(drug => {
                displayDrugInfo(drug);
            })
            .catch(error => {
                console.error('Error fetching drug info:', error);
            });
    }
    
    /**
     * Display detailed drug information
     */
    function displayDrugInfo(drug) {
        drugInfoContent.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h5 class="text-primary">${drug.drug_name}</h5>
                    ${drug.generic_name ? `<p class="text-muted mb-2"><strong>Generic:</strong> ${drug.generic_name}</p>` : ''}
                    ${drug.brand_names ? `<p class="mb-2"><strong>Brands:</strong> ${drug.brand_names}</p>` : ''}
                    <p class="mb-2">
                        <span class="badge bg-info">${drug.category}</span>
                        ${drug.prescription_required ? '<span class="badge bg-warning ms-2">℞ Required</span>' : ''}
                    </p>
                </div>
                <div class="col-md-6 text-end">
                    ${drug.price ? `<h4 class="text-success">₹${drug.price}</h4>` : ''}
                    ${drug.pregnancy_category ? `<span class="badge bg-secondary">Pregnancy: ${drug.pregnancy_category}</span>` : ''}
                </div>
            </div>
            
            <hr>
            
            <div class="row">
                <div class="col-md-12 mb-3">
                    <h6><i class="fas fa-heartbeat me-2"></i>Indication</h6>
                    <p>${drug.indication || 'Not specified'}</p>
                </div>
                
                <div class="col-md-6 mb-3">
                    <h6><i class="fas fa-pills me-2"></i>Dosage</h6>
                    <p>${drug.standard_dosage || 'Consult physician'}</p>
                    <small class="text-muted">Forms: ${drug.dosage_forms || 'N/A'}</small>
                </div>
                
                <div class="col-md-6 mb-3">
                    <h6><i class="fas fa-exclamation-triangle me-2"></i>Side Effects</h6>
                    <p class="small">${drug.side_effects || 'See package insert'}</p>
                </div>
            </div>
            
            <div class="text-end">
                <button class="btn btn-primary btn-sm" onclick="selectDrug('${drug.drug_name}')">
                    <i class="fas fa-check me-1"></i> Select This Drug
                </button>
                <button class="btn btn-secondary btn-sm" onclick="document.getElementById('drugInfoCard').style.display='none'">
                    <i class="fas fa-times me-1"></i> Close
                </button>
            </div>
        `;
        
        drugInfoCard.style.display = 'block';
        drugInfoCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    // Make selectDrug globally available
    window.selectDrug = selectDrug;
});
