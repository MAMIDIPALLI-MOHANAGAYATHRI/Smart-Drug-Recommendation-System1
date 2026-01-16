/**
 * NLP Symptom Analysis
 * Phase 12.5: Natural Language Processing for symptom extraction
 */

document.addEventListener('DOMContentLoaded', function() {
    const symptomsTextarea = document.getElementById('symptoms');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const nlpAnalysis = document.getElementById('nlpAnalysis');
    const nlpResults = document.getElementById('nlpResults');
    
    if (analyzeBtn && symptomsTextarea) {
        analyzeBtn.addEventListener('click', function() {
            const symptoms = symptomsTextarea.value.trim();
            
            if (symptoms.length < 3) {
                alert('Please enter symptom description first');
                return;
            }
            
            // Show loading
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Analyzing...';
            
            // Call NLP analysis API
            fetch('/analyze-symptoms', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    symptoms: symptoms
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayNLPResults(data);
                } else {
                    alert('Analysis failed: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Analysis error. Please try again.');
            })
            .finally(() => {
                // Reset button
                analyzeBtn.disabled = false;
                analyzeBtn.innerHTML = '<i class="fas fa-robot me-1"></i> Analyze with AI';
            });
        });
    }
    
    /**
     * Display NLP analysis results
     */
    function displayNLPResults(data) {
        const extraction = data.extraction;
        const summary = data.summary_html;
        const suggestions = data.suggestions;
        
        let html = `
            <div class="row">
                <div class="col-md-8">
                    ${summary}
                </div>
                <div class="col-md-4">
                    <div class="bg-light p-3 rounded">
                        <h6 class="text-muted mb-2">
                            <i class="fas fa-lightbulb me-1"></i>
                            Original Text:
                        </h6>
                        <p class="small mb-0">"${extraction.cleaned_text}"</p>
                    </div>
                </div>
            </div>
        `;
        
        // Show suggestions if any
        if (suggestions && suggestions.length > 0) {
            html += `
                <div class="alert alert-info mt-3 mb-0">
                    <h6>
                        <i class="fas fa-info-circle me-2"></i>
                        💡 Suggestions for Better Diagnosis:
                    </h6>
                    <ul class="mb-0 small">
                        ${suggestions.map(s => `<li>${s}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        // Show formatted symptoms
        if (extraction.symptom_text) {
            html += `
                <div class="mt-3">
                    <button type="button" 
                            class="btn btn-sm btn-success"
                            onclick="useFormattedSymptoms('${extraction.symptom_text.replace(/'/g, "\\'")}')">
                        <i class="fas fa-check me-1"></i>
                        Use Formatted Symptoms
                    </button>
                    <span class="text-muted ms-2 small">
                        Will update symptom field with: "${extraction.symptom_text}"
                    </span>
                </div>
            `;
        }
        
        nlpResults.innerHTML = html;
        nlpAnalysis.style.display = 'block';
        
        // Scroll to results
        nlpAnalysis.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    /**
     * Use formatted symptoms
     */
    window.useFormattedSymptoms = function(formattedText) {
        if (symptomsTextarea) {
            symptomsTextarea.value = formattedText;
            symptomsTextarea.classList.add('bg-success-subtle');
            
            // Show success message
            const successMsg = document.createElement('div');
            successMsg.className = 'alert alert-success alert-dismissible fade show mt-2';
            successMsg.innerHTML = `
                <i class="fas fa-check-circle me-2"></i>
                Symptoms updated with AI-extracted terms
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            symptomsTextarea.parentElement.appendChild(successMsg);
            
            setTimeout(() => {
                symptomsTextarea.classList.remove('bg-success-subtle');
            }, 2000);
        }
    };
    
    /**
     * Real-time symptom suggestions (optional)
     */
    let typingTimer;
    if (symptomsTextarea) {
        symptomsTextarea.addEventListener('input', function() {
            clearTimeout(typingTimer);
            
            // Show analyze button hint after typing
            if (this.value.length > 20) {
                analyzeBtn.classList.add('btn-primary');
                analyzeBtn.classList.remove('btn-outline-primary');
            } else {
                analyzeBtn.classList.remove('btn-primary');
                analyzeBtn.classList.add('btn-outline-primary');
            }
        });
    }
});
