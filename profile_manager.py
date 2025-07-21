"""
Profile Manager for Cover Letter Generation System
Handles multiple user profiles with CRUD operations
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import uuid

class ProfileManager:
    """Manages user profiles for the cover letter generation system"""
    
    def __init__(self, profiles_dir: str = "profiles"):
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(exist_ok=True)
        self.profiles_index_file = self.profiles_dir / "profiles_index.json"
        self._ensure_index_file()
    
    def _ensure_index_file(self):
        """Ensure the profiles index file exists"""
        if not self.profiles_index_file.exists():
            # Initialize with ziyanxin profile as the first profile
            initial_index = {
                "profiles": {
                    "ziyanxin": {
                        "id": "ziyanxin",
                        "name": "Ethan Xin (Ziyan)",
                        "email": "ziyanxinbci@gmail.com",
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                        "is_default": True
                    }
                },
                "default_profile": "ziyanxin"
            }
            self._save_index(initial_index)
            
            # Create the ziyanxin profile file
            from user_profile import PROFILES
            self._save_profile_data("ziyanxin", PROFILES["ziyanxin"])
    
    def _load_index(self) -> Dict:
        """Load the profiles index"""
        try:
            with open(self.profiles_index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"profiles": {}, "default_profile": None}
    
    def _save_index(self, index_data: Dict):
        """Save the profiles index"""
        with open(self.profiles_index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    def _save_profile_data(self, profile_id: str, profile_data: Dict):
        """Save profile data to individual file"""
        profile_file = self.profiles_dir / f"{profile_id}.json"
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)
    
    def _load_profile_data(self, profile_id: str) -> Optional[Dict]:
        """Load profile data from individual file"""
        profile_file = self.profiles_dir / f"{profile_id}.json"
        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def create_profile(self, profile_data: Dict) -> str:
        """Create a new profile and return its ID"""
        # Generate unique profile ID
        profile_id = str(uuid.uuid4())[:8]
        
        # Ensure unique ID
        index = self._load_index()
        while profile_id in index["profiles"]:
            profile_id = str(uuid.uuid4())[:8]
        
        # Extract basic info for index
        resume_info = profile_data.get("RESUME_INFO", {})
        profile_meta = {
            "id": profile_id,
            "name": resume_info.get("name", "Unknown User"),
            "email": resume_info.get("email", ""),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "is_default": False
        }
        
        # Update index
        index["profiles"][profile_id] = profile_meta
        if not index.get("default_profile"):
            index["default_profile"] = profile_id
            profile_meta["is_default"] = True
        
        self._save_index(index)
        self._save_profile_data(profile_id, profile_data)
        
        return profile_id
    
    def get_profile(self, profile_id: str) -> Optional[Dict]:
        """Get a profile by ID"""
        return self._load_profile_data(profile_id)
    
    def update_profile(self, profile_id: str, profile_data: Dict) -> bool:
        """Update an existing profile"""
        index = self._load_index()
        if profile_id not in index["profiles"]:
            return False
        
        # Update metadata
        resume_info = profile_data.get("RESUME_INFO", {})
        index["profiles"][profile_id].update({
            "name": resume_info.get("name", index["profiles"][profile_id]["name"]),
            "email": resume_info.get("email", index["profiles"][profile_id]["email"]),
            "updated_at": datetime.now().isoformat()
        })
        
        self._save_index(index)
        self._save_profile_data(profile_id, profile_data)
        return True
    
    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile"""
        index = self._load_index()
        if profile_id not in index["profiles"]:
            return False
        
        # Don't allow deleting the default profile if it's the only one
        if len(index["profiles"]) == 1:
            return False
        
        # Remove from index
        del index["profiles"][profile_id]
        
        # Update default if necessary
        if index["default_profile"] == profile_id:
            # Set first available profile as default
            new_default = next(iter(index["profiles"].keys()))
            index["default_profile"] = new_default
            index["profiles"][new_default]["is_default"] = True
        
        self._save_index(index)
        
        # Remove profile file
        profile_file = self.profiles_dir / f"{profile_id}.json"
        if profile_file.exists():
            profile_file.unlink()
        
        return True
    
    def list_profiles(self) -> List[Dict]:
        """List all profiles with metadata"""
        index = self._load_index()
        return list(index["profiles"].values())
    
    def get_default_profile(self) -> Optional[str]:
        """Get the default profile ID"""
        index = self._load_index()
        return index.get("default_profile")
    
    def set_default_profile(self, profile_id: str) -> bool:
        """Set a profile as default"""
        index = self._load_index()
        if profile_id not in index["profiles"]:
            return False
        
        # Update old default
        old_default = index.get("default_profile")
        if old_default and old_default in index["profiles"]:
            index["profiles"][old_default]["is_default"] = False
        
        # Set new default
        index["default_profile"] = profile_id
        index["profiles"][profile_id]["is_default"] = True
        
        self._save_index(index)
        return True
    
    def get_profile_for_generation(self, profile_id: str) -> Optional[Dict]:
        """Get profile data formatted for cover letter generation"""
        profile_data = self.get_profile(profile_id)
        if not profile_data:
            return None
        
        return {
            "resume_info": profile_data.get("RESUME_INFO", {}),
            "project_descriptions": profile_data.get("PROJECT_DESCRIPTIONS", {}),
            "social_profiles": profile_data.get("SOCIAL_PROFILES", {})
        }

# Global instance
profile_manager = ProfileManager()

