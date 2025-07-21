// Profile Manager JavaScript
class ProfileManager {
    constructor() {
        this.currentProfiles = [];
        this.selectedProfile = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadProfiles();
    }

    bindEvents() {
        // Form submission
        document.getElementById('profileForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveProfile();
        });

        // Add skill button
        document.getElementById('addSkillBtn').addEventListener('click', () => {
            this.addSkillField();
        });

        // Add experience button
        document.getElementById('addExperienceBtn').addEventListener('click', () => {
            this.addExperienceField();
        });

        // Add project button
        document.getElementById('addProjectBtn').addEventListener('click', () => {
            this.addProjectField();
        });

        // Delete confirmation
        document.getElementById('confirmDeleteBtn').addEventListener('click', () => {
            this.deleteProfile();
        });

        // Tab switching
        document.getElementById('list-tab').addEventListener('click', () => {
            this.loadProfiles();
        });
    }

    addSkillField() {
        const container = document.getElementById('skillsContainer');
        const skillCount = container.children.length + 1;
        
        const skillDiv = document.createElement('div');
        skillDiv.className = 'mb-3';
        skillDiv.innerHTML = `
            <label class="form-label">Skill Category ${skillCount}</label>
            <div class="input-group">
                <input type="text" class="form-control skill-input" placeholder="e.g., AI Systems & Tools: GraphRAG, AI Agents, Docker">
                <button type="button" class="btn btn-outline-danger" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        container.appendChild(skillDiv);
    }

    addExperienceField() {
        const container = document.getElementById('experienceContainer');
        const expCount = container.children.length + 1;
        
        const expDiv = document.createElement('div');
        expDiv.className = 'experience-entry mb-4 p-3 border rounded';
        expDiv.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h6 class="mb-0">Experience ${expCount}</h6>
                <button type="button" class="btn btn-outline-danger btn-sm" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label class="form-label">Job Title</label>
                    <input type="text" class="form-control exp-title" placeholder="e.g., Algorithm Engineer">
                </div>
                <div class="col-md-6 mb-3">
                    <label class="form-label">Company</label>
                    <input type="text" class="form-control exp-company" placeholder="e.g., ITLogica, Nanjing">
                </div>
                <div class="col-md-6 mb-3">
                    <label class="form-label">Period</label>
                    <input type="text" class="form-control exp-period" placeholder="e.g., Jun 2025 – Aug 2025">
                </div>
                <div class="col-12 mb-3">
                    <label class="form-label">Description</label>
                    <textarea class="form-control exp-description" rows="3" placeholder="Describe your key achievements and responsibilities"></textarea>
                </div>
            </div>
        `;
        container.appendChild(expDiv);
    }

    addProjectField() {
        const container = document.getElementById('projectsContainer');
        const projectCount = container.children.length + 1;
        
        const projectDiv = document.createElement('div');
        projectDiv.className = 'mb-3';
        projectDiv.innerHTML = `
            <label class="form-label">Project ${projectCount}</label>
            <div class="input-group">
                <textarea class="form-control project-input" rows="2" placeholder="Brief project description with key achievements"></textarea>
                <button type="button" class="btn btn-outline-danger" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        container.appendChild(projectDiv);
    }

    async loadProfiles() {
        try {
            const response = await fetch('/api/profiles');
            const data = await response.json();
            
            if (data.success) {
                this.currentProfiles = data.profiles;
                this.renderProfiles();
            } else {
                this.showAlert('Error loading profiles: ' + data.error, 'danger');
            }
        } catch (error) {
            console.error('Error loading profiles:', error);
            this.showAlert('Failed to load profiles', 'danger');
        }
    }

    renderProfiles() {
        const container = document.getElementById('profilesList');
        
        if (this.currentProfiles.length === 0) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="text-center py-5">
                        <i class="fas fa-user-plus fa-3x text-muted mb-3"></i>
                        <h4>No Profiles Found</h4>
                        <p class="text-muted">Create your first profile to get started</p>
                        <button class="btn btn-primary" onclick="document.getElementById('create-tab').click()">
                            <i class="fas fa-plus me-1"></i>
                            Create Profile
                        </button>
                    </div>
                </div>
            `;
            return;
        }

        container.innerHTML = this.currentProfiles.map(profile => `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card profile-card h-100 ${profile.is_default ? 'selected' : ''}" data-profile-id="${profile.id}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <h5 class="card-title mb-0">${profile.name}</h5>
                            ${profile.is_default ? '<span class="badge bg-primary">Default</span>' : ''}
                        </div>
                        <p class="card-text text-muted small">
                            <i class="fas fa-envelope me-1"></i>
                            ${profile.email}
                        </p>
                        <p class="card-text text-muted small">
                            <i class="fas fa-calendar me-1"></i>
                            Created: ${new Date(profile.created_at).toLocaleDateString()}
                        </p>
                        <div class="btn-group w-100" role="group">
                            <button class="btn btn-outline-primary btn-sm" onclick="profileManager.selectProfile('${profile.id}')">
                                <i class="fas fa-check me-1"></i>
                                Select
                            </button>
                            <button class="btn btn-outline-secondary btn-sm" onclick="profileManager.editProfile('${profile.id}')">
                                <i class="fas fa-edit me-1"></i>
                                Edit
                            </button>
                            <button class="btn btn-outline-danger btn-sm" onclick="profileManager.confirmDelete('${profile.id}')">
                                <i class="fas fa-trash me-1"></i>
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async saveProfile() {
        const formData = this.collectFormData();
        
        try {
            const response = await fetch('/api/profiles', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            
            if (data.success) {
                this.showAlert('Profile saved successfully!', 'success');
                this.resetForm();
                document.getElementById('list-tab').click();
                this.loadProfiles();
            } else {
                this.showAlert('Error saving profile: ' + data.error, 'danger');
            }
        } catch (error) {
            console.error('Error saving profile:', error);
            this.showAlert('Failed to save profile', 'danger');
        }
    }

    collectFormData() {
        // Personal Information
        const resumeInfo = {
            name: document.getElementById('fullName').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            education: {
                degree: document.getElementById('degree').value,
                university: document.getElementById('university').value,
                graduation: document.getElementById('graduation').value,
                gpa: document.getElementById('gpa').value,
                honors: document.getElementById('honors').value
            },
            core_skills: [],
            experience: [],
            projects: [],
            domain_expertise: document.getElementById('domainExpertise').value
        };

        // Collect skills
        document.querySelectorAll('.skill-input').forEach(input => {
            if (input.value.trim()) {
                resumeInfo.core_skills.push(input.value.trim());
            }
        });

        // Collect experience
        document.querySelectorAll('.experience-entry').forEach(entry => {
            const title = entry.querySelector('.exp-title').value;
            const company = entry.querySelector('.exp-company').value;
            const period = entry.querySelector('.exp-period').value;
            const description = entry.querySelector('.exp-description').value;
            
            if (title && company) {
                resumeInfo.experience.push({
                    title,
                    company,
                    period,
                    description
                });
            }
        });

        // Collect projects
        document.querySelectorAll('.project-input').forEach(input => {
            if (input.value.trim()) {
                resumeInfo.projects.push(input.value.trim());
            }
        });

        // Social profiles
        const socialProfiles = {
            linkedin: document.getElementById('linkedin').value,
            github: document.getElementById('github').value
        };

        return {
            RESUME_INFO: resumeInfo,
            PROJECT_DESCRIPTIONS: {}, // Will be populated later or through advanced editing
            SOCIAL_PROFILES: socialProfiles
        };
    }

    async selectProfile(profileId) {
        try {
            const response = await fetch(`/api/profiles/${profileId}/set-default`, {
                method: 'POST'
            });

            const data = await response.json();
            
            if (data.success) {
                this.showAlert('Profile selected as default!', 'success');
                this.loadProfiles();
            } else {
                this.showAlert('Error selecting profile: ' + data.error, 'danger');
            }
        } catch (error) {
            console.error('Error selecting profile:', error);
            this.showAlert('Failed to select profile', 'danger');
        }
    }

    async editProfile(profileId) {
        // For now, just show an alert. Full editing can be implemented later
        this.showAlert('Profile editing will be available in a future update', 'info');
    }

    confirmDelete(profileId) {
        this.selectedProfile = profileId;
        const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
        modal.show();
    }

    async deleteProfile() {
        if (!this.selectedProfile) return;

        try {
            const response = await fetch(`/api/profiles/${this.selectedProfile}`, {
                method: 'DELETE'
            });

            const data = await response.json();
            
            if (data.success) {
                this.showAlert('Profile deleted successfully!', 'success');
                this.loadProfiles();
                const modal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'));
                modal.hide();
            } else {
                this.showAlert('Error deleting profile: ' + data.error, 'danger');
            }
        } catch (error) {
            console.error('Error deleting profile:', error);
            this.showAlert('Failed to delete profile', 'danger');
        }

        this.selectedProfile = null;
    }

    resetForm() {
        document.getElementById('profileForm').reset();
        
        // Reset dynamic fields
        document.getElementById('skillsContainer').innerHTML = `
            <div class="mb-3">
                <label class="form-label">Skill Category 1</label>
                <input type="text" class="form-control skill-input" placeholder="e.g., Programming & ML: Python, C/C++, R, PyTorch">
            </div>
        `;
        
        document.getElementById('experienceContainer').innerHTML = '';
        
        document.getElementById('projectsContainer').innerHTML = `
            <div class="mb-3">
                <label class="form-label">Project 1</label>
                <textarea class="form-control project-input" rows="2" placeholder="Brief project description with key achievements"></textarea>
            </div>
        `;
    }

    showAlert(message, type = 'info') {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at top of container
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.profileManager = new ProfileManager();
});

