"""
User Profile and Project Information
This file contains the extracted resume information and detailed project descriptions
for the cover letter generation system.
"""

# Resume Information Extracted from PDF
RESUME_INFO = {
    "name": "Ethan Xin",
    "email": "ziyanxinbci@gmail.com",
    "phone": "+1-412-980-3368",
    "education": {
        "degree": "B.S. Computational Neuroscience (minor in AI)",
        "university": "Carnegie Mellon University",
        "graduation": "May 2026",
        "gpa": "3.61",
        "honors": "DEAN's list honor"
    },
    "core_skills": [
        "Programming & ML: Python, C/C++, R, fsm, PyTorch, TensorFlow, PaddlePaddle, LangChain",
        "AI Systems & Tools: GraphRAG, AI Agents, Google ADK, OpenAI ADK, Docker, Git, Colab, Label Studio",
        "Languages: Fluent in English and Mandarin, A2 Spanish proficiency"
    ],
    "experience": [
        {
            "title": "Algorithm Engineer",
            "company": "ITLogica, Nanjing",
            "period": "Jun 2025 – Aug 2025",
            "description": "Designed real-time license-plate pipeline (YOLOv8 + PaddleOCR); achieved 20% overall precision boost with <180ms mobile latency."
        },
        {
            "title": "Project Lead (LLM News Dashboard)",
            "company": "CMU",
            "period": "Aug 2024 – Present",
            "description": "Partnered with PublicSource; prompt-tuned LLM + label filter (region F1 = 0.93 on custom dataset) for precise article push/filtering."
        },
        {
            "title": "Algorithm Engineer",
            "company": "Xuanjia Technology, Nanjing",
            "period": "Jun 2024 – Aug 2024",
            "description": "Benchmarked and optimized super-resolution pipelines (TensorFlow, PyTorch), achieving 60% throughput gain via pruning & fine-tuning."
        },
        {
            "title": "Medical-Tech Intern",
            "company": "VISHEE",
            "period": "Dec 2023 – Jan 2024",
            "description": "Proposed 9 cortical targets for AI-guided TMS therapy; validated CNN-based field simulation for treatment optimization."
        }
    ],
    "projects": [
        "NFNet-to-PP-HGNet Distillation - Teacher-student model compression for mobile deployment; 97% accuracy on 21MB phone model with occlusion handling.",
        "AI Agent System - Built multimodal agents using Langgraph/GraphRAG for data cleaning, requirement document writing, and notes taking tasks.",
        "YouTube Comment Analysis - Analyzed 890K religious comments via LDA topic modeling; integrated video metadata for classification.",
        "Cognitive Robotics tour guide - Collaborated on a pioneering undergraduate project to develop an LLM-driven robotic museum tour guide"
    ],
    "domain_expertise": "Applied neuroscience, Neural Signal Processing, Machine Learning, AI-powered product ideation, rapid prototyping"
}

# Detailed Project Descriptions for Cover Letter Generation
PROJECT_DESCRIPTIONS = {
    "algorithm_research": {
        "title": "Algorithm Research & Optimization",
        "what_you_did": "Focused on applying frontier models to real-world scenarios with extreme optimization during algorithm engineer positions at ITLogica and Xuanjia Technology",
        "how_you_did_it": "Implemented pruning and fine-tuning techniques for super-resolution models, designed real-time license plate recognition systems using YOLOv8 + PaddleOCR",
        "results": "Achieved 60% throughput speed improvement for super-resolution models, controlled latency under 180ms while improving global accuracy by 20%, reaching 97% recognition accuracy on previously unrecognizable cases. Passionate about solving complex challenges that balance performance and accuracy.",
        "category": "technical_research"
    },
    
    "agent_development": {
        "title": "AI Agent System Development",
        "what_you_did": "Built comprehensive multimodal AI agent systems using cutting-edge technologies like LangGraph, GraphRAG, and various AI development SDKs including OpenAI and Google's",
        "how_you_did_it": "Applied these technologies to solve real-world problems through hands-on projects and practical implementations, focusing on data processing, requirement analysis, and automation",
        "results": "Successfully created a data cleaning agent for ITLogica, developed a notes-taking agent that converts PPT courseware into systematic refined notes, and built a requirement document generation agent for business analytics team, significantly improving workflow efficiency.",
        "category": "both"
    },
    
    "news_dashboard": {
        "title": "LLM News Dashboard Project Leadership",
        "what_you_did": "Led CMU's LLM News Dashboard project in collaboration with external partner PublicSource, taking full responsibility from data processing to model fine-tuning",
        "how_you_did_it": "Collaborated closely with external partners to understand user requirements, implemented comprehensive data pipeline, and fine-tuned LLM models with custom labeling filters",
        "results": "Achieved F1 score improvement from 0.93 in MVP to completely meeting and exceeding partner requirements. Enhanced ability to communicate with large enterprises and better understand their project needs and technical implementation requirements.",
        "category": "product"
    }
}

# LinkedIn Profile and GitHub for reference
SOCIAL_PROFILES = {
    "linkedin": "www.linkedin.com/in/ziyan-xin-20191a22b",
    "github": "https://github.com/Ziyan0219?tab=repositories"
}

