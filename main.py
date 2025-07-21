"""
FastAPI application for the Cover Letter Generation System
"""

from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import asyncio
from pathlib import Path
from typing import Optional
import PyPDF2
import json

from agents.langgraph_orchestrator import LangGraphOrchestrator
from user_profile import PROFILES
from profile_manager import profile_manager

# Initialize FastAPI app
app = FastAPI(
    title="Cover Letter Generation System",
    description="An intelligent cover letter generation system powered by LangGraph and FastAPI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Initialize the orchestrator
orchestrator = LangGraphOrchestrator()

# Ensure directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("generated_letters", exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with the cover letter generation form"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Cover Letter Generation System is running"}


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload and process resume PDF"""
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save uploaded file
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Extract text from PDF
        resume_text = extract_pdf_text(file_path)
        
        return {
            "success": True,
            "filename": file.filename,
            "text_preview": resume_text[:500] + "..." if len(resume_text) > 500 else resume_text,
            "message": "Resume uploaded and processed successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.get("/profiles", response_class=HTMLResponse)
async def profiles_page(request: Request):
    """Profile management page"""
    return templates.TemplateResponse("profile_manager.html", {"request": request})


@app.get("/api/profiles")
async def list_profiles():
    """Get all profiles"""
    try:
        profiles = profile_manager.list_profiles()
        return {
            "success": True,
            "profiles": profiles
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "profiles": []
        }


@app.get("/api/profiles/{profile_id}")
async def get_profile(profile_id: str):
    """Get a specific profile"""
    try:
        profile_data = profile_manager.get_profile(profile_id)
        if profile_data:
            return {
                "success": True,
                "profile": profile_data
            }
        else:
            raise HTTPException(status_code=404, detail="Profile not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving profile: {str(e)}")


@app.post("/api/profiles")
async def create_profile(profile_data: dict):
    """Create a new profile"""
    try:
        profile_id = profile_manager.create_profile(profile_data)
        return {
            "success": True,
            "profile_id": profile_id,
            "message": "Profile created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating profile: {str(e)}")


@app.put("/api/profiles/{profile_id}")
async def update_profile(profile_id: str, profile_data: dict):
    """Update an existing profile"""
    try:
        success = profile_manager.update_profile(profile_id, profile_data)
        if success:
            return {
                "success": True,
                "message": "Profile updated successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Profile not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")


@app.delete("/api/profiles/{profile_id}")
async def delete_profile(profile_id: str):
    """Delete a profile"""
    try:
        success = profile_manager.delete_profile(profile_id)
        if success:
            return {
                "success": True,
                "message": "Profile deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Profile not found or cannot be deleted")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting profile: {str(e)}")


@app.post("/api/profiles/{profile_id}/set-default")
async def set_default_profile(profile_id: str):
    """Set a profile as default"""
    try:
        success = profile_manager.set_default_profile(profile_id)
        if success:
            return {
                "success": True,
                "message": "Default profile updated successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Profile not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting default profile: {str(e)}")


@app.post("/generate-cover-letter")
async def generate_cover_letter(
    company_name: str = Form(...),
    job_title: str = Form(...),
    job_description: str = Form(...),
    profile_id: str = Form(...),
    resume_file: Optional[str] = Form(None)
):
    """Generate a cover letter using the LangGraph system"""
    
    try:
        # Get profile data
        profile_data = profile_manager.get_profile_for_generation(profile_id)
        if not profile_data:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Prepare input data
        input_data = {
            "company_name": company_name,
            "job_title": job_title,
            "job_description": job_description,
            "resume_info": profile_data["resume_info"],
            "project_descriptions": profile_data["project_descriptions"]
        }
        
        # Generate cover letter using the orchestrator
        result = orchestrator.generate_cover_letter_sync(input_data)
        
        if result["success"]:
            final_document = result["final_document"]
            
            return {
                "success": True,
                "document_path": final_document.get("document_path", ""),
                "content": final_document.get("final_content", ""),
                "word_count": final_document.get("word_count", 0),
                "company_research": result.get("company_research", {}),
                "experience_matching": result.get("experience_matching", {}),
                "message": "Cover letter generated successfully!"
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to generate cover letter: {result.get('error', 'Unknown error')}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating cover letter: {str(e)}")


@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download generated cover letter"""
    
    file_path = f"generated_letters/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )


@app.get("/preview/{filename}")
async def preview_file(filename: str):
    """Preview generated cover letter content"""
    
    file_path = f"generated_letters/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # For Word documents, we'll return basic info
        # In production, you might want to convert to HTML for preview
        return {
            "filename": filename,
            "file_size": os.path.getsize(file_path),
            "created_time": os.path.getctime(file_path),
            "message": "Document ready for download"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error previewing file: {str(e)}")


@app.get("/api/company-info/{company_name}")
async def get_company_info(company_name: str):
    """Get company information for preview"""
    
    try:
        from services.company_research_service import CompanyResearchService
        
        research_service = CompanyResearchService()
        company_info = research_service.research_company(company_name)
        
        return {
            "success": True,
            "company_info": company_info
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "company_info": {}
        }


def extract_pdf_text(file_path: str) -> str:
    """Extract text content from PDF file"""
    
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
    
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    # Load environment variables
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print(f"Starting Cover Letter Generation System on {host}:{port}")
    print(f"Debug mode: {debug}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )

