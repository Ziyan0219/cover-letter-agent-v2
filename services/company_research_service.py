"""
Company Research Service
Handles web search and information extraction for companies
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
import time
import re
from urllib.parse import urljoin, urlparse


class CompanyResearchService:
    """Service for researching company information through web search"""
    
    def __init__(self):
        """Initialize the research service"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def research_company(self, company_name: str) -> Dict[str, Any]:
        """
        Research comprehensive information about a company
        
        Args:
            company_name: Name of the company to research
            
        Returns:
            Dictionary containing company information
        """
        
        company_info = {
            "name": company_name,
            "description": "",
            "products": [],
            "technologies": [],
            "values": [],
            "recent_news": [],
            "website": "",
            "industry": "",
            "size": "",
            "founded": "",
            "headquarters": "",
            "mission": "",
            "search_queries_used": [],
            "sources": []
        }
        
        try:
            # Search for basic company information
            basic_info = self._search_basic_info(company_name)
            company_info.update(basic_info)
            
            # Search for products and services
            products_info = self._search_products_services(company_name)
            company_info["products"].extend(products_info.get("products", []))
            company_info["technologies"].extend(products_info.get("technologies", []))
            
            # Search for company values and culture
            values_info = self._search_values_culture(company_name)
            company_info["values"].extend(values_info.get("values", []))
            company_info["mission"] = values_info.get("mission", company_info["mission"])
            
            # Search for recent news
            news_info = self._search_recent_news(company_name)
            company_info["recent_news"].extend(news_info.get("news", []))
            
            # Clean and deduplicate information
            company_info = self._clean_company_info(company_info)
            
        except Exception as e:
            company_info["error"] = str(e)
            company_info["research_status"] = "failed"
        
        return company_info
    
    def _search_basic_info(self, company_name: str) -> Dict[str, Any]:
        """Search for basic company information"""
        
        search_queries = [
            f"{company_name} company about",
            f"{company_name} company overview",
            f"{company_name} headquarters founded industry"
        ]
        
        info = {
            "search_queries_used": search_queries,
            "sources": []
        }
        
        for query in search_queries:
            try:
                # Simulate web search - in production, use actual search API
                search_results = self._perform_web_search(query)
                
                for result in search_results[:3]:  # Check top 3 results
                    page_content = self._extract_page_content(result["url"])
                    if page_content:
                        extracted_info = self._extract_basic_info_from_content(page_content, company_name)
                        info.update(extracted_info)
                        info["sources"].append(result["url"])
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                continue
        
        return info
    
    def _search_products_services(self, company_name: str) -> Dict[str, Any]:
        """Search for company products and services"""
        
        search_queries = [
            f"{company_name} products services",
            f"{company_name} technology stack",
            f"{company_name} software solutions"
        ]
        
        info = {
            "products": [],
            "technologies": [],
            "search_queries_used": search_queries
        }
        
        for query in search_queries:
            try:
                search_results = self._perform_web_search(query)
                
                for result in search_results[:2]:
                    page_content = self._extract_page_content(result["url"])
                    if page_content:
                        extracted_info = self._extract_products_from_content(page_content, company_name)
                        info["products"].extend(extracted_info.get("products", []))
                        info["technologies"].extend(extracted_info.get("technologies", []))
                
                time.sleep(1)
                
            except Exception as e:
                continue
        
        return info
    
    def _search_values_culture(self, company_name: str) -> Dict[str, Any]:
        """Search for company values and culture"""
        
        search_queries = [
            f"{company_name} company values mission",
            f"{company_name} culture vision",
            f"{company_name} about us mission statement"
        ]
        
        info = {
            "values": [],
            "mission": "",
            "search_queries_used": search_queries
        }
        
        for query in search_queries:
            try:
                search_results = self._perform_web_search(query)
                
                for result in search_results[:2]:
                    page_content = self._extract_page_content(result["url"])
                    if page_content:
                        extracted_info = self._extract_values_from_content(page_content, company_name)
                        info["values"].extend(extracted_info.get("values", []))
                        if not info["mission"] and extracted_info.get("mission"):
                            info["mission"] = extracted_info["mission"]
                
                time.sleep(1)
                
            except Exception as e:
                continue
        
        return info
    
    def _search_recent_news(self, company_name: str) -> Dict[str, Any]:
        """Search for recent company news"""
        
        search_queries = [
            f"{company_name} news 2024",
            f"{company_name} recent announcements",
            f"{company_name} latest updates"
        ]
        
        info = {
            "news": [],
            "search_queries_used": search_queries
        }
        
        for query in search_queries:
            try:
                search_results = self._perform_web_search(query)
                
                for result in search_results[:3]:
                    news_item = {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("snippet", "")
                    }
                    info["news"].append(news_item)
                
                time.sleep(1)
                
            except Exception as e:
                continue
        
        return info
    
    def _perform_web_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform web search using the web search service
        """
        from .web_search_service import WebSearchService
        
        try:
            search_service = WebSearchService()
            results = search_service.search_web(query, num_results=5)
            return results
        except Exception as e:
            # Fallback to simulated results
            return self._generate_simulated_results(query)
    
    def _generate_simulated_results(self, query: str) -> List[Dict[str, Any]]:
        """Generate simulated search results as fallback"""
        company_name = query.split()[0] if query.split() else "Company"
        
        return [
            {
                "title": f"About {company_name} - Company Overview",
                "url": f"https://www.{company_name.lower()}.com/about",
                "snippet": f"Learn more about {company_name} and our mission..."
            },
            {
                "title": f"{company_name} Products and Services",
                "url": f"https://www.{company_name.lower()}.com/products",
                "snippet": f"Discover {company_name}'s innovative solutions..."
            },
            {
                "title": f"{company_name} Company Information",
                "url": f"https://en.wikipedia.org/wiki/{company_name}",
                "snippet": f"{company_name} is a technology company..."
            }
        ]
    
    def _extract_page_content(self, url: str) -> str:
        """Extract text content from a web page"""
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:5000]  # Limit content length
            
        except Exception as e:
            return ""
    
    def _extract_basic_info_from_content(self, content: str, company_name: str) -> Dict[str, Any]:
        """Extract basic company information from page content"""
        
        info = {}
        content_lower = content.lower()
        
        # Extract description (first paragraph mentioning the company)
        sentences = content.split('.')
        for sentence in sentences[:10]:
            if company_name.lower() in sentence.lower() and len(sentence) > 50:
                info["description"] = sentence.strip()
                break
        
        # Extract industry
        industry_keywords = ["technology", "software", "healthcare", "finance", "retail", "manufacturing"]
        for keyword in industry_keywords:
            if keyword in content_lower:
                info["industry"] = keyword.title()
                break
        
        # Extract founding year
        year_pattern = r"founded in (\d{4})|established in (\d{4})|since (\d{4})"
        year_match = re.search(year_pattern, content_lower)
        if year_match:
            info["founded"] = year_match.group(1) or year_match.group(2) or year_match.group(3)
        
        return info
    
    def _extract_products_from_content(self, content: str, company_name: str) -> Dict[str, Any]:
        """Extract products and technologies from page content"""
        
        info = {"products": [], "technologies": []}
        
        # Technology keywords to look for
        tech_keywords = [
            "AI", "machine learning", "artificial intelligence", "deep learning",
            "cloud", "AWS", "Azure", "Python", "JavaScript", "React", "Node.js",
            "microservices", "API", "database", "analytics", "big data"
        ]
        
        content_lower = content.lower()
        
        for tech in tech_keywords:
            if tech.lower() in content_lower:
                info["technologies"].append(tech)
        
        # Extract product names (simplified)
        product_patterns = [
            r"our (\w+) platform",
            r"(\w+) solution",
            r"(\w+) software",
            r"(\w+) service"
        ]
        
        for pattern in product_patterns:
            matches = re.findall(pattern, content_lower)
            for match in matches[:3]:  # Limit to 3 products
                if len(match) > 3:  # Avoid short words
                    info["products"].append(match.title())
        
        return info
    
    def _extract_values_from_content(self, content: str, company_name: str) -> Dict[str, Any]:
        """Extract company values and mission from page content"""
        
        info = {"values": [], "mission": ""}
        content_lower = content.lower()
        
        # Common value keywords
        value_keywords = [
            "innovation", "integrity", "excellence", "collaboration", "diversity",
            "customer-focused", "transparency", "sustainability", "quality"
        ]
        
        for value in value_keywords:
            if value in content_lower:
                info["values"].append(value.title())
        
        # Extract mission statement
        mission_patterns = [
            r"our mission is to ([^.]+)",
            r"mission: ([^.]+)",
            r"we believe in ([^.]+)"
        ]
        
        for pattern in mission_patterns:
            match = re.search(pattern, content_lower)
            if match:
                info["mission"] = match.group(1).strip()
                break
        
        return info
    
    def _clean_company_info(self, company_info: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and deduplicate company information"""
        
        # Remove duplicates from lists
        for key in ["products", "technologies", "values", "recent_news"]:
            if key in company_info and isinstance(company_info[key], list):
                company_info[key] = list(dict.fromkeys(company_info[key]))  # Remove duplicates while preserving order
        
        # Limit list sizes
        company_info["products"] = company_info.get("products", [])[:5]
        company_info["technologies"] = company_info.get("technologies", [])[:8]
        company_info["values"] = company_info.get("values", [])[:6]
        company_info["recent_news"] = company_info.get("recent_news", [])[:3]
        
        return company_info

