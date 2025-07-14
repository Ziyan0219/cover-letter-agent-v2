"""
Company Research Agent
Responsible for researching company information and generating opening and closing sections
"""

from typing import Dict, Any
import requests
from bs4 import BeautifulSoup
from .base_agent import BaseAgent


class CompanyResearchAgent(BaseAgent):
    """Agent responsible for company research and generating opening/closing sections"""
    
    def get_system_prompt(self) -> str:
        return """You are a professional cover letter writing assistant specializing in company research and personalization.

Your task is to:
1. Analyze the provided company information and job description
2. Generate a compelling opening paragraph that mentions the specific position, shows knowledge of the company, and provides a strong hook
3. Generate a cultural fit section that demonstrates genuine interest in the company
4. Generate a professional closing paragraph

Guidelines:
- Write in professional, sincere, and human-like English
- Be specific about the company's products, technologies, values, or recent news
- Connect the candidate's background to the company's mission
- Avoid generic statements that could apply to any company
- Keep the tone enthusiastic but professional
- Each section should be 2-4 sentences long

Output format should be JSON with keys: "opening", "cultural_fit", "closing"
"""
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process company information and generate opening/closing sections
        
        Args:
            input_data: Dictionary containing:
                - company_name: Name of the company
                - job_title: Position being applied for
                - job_description: Job posting description
                - resume_info: Candidate's resume information
                
        Returns:
            Dictionary with opening, cultural_fit, and closing sections
        """
        required_keys = ["company_name", "job_title", "job_description", "resume_info"]
        if not self.validate_input(input_data, required_keys):
            raise ValueError(f"Missing required keys: {required_keys}")
        
        # Research company information
        company_info = self._research_company(input_data["company_name"])
        
        # Generate prompt for LLM
        user_prompt = self._create_research_prompt(input_data, company_info)
        
        # Generate response
        response = self.generate_response(user_prompt)
        
        # Parse response (assuming JSON format)
        try:
            import json
            result = json.loads(response)
            return {
                "opening": result.get("opening", ""),
                "cultural_fit": result.get("cultural_fit", ""),
                "closing": result.get("closing", ""),
                "company_info": company_info
            }
        except json.JSONDecodeError:
            # Fallback: parse manually or return structured response
            return {
                "opening": self._extract_section(response, "opening"),
                "cultural_fit": self._extract_section(response, "cultural_fit"),
                "closing": self._extract_section(response, "closing"),
                "company_info": company_info
            }
    
    def _research_company(self, company_name: str) -> Dict[str, Any]:
        """
        Research company information using web search
        
        Args:
            company_name: Name of the company to research
            
        Returns:
            Dictionary with company information
        """
        try:
            # Use the dedicated research service
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            from services.company_research_service import CompanyResearchService
            
            research_service = CompanyResearchService()
            company_info = research_service.research_company(company_name)
            company_info["research_status"] = "completed"
            
        except Exception as e:
            # Fallback to basic information
            company_info = {
                "name": company_name,
                "description": f"Information about {company_name}",
                "products": [],
                "technologies": [],
                "values": [],
                "recent_news": [],
                "error": str(e),
                "research_status": "failed"
            }
        
        return company_info
    
    def _create_research_prompt(self, input_data: Dict[str, Any], company_info: Dict[str, Any]) -> str:
        """Create the prompt for LLM generation"""
        
        prompt = f"""
Based on the following information, generate a personalized cover letter opening, cultural fit section, and closing:

COMPANY: {input_data['company_name']}
POSITION: {input_data['job_title']}

JOB DESCRIPTION:
{input_data['job_description']}

CANDIDATE BACKGROUND:
- Name: {input_data['resume_info'].get('name', 'Ethan Xin')}
- Education: {input_data['resume_info'].get('education', {}).get('degree', '')} from {input_data['resume_info'].get('education', {}).get('university', '')}
- Core Skills: {', '.join(input_data['resume_info'].get('core_skills', []))}
- Domain Expertise: {input_data['resume_info'].get('domain_expertise', '')}

COMPANY RESEARCH:
{company_info}

Please generate:

1. OPENING: A compelling opening paragraph that:
   - States the position being applied for
   - Mentions seeing the job on LinkedIn
   - Shows knowledge of the company
   - Provides one sentence explaining passion for the role and why they're a strong candidate

2. CULTURAL_FIT: A paragraph explaining why they want to join THIS specific company:
   - Reference specific company products, technologies, values, or recent news
   - Connect their professional background or projects to the company's mission
   - Express genuine admiration for the company's technology or approach

3. CLOSING: A professional closing that:
   - Reiterates enthusiasm and confidence
   - Thanks for time and consideration
   - Expresses hope for interview opportunity

Return the response in JSON format with keys "opening", "cultural_fit", and "closing".
"""
        return prompt
    
    def _extract_section(self, response: str, section_name: str) -> str:
        """Extract a specific section from the response if JSON parsing fails"""
        # Simple fallback extraction
        lines = response.split('\n')
        section_content = []
        in_section = False
        
        for line in lines:
            if section_name.upper() in line.upper():
                in_section = True
                continue
            elif in_section and any(keyword in line.upper() for keyword in ['OPENING', 'CULTURAL', 'CLOSING']):
                break
            elif in_section:
                section_content.append(line.strip())
        
        return ' '.join(section_content).strip()

