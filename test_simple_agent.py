#!/usr/bin/env python3
"""
Simple test script to diagnose the cover letter generation issue
"""

import os
import sys
import traceback

# Add the current directory to Python path
sys.path.insert(0, '/home/ubuntu/cover-letter-agent')

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from agents.langgraph_orchestrator import LangGraphOrchestrator
        print("✅ LangGraphOrchestrator imported successfully")
    except Exception as e:
        print(f"❌ Failed to import LangGraphOrchestrator: {e}")
        traceback.print_exc()
        return False
    
    try:
        from user_profile import RESUME_INFO, PROJECT_DESCRIPTIONS
        print("✅ User profile imported successfully")
    except Exception as e:
        print(f"❌ Failed to import user profile: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\nTesting OpenAI connection...")
    
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_API_BASE")
        )
        
        # Test with a simple message
        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content="Hello, this is a test.")])
        print("✅ OpenAI connection successful")
        print(f"Response: {response.content[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        traceback.print_exc()
        return False

def test_individual_agents():
    """Test individual agents"""
    print("\nTesting individual agents...")
    
    try:
        from agents.company_research_agent import CompanyResearchAgent
        
        agent = CompanyResearchAgent()
        print("✅ CompanyResearchAgent created successfully")
        
        # Test with simple input
        test_input = {
            "company_name": "Google",
            "job_title": "Data Scientist",
            "job_description": "We are looking for a data scientist...",
            "resume_info": {"name": "Test User"}
        }
        
        result = agent.process(test_input)
        print("✅ CompanyResearchAgent processing successful")
        print(f"Result keys: {list(result.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent testing failed: {e}")
        traceback.print_exc()
        return False

def test_orchestrator():
    """Test the LangGraph orchestrator"""
    print("\nTesting LangGraph orchestrator...")
    
    try:
        from agents.langgraph_orchestrator import LangGraphOrchestrator
        from user_profile import RESUME_INFO, PROJECT_DESCRIPTIONS
        
        orchestrator = LangGraphOrchestrator()
        print("✅ Orchestrator created successfully")
        
        # Test with simple input
        input_data = {
            "company_name": "Google",
            "job_title": "Data Scientist", 
            "job_description": "We are looking for a data scientist with machine learning experience.",
            "resume_info": RESUME_INFO,
            "project_descriptions": PROJECT_DESCRIPTIONS
        }
        
        result = orchestrator.generate_cover_letter_sync(input_data)
        print("✅ Orchestrator processing successful")
        print(f"Success: {result.get('success')}")
        print(f"Status: {result.get('status')}")
        
        if not result.get('success'):
            print(f"Errors: {result.get('errors')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Orchestrator testing failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=== Cover Letter Generation System Diagnostic ===\n")
    
    # Check environment variables
    print("Environment variables:")
    print(f"OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
    print(f"OPENAI_API_BASE: {os.getenv('OPENAI_API_BASE', 'Not set')}")
    print()
    
    # Run tests
    tests = [
        ("Import Test", test_imports),
        ("OpenAI Connection Test", test_openai_connection),
        ("Individual Agents Test", test_individual_agents),
        ("Orchestrator Test", test_orchestrator)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
        print()
    
    # Summary
    print("=== Test Summary ===")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    print(f"\nOverall: {total_passed}/{total_tests} tests passed")

if __name__ == "__main__":
    main()

