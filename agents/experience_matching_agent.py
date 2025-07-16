"""
Experience Matching Agent
Responsible for customizing project descriptions to match job requirements
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent


class ExperienceMatchingAgent(BaseAgent):
    """Agent responsible for matching candidate experience with job requirements"""
    
    def get_system_prompt(self) -> str:
        return """You are a professional cover letter writing assistant specializing in experience matching and project customization.

Your task is to:
1. Analyze the job description to identify key requirements and skills
2. Select 2-3 most relevant projects from the candidate's experience
3. Customize each project description to highlight relevance to the job
4. Structure each project with: What you did, How you did it, What was the result
5. Connect the candidate's experience to the company's needs

Guidelines:
- Write in professional, sincere, and human-like English
- Focus on quantifiable achievements and specific technologies
- Emphasize skills and experiences most relevant to the job description
- Show progression and growth in capabilities
- Use action verbs and specific metrics where possible
- Each project description should be 3-4 sentences

Output format should be JSON with key "experience_section" containing the complete experience paragraph.
"""
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process job requirements and generate customized experience section
        
        Args:
            input_data: Dictionary containing:
                - job_description: Job posting description
                - job_title: Position being applied for
                - project_descriptions: Detailed project information
                - resume_info: Candidate's resume information
                
        Returns:
            Dictionary with customized experience section
        """
        required_keys = ["job_description", "job_title", "project_descriptions", "resume_info"]
        if not self.validate_input(input_data, required_keys):
            raise ValueError(f"Missing required keys: {required_keys}")
        
        # Analyze job requirements
        job_analysis = self._analyze_job_requirements(input_data["job_description"])
        
        # Select most relevant projects
        relevant_projects = self._select_relevant_projects(
            input_data["project_descriptions"], 
            job_analysis,
            input_data["job_title"]
        )
        
        # Generate customized experience section
        user_prompt = self._create_experience_prompt(input_data, job_analysis, relevant_projects)
        response = self.generate_response(user_prompt)
        
        # Parse response
        try:
            import json
            result = json.loads(response)
            return {
                "experience_section": result.get("experience_section", ""),
                "selected_projects": relevant_projects,
                "job_analysis": job_analysis
            }
        except json.JSONDecodeError:
            # Fallback: return the response as experience section
            return {
                "experience_section": response.strip(),
                "selected_projects": relevant_projects,
                "job_analysis": job_analysis
            }
    
    def _analyze_job_requirements(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze job description to extract key requirements
        
        Args:
            job_description: The job posting description
            
        Returns:
            Dictionary with analyzed requirements
        """
        # Simple keyword extraction - in production, use more sophisticated NLP
        technical_keywords = [
            "python", "machine learning", "ai", "deep learning", "tensorflow", "pytorch",
            "data science", "nlp", "computer vision", "llm", "neural networks",
            "optimization", "algorithms", "real-time", "pipeline", "deployment"
        ]
        
        soft_skills = [
            "leadership", "collaboration", "communication", "problem solving",
            "project management", "teamwork", "innovation", "research"
        ]
        
        job_lower = job_description.lower()
        
        found_technical = [kw for kw in technical_keywords if kw in job_lower]
        found_soft = [kw for kw in soft_skills if kw in job_lower]
        
        return {
            "technical_requirements": found_technical,
            "soft_skills": found_soft,
            "key_phrases": self._extract_key_phrases(job_description),
            "seniority_level": self._determine_seniority(job_description)
        }
    
    def _extract_key_phrases(self, job_description: str) -> List[str]:
        """Extract key phrases from job description"""
        # Simplified key phrase extraction
        phrases = []
        lines = job_description.split('\n')
        for line in lines:
            if any(word in line.lower() for word in ['experience', 'required', 'preferred', 'must']):
                phrases.append(line.strip())
        return phrases[:5]  # Return top 5 key phrases
    
    def _determine_seniority(self, job_description: str) -> str:
        """Determine the seniority level from job description"""
        job_lower = job_description.lower()
        if any(word in job_lower for word in ['senior', 'lead', 'principal', 'staff']):
            return "senior"
        elif any(word in job_lower for word in ['junior', 'entry', 'associate', 'new grad']):
            return "junior"
        else:
            return "mid"
    
    def _select_relevant_projects(self, project_descriptions: Dict[str, Any], 
                                job_analysis: Dict[str, Any], job_title: str) -> List[Dict[str, Any]]:
        """
        Select the most relevant projects based on job requirements and company type
        
        Args:
            project_descriptions: Available project descriptions
            job_analysis: Analyzed job requirements
            job_title: Position being applied for
            
        Returns:
            List of selected projects with relevance scores
        """
        # Detect company type based on job description and title
        company_type = self._detect_company_type(job_analysis, job_title)
        
        # Select projects based on company type and user's requirements
        selected_projects = self._select_projects_by_type(project_descriptions, company_type)
        
        # Score and rank the selected projects
        projects = []
        for project_key, project_info in selected_projects.items():
            score = self._calculate_relevance_score(project_info, job_analysis, job_title)
            projects.append({
                "key": project_key,
                "info": project_info,
                "relevance_score": score
            })
        
        # Sort by relevance and return top 2
        projects.sort(key=lambda x: x["relevance_score"], reverse=True)
        return projects[:2]  # Return exactly 2 projects as requested
    
    def _detect_company_type(self, job_analysis: Dict[str, Any], job_title: str) -> str:
        """
        Detect if the company is technical research-oriented or product-oriented
        
        Args:
            job_analysis: Analyzed job requirements
            job_title: Position being applied for
            
        Returns:
            'technical_research' or 'product'
        """
        job_lower = job_title.lower()
        technical_requirements = job_analysis.get("technical_requirements", [])
        key_phrases = " ".join(job_analysis.get("key_phrases", [])).lower()
        
        # Technical research indicators
        research_indicators = [
            "research", "scientist", "algorithm", "optimization", "neural", "deep learning",
            "machine learning", "ai research", "computer vision", "nlp research", "phd",
            "publication", "paper", "novel", "innovation", "cutting-edge", "frontier"
        ]
        
        # Product-oriented indicators
        product_indicators = [
            "product", "engineer", "developer", "full-stack", "backend", "frontend",
            "deployment", "production", "scale", "user", "customer", "business",
            "dashboard", "application", "platform", "service", "api", "pipeline"
        ]
        
        research_score = sum(1 for indicator in research_indicators 
                           if indicator in job_lower or indicator in key_phrases)
        product_score = sum(1 for indicator in product_indicators 
                          if indicator in job_lower or indicator in key_phrases)
        
        # Additional scoring based on technical requirements
        if any(tech in ["optimization", "algorithms", "neural networks", "deep learning"] 
               for tech in technical_requirements):
            research_score += 2
        
        if any(tech in ["pipeline", "deployment", "real-time"] 
               for tech in technical_requirements):
            product_score += 2
        
        return "technical_research" if research_score > product_score else "product"
    
    def _select_projects_by_type(self, project_descriptions: Dict[str, Any], 
                               company_type: str) -> Dict[str, Any]:
        """
        Select projects based on company type according to user's requirements
        
        Args:
            project_descriptions: Available project descriptions
            company_type: 'technical_research' or 'product'
            
        Returns:
            Dictionary of selected projects
        """
        selected = {}
        
        if company_type == "technical_research":
            # For technical research companies: algorithm_research + agent_development
            if "algorithm_research" in project_descriptions:
                selected["algorithm_research"] = project_descriptions["algorithm_research"]
            if "agent_development" in project_descriptions:
                selected["agent_development"] = project_descriptions["agent_development"]
        else:
            # For product companies: agent_development + news_dashboard
            if "agent_development" in project_descriptions:
                selected["agent_development"] = project_descriptions["agent_development"]
            if "news_dashboard" in project_descriptions:
                selected["news_dashboard"] = project_descriptions["news_dashboard"]
        
        return selected
    
    def _calculate_relevance_score(self, project_info: Dict[str, Any], 
                                 job_analysis: Dict[str, Any], job_title: str) -> float:
        """Calculate relevance score for a project"""
        score = 0.0
        
        # Check technical alignment
        project_text = " ".join([
            project_info.get("title", ""),
            project_info.get("what_you_did", ""),
            project_info.get("how_you_did_it", ""),
            project_info.get("results", "")
        ]).lower()
        
        # Technical requirements match
        for tech in job_analysis.get("technical_requirements", []):
            if tech in project_text:
                score += 2.0
        
        # Soft skills match
        for skill in job_analysis.get("soft_skills", []):
            if skill in project_text:
                score += 1.0
        
        # Job title specific bonuses
        job_lower = job_title.lower()
        if "data scientist" in job_lower and any(word in project_text for word in ["data", "analysis", "model"]):
            score += 3.0
        elif "engineer" in job_lower and any(word in project_text for word in ["optimization", "pipeline", "system"]):
            score += 3.0
        elif "research" in job_lower and any(word in project_text for word in ["research", "novel", "innovation"]):
            score += 3.0
        
        return score
    
    def _create_experience_prompt(self, input_data: Dict[str, Any], 
                                job_analysis: Dict[str, Any], 
                                relevant_projects: List[Dict[str, Any]]) -> str:
        """Create the prompt for experience section generation"""
        
        prompt = f"""
Based on the following information, generate a compelling experience section for a cover letter:

POSITION: {input_data['job_title']}

JOB DESCRIPTION:
{input_data['job_description']}

JOB ANALYSIS:
- Technical Requirements: {', '.join(job_analysis.get('technical_requirements', []))}
- Soft Skills: {', '.join(job_analysis.get('soft_skills', []))}
- Seniority Level: {job_analysis.get('seniority_level', 'mid')}

CANDIDATE'S MOST RELEVANT PROJECTS:

"""
        
        for i, project in enumerate(relevant_projects, 1):
            project_info = project["info"]
            prompt += f"""
PROJECT {i}: {project_info.get('title', '')}
What you did: {project_info.get('what_you_did', '')}
How you did it: {project_info.get('how_you_did_it', '')}
Results: {project_info.get('results', '')}
Relevance Score: {project['relevance_score']:.1f}

"""
        
        prompt += """
Please generate a well-structured experience section that:
1. Creates exactly 2 distinct paragraphs, one for each selected project
2. Each paragraph should be 3-4 sentences focusing on: What you did, How you did it, Results achieved
3. Emphasizes skills and achievements most relevant to the job requirements
4. Uses specific metrics and technologies mentioned in the projects
5. Shows progression and demonstrates impact
6. Connects the candidate's experience directly to the company's needs
7. Maintains professional, sincere tone throughout

STRUCTURE REQUIREMENTS:
- Paragraph 1: Focus on the first project (higher relevance score)
- Paragraph 2: Focus on the second project
- Each paragraph should be self-contained but flow naturally
- Use quantifiable achievements where possible
- Avoid repetitive phrasing between paragraphs

Return the response in JSON format with key "experience_section" containing the complete formatted text with clear paragraph breaks.
"""
        
        return prompt

