"""
Document Assembly Agent
Responsible for combining all sections into a cohesive cover letter and generating Word document
"""

from typing import Dict, Any
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os
from datetime import datetime
from .base_agent import BaseAgent


class DocumentAssemblyAgent(BaseAgent):
    """Agent responsible for assembling the final cover letter document"""
    
    def get_system_prompt(self) -> str:
        return """You are a professional document assembly assistant specializing in cover letter formatting and final review.

Your task is to:
1. Combine all sections into a cohesive, well-flowing cover letter
2. Ensure smooth transitions between sections
3. Maintain consistent tone and style throughout
4. Perform final quality checks for grammar, flow, and professionalism
5. Format the document appropriately for professional presentation

Guidelines:
- Ensure the letter flows naturally from opening to closing
- Maintain professional, sincere, and human-like tone
- Check for any repetitive content or awkward transitions
- Ensure the letter is approximately one page in length
- Verify all company and position names are correct
- Make minor adjustments for better readability and impact

Output should be the final, polished cover letter text.
"""
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assemble the final cover letter document
        
        Args:
            input_data: Dictionary containing:
                - opening: Opening paragraph
                - experience_section: Experience/projects section
                - cultural_fit: Cultural fit paragraph
                - closing: Closing paragraph
                - candidate_info: Candidate information
                - company_name: Company name
                - job_title: Position title
                - output_dir: Directory to save the document
                
        Returns:
            Dictionary with final document path and content
        """
        required_keys = ["opening", "experience_section", "cultural_fit", "closing", 
                        "candidate_info", "company_name", "job_title"]
        if not self.validate_input(input_data, required_keys):
            raise ValueError(f"Missing required keys: {required_keys}")
        
        # Assemble the cover letter content
        cover_letter_content = self._assemble_content(input_data)
        
        # Polish the content using LLM
        polished_content = self._polish_content(cover_letter_content, input_data)
        
        # Generate Word document
        output_dir = input_data.get("output_dir", "generated_letters")
        doc_path = self._generate_word_document(polished_content, input_data, output_dir)
        
        return {
            "final_content": polished_content,
            "document_path": doc_path,
            "word_count": len(polished_content.split()),
            "status": "completed"
        }
    
    def _assemble_content(self, input_data: Dict[str, Any]) -> str:
        """Assemble the basic cover letter structure"""
        
        candidate_info = input_data["candidate_info"]
        
        # Header with candidate information
        header = f"""
{candidate_info.get('name', 'Ethan Xin')}
{candidate_info.get('email', 'ziyanxinbci@gmail.com')}
{candidate_info.get('phone', '+1-412-980-3368')}

{datetime.now().strftime('%B %d, %Y')}

Hiring Manager
{input_data['company_name']}

Dear Hiring Manager,
"""
        
        # Assemble body sections
        body = f"""
{input_data['opening']}

{input_data['experience_section']}

{input_data['cultural_fit']}

{input_data['closing']}

Sincerely,
{candidate_info.get('name', 'Ethan Xin')}
"""
        
        return header + body
    
    def _polish_content(self, content: str, input_data: Dict[str, Any]) -> str:
        """Polish the content using LLM for final improvements"""
        
        user_prompt = f"""
Please review and polish the following cover letter for a {input_data['job_title']} position at {input_data['company_name']}:

{content}

Please:
1. Ensure smooth transitions between paragraphs
2. Check for any repetitive content
3. Verify the tone is professional yet personable
4. Make minor improvements for better flow and impact
5. Ensure the letter is concise and impactful
6. Maintain all specific details about the candidate and company

Return only the polished cover letter text, maintaining the same structure and format.
"""
        
        polished = self.generate_response(user_prompt)
        return polished.strip()
    
    def _generate_word_document(self, content: str, input_data: Dict[str, Any], output_dir: str) -> str:
        """Generate a Word document from the cover letter content"""
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create document
        doc = Document()
        
        # Set document margins
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
        
        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        
        for para_text in paragraphs:
            if para_text.strip():
                paragraph = doc.add_paragraph(para_text.strip())
                
                # Special formatting for header information
                if any(info in para_text for info in ['@', '+1-', 'Dear']):
                    if 'Dear' in para_text:
                        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    else:
                        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                else:
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        # Generate filename
        company_safe = "".join(c for c in input_data['company_name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        position_safe = "".join(c for c in input_data['job_title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        filename = f"Cover_Letter_{company_safe}_{position_safe}_{timestamp}.docx"
        filepath = os.path.join(output_dir, filename)
        
        # Save document
        doc.save(filepath)
        
        return filepath
    
    def get_document_stats(self, content: str) -> Dict[str, Any]:
        """Get statistics about the generated document"""
        
        words = content.split()
        sentences = content.split('.')
        paragraphs = content.split('\n\n')
        
        return {
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "paragraph_count": len([p for p in paragraphs if p.strip()]),
            "estimated_reading_time": len(words) / 200,  # Assuming 200 WPM reading speed
            "character_count": len(content),
            "character_count_no_spaces": len(content.replace(' ', ''))
        }

