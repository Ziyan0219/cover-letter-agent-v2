"""
LangGraph Orchestrator
Coordinates the execution of all agents using LangGraph for parallel processing
"""

from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .company_research_agent import CompanyResearchAgent
from .experience_matching_agent import ExperienceMatchingAgent
from .document_assembly_agent import DocumentAssemblyAgent


class CoverLetterState(TypedDict):
    """State object for the cover letter generation workflow"""
    # Input data
    company_name: str
    job_title: str
    job_description: str
    resume_info: Dict[str, Any]
    project_descriptions: Dict[str, Any]
    
    # Intermediate results
    company_research_result: Dict[str, Any]
    experience_matching_result: Dict[str, Any]
    
    # Final output
    final_document: Dict[str, Any]
    
    # Workflow status
    status: str
    errors: List[str]


class LangGraphOrchestrator:
    """Orchestrates the cover letter generation workflow using LangGraph"""
    
    def __init__(self):
        """Initialize the orchestrator with all agents"""
        self.company_research_agent = CompanyResearchAgent()
        self.experience_matching_agent = ExperienceMatchingAgent()
        self.document_assembly_agent = DocumentAssemblyAgent()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create the state graph
        workflow = StateGraph(CoverLetterState)
        
        # Add nodes for each agent
        workflow.add_node("company_research", self._company_research_node)
        workflow.add_node("experience_matching", self._experience_matching_node)
        workflow.add_node("document_assembly", self._document_assembly_node)
        
        # Define the workflow edges
        workflow.set_entry_point("company_research")
        workflow.add_edge("company_research", "experience_matching")
        workflow.add_edge("experience_matching", "document_assembly")
        workflow.add_edge("document_assembly", END)
        
        return workflow.compile()
    
    def _company_research_node(self, state: CoverLetterState) -> CoverLetterState:
        """Execute company research agent"""
        try:
            input_data = {
                "company_name": state["company_name"],
                "job_title": state["job_title"],
                "job_description": state["job_description"],
                "resume_info": state["resume_info"]
            }
            
            result = self.company_research_agent.process(input_data)
            state["company_research_result"] = result
            state["status"] = "company_research_completed"
            
        except Exception as e:
            state["errors"].append(f"Company research error: {str(e)}")
            state["status"] = "error"
        
        return state
    
    def _experience_matching_node(self, state: CoverLetterState) -> CoverLetterState:
        """Execute experience matching agent"""
        try:
            input_data = {
                "job_description": state["job_description"],
                "job_title": state["job_title"],
                "project_descriptions": state["project_descriptions"],
                "resume_info": state["resume_info"]
            }
            
            result = self.experience_matching_agent.process(input_data)
            state["experience_matching_result"] = result
            state["status"] = "experience_matching_completed"
            
        except Exception as e:
            state["errors"].append(f"Experience matching error: {str(e)}")
            state["status"] = "error"
        
        return state
    
    def _document_assembly_node(self, state: CoverLetterState) -> CoverLetterState:
        """Execute document assembly agent"""
        try:
            # Combine results from previous agents
            company_result = state["company_research_result"]
            experience_result = state["experience_matching_result"]
            
            input_data = {
                "opening": company_result.get("opening", ""),
                "experience_section": experience_result.get("experience_section", ""),
                "cultural_fit": company_result.get("cultural_fit", ""),
                "closing": company_result.get("closing", ""),
                "candidate_info": state["resume_info"],
                "company_name": state["company_name"],
                "job_title": state["job_title"],
                "output_dir": "generated_letters"
            }
            
            result = self.document_assembly_agent.process(input_data)
            state["final_document"] = result
            state["status"] = "completed"
            
        except Exception as e:
            state["errors"].append(f"Document assembly error: {str(e)}")
            state["status"] = "error"
        
        return state
    
    async def generate_cover_letter(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a cover letter using the LangGraph workflow
        
        Args:
            input_data: Dictionary containing all required input data
            
        Returns:
            Dictionary with the final cover letter and metadata
        """
        
        # Initialize state
        initial_state = CoverLetterState(
            company_name=input_data["company_name"],
            job_title=input_data["job_title"],
            job_description=input_data["job_description"],
            resume_info=input_data["resume_info"],
            project_descriptions=input_data["project_descriptions"],
            company_research_result={},
            experience_matching_result={},
            final_document={},
            status="initialized",
            errors=[]
        )
        
        try:
            # Execute the workflow
            final_state = await self._execute_workflow(initial_state)
            
            return {
                "success": final_state["status"] == "completed",
                "final_document": final_state.get("final_document", {}),
                "company_research": final_state.get("company_research_result", {}),
                "experience_matching": final_state.get("experience_matching_result", {}),
                "status": final_state["status"],
                "errors": final_state["errors"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status": "workflow_error",
                "errors": [str(e)]
            }
    
    async def _execute_workflow(self, initial_state: CoverLetterState) -> CoverLetterState:
        """Execute the LangGraph workflow asynchronously"""
        
        # Run the workflow in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            final_state = await loop.run_in_executor(
                executor, 
                self._run_workflow_sync, 
                initial_state
            )
        
        return final_state
    
    def _run_workflow_sync(self, initial_state: CoverLetterState) -> CoverLetterState:
        """Run the workflow synchronously"""
        
        # Execute the workflow
        result = self.workflow.invoke(initial_state)
        return result
    
    def generate_cover_letter_sync(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronous version of cover letter generation
        
        Args:
            input_data: Dictionary containing all required input data
            
        Returns:
            Dictionary with the final cover letter and metadata
        """
        
        # Initialize state
        initial_state = CoverLetterState(
            company_name=input_data["company_name"],
            job_title=input_data["job_title"],
            job_description=input_data["job_description"],
            resume_info=input_data["resume_info"],
            project_descriptions=input_data["project_descriptions"],
            company_research_result={},
            experience_matching_result={},
            final_document={},
            status="initialized",
            errors=[]
        )
        
        try:
            # Execute the workflow
            final_state = self._run_workflow_sync(initial_state)
            
            return {
                "success": final_state["status"] == "completed",
                "final_document": final_state.get("final_document", {}),
                "company_research": final_state.get("company_research_result", {}),
                "experience_matching": final_state.get("experience_matching_result", {}),
                "status": final_state["status"],
                "errors": final_state["errors"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status": "workflow_error",
                "errors": [str(e)]
            }

