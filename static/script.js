// Cover Letter Generation System JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    // Get form elements
    const form = document.getElementById('coverLetterForm');
    const generateBtn = document.getElementById('generateBtn');
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    const resultsSection = document.getElementById('resultsSection');
    
    // Load profiles on page load
    loadProfiles();
    
    // Form submission handler
    form.addEventListener('submit', handleFormSubmission);
    
    // Profile selection handler
    const profileSelect = document.getElementById('profileSelect');
    profileSelect.addEventListener('change', handleProfileSelection);
    
    // Company name input handler for real-time research
    const companyNameInput = document.getElementById('companyName');
    let companyResearchTimeout;
    
    companyNameInput.addEventListener('input', function() {
        clearTimeout(companyResearchTimeout);
        companyResearchTimeout = setTimeout(() => {
            if (this.value.length > 2) {
                previewCompanyInfo(this.value);
            }
        }, 1000);
    });
}

async function loadProfiles() {
    try {
        const response = await fetch('/api/profiles');
        const data = await response.json();
        
        const profileSelect = document.getElementById('profileSelect');
        
        if (data.success && data.profiles.length > 0) {
            profileSelect.innerHTML = '<option value="">Select a profile...</option>';
            
            data.profiles.forEach(profile => {
                const option = document.createElement('option');
                option.value = profile.id;
                option.textContent = profile.name;
                if (profile.is_default) {
                    option.selected = true;
                }
                profileSelect.appendChild(option);
            });
            
            // Load default profile info if available
            const defaultProfile = data.profiles.find(p => p.is_default);
            if (defaultProfile) {
                loadProfileInfo(defaultProfile.id);
            }
        } else {
            profileSelect.innerHTML = '<option value="">No profiles available</option>';
            showAlert('No profiles found. Please create a profile first.', 'warning');
        }
    } catch (error) {
        console.error('Error loading profiles:', error);
        showAlert('Failed to load profiles', 'danger');
    }
}

async function handleProfileSelection(event) {
    const profileId = event.target.value;
    if (profileId) {
        await loadProfileInfo(profileId);
    } else {
        document.getElementById('resumeInfo').innerHTML = '<p class="text-muted">Select a profile to view information</p>';
    }
}

async function loadProfileInfo(profileId) {
    try {
        const response = await fetch(`/api/profiles/${profileId}`);
        const data = await response.json();
        
        if (data.success && data.profile) {
            const resumeInfo = data.profile.RESUME_INFO;
            const resumeInfoDiv = document.getElementById('resumeInfo');
            
            resumeInfoDiv.innerHTML = `
                <p><strong>Name:</strong> ${resumeInfo.name}</p>
                <p><strong>Email:</strong> ${resumeInfo.email}</p>
                <p><strong>Education:</strong> ${resumeInfo.education.degree}</p>
                <p><strong>University:</strong> ${resumeInfo.education.university}</p>
                <p><strong>Skills:</strong> ${resumeInfo.core_skills.slice(0, 2).join(', ').substring(0, 100)}...</p>
            `;
        }
    } catch (error) {
        console.error('Error loading profile info:', error);
    }
}

async function handleFormSubmission(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const generateBtn = document.getElementById('generateBtn');
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    
    // Validate form
    if (!validateForm(formData)) {
        return;
    }
    
    // Update UI state
    updateProgressStep(2);
    generateBtn.disabled = true;
    loadingModal.show();
    
    try {
        // Submit form data
        const response = await fetch('/generate-cover-letter', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Hide loading modal
            loadingModal.hide();
            
            // Update progress
            updateProgressStep(3);
            
            // Display results
            displayResults(result);
            
            // Show success message
            showNotification('Cover letter generated successfully!', 'success');
            
        } else {
            throw new Error(result.detail || 'Failed to generate cover letter');
        }
        
    } catch (error) {
        console.error('Error generating cover letter:', error);
        loadingModal.hide();
        showNotification('Error generating cover letter: ' + error.message, 'error');
        updateProgressStep(1);
    } finally {
        generateBtn.disabled = false;
    }
}

function validateForm(formData) {
    const requiredFields = ['company_name', 'job_title', 'job_description'];
    const errors = [];
    
    for (const field of requiredFields) {
        const value = formData.get(field);
        if (!value || value.trim().length === 0) {
            errors.push(`${field.replace('_', ' ')} is required`);
        }
    }
    
    // Validate job description length
    const jobDescription = formData.get('job_description');
    if (jobDescription && jobDescription.length < 50) {
        errors.push('Job description should be at least 50 characters long');
    }
    
    if (errors.length > 0) {
        showNotification('Please fix the following errors:\\n' + errors.join('\\n'), 'error');
        return false;
    }
    
    return true;
}

function updateProgressStep(stepNumber) {
    // Remove active class from all steps
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active', 'completed');
    });
    
    // Add completed class to previous steps
    for (let i = 1; i < stepNumber; i++) {
        const step = document.getElementById(`step${i}`);
        if (step) {
            step.classList.add('completed');
        }
    }
    
    // Add active class to current step
    const currentStep = document.getElementById(`step${stepNumber}`);
    if (currentStep) {
        currentStep.classList.add('active');
    }
}

function displayResults(result) {
    const resultsSection = document.getElementById('resultsSection');
    const letterPreview = document.getElementById('letterPreview');
    const wordCount = document.getElementById('wordCount');
    const generatedTime = document.getElementById('generatedTime');
    const downloadBtn = document.getElementById('downloadBtn');
    
    // Format the cover letter content for display
    const formattedContent = formatLetterContent(result.content);
    letterPreview.innerHTML = formattedContent;
    
    // Update stats
    wordCount.textContent = result.word_count || 'N/A';
    generatedTime.textContent = new Date().toLocaleString();
    
    // Set up download button
    if (result.document_path) {
        const filename = result.document_path.split('/').pop();
        downloadBtn.onclick = () => downloadFile(filename);
    }
    
    // Show results section with animation
    resultsSection.style.display = 'block';
    resultsSection.classList.add('fade-in');
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function formatLetterContent(content) {
    if (!content) return '<p>No content available</p>';
    
    // Split content into paragraphs and format
    const paragraphs = content.split('\\n\\n').filter(p => p.trim());
    
    let formattedContent = '<h4>Generated Cover Letter</h4>';
    
    paragraphs.forEach(paragraph => {
        const trimmed = paragraph.trim();
        if (trimmed) {
            formattedContent += `<p>${trimmed}</p>`;
        }
    });
    
    return formattedContent;
}

async function downloadFile(filename) {
    try {
        const response = await fetch(`/download/${filename}`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showNotification('File downloaded successfully!', 'success');
        } else {
            throw new Error('Failed to download file');
        }
    } catch (error) {
        console.error('Download error:', error);
        showNotification('Error downloading file: ' + error.message, 'error');
    }
}

async function previewCompanyInfo(companyName) {
    try {
        const response = await fetch(`/api/company-info/${encodeURIComponent(companyName)}`);
        const result = await response.json();
        
        if (result.success && result.company_info) {
            // You could display company info preview here
            console.log('Company info:', result.company_info);
        }
    } catch (error) {
        console.error('Error fetching company info:', error);
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    notification.innerHTML = `
        <i class="fas fa-${getIconForType(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function getIconForType(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Form enhancement functions
function enhanceFormExperience() {
    // Add character counters
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        addCharacterCounter(textarea);
    });
    
    // Add input validation feedback
    const inputs = document.querySelectorAll('input[required], textarea[required]');
    inputs.forEach(input => {
        addValidationFeedback(input);
    });
}

function addCharacterCounter(textarea) {
    const counter = document.createElement('div');
    counter.className = 'form-text text-end';
    counter.style.fontSize = '0.8rem';
    
    const updateCounter = () => {
        const length = textarea.value.length;
        counter.textContent = `${length} characters`;
        
        if (length < 50) {
            counter.className = 'form-text text-end text-warning';
        } else {
            counter.className = 'form-text text-end text-muted';
        }
    };
    
    textarea.addEventListener('input', updateCounter);
    textarea.parentNode.appendChild(counter);
    updateCounter();
}

function addValidationFeedback(input) {
    input.addEventListener('blur', function() {
        if (this.value.trim() === '') {
            this.classList.add('is-invalid');
        } else {
            this.classList.remove('is-invalid');
            this.classList.add('is-valid');
        }
    });
    
    input.addEventListener('input', function() {
        if (this.classList.contains('is-invalid') && this.value.trim() !== '') {
            this.classList.remove('is-invalid');
            this.classList.add('is-valid');
        }
    });
}

// Initialize enhanced features when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    enhanceFormExperience();
});

