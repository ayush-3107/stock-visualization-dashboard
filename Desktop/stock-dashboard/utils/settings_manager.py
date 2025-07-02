import json
import os
from typing import List

FAVOURITES_DIR = "user_favourites"

def ensure_favourites_dir():
    """Create favourites directory if it doesn't exist"""
    if not os.path.exists(FAVOURITES_DIR):
        os.makedirs(FAVOURITES_DIR)

def get_user_favourites_path(username: str) -> str:
    """Get the path to user's favourites file"""
    return os.path.join(FAVOURITES_DIR, f"{username}_favourites.json")

def load_user_favourites(username: str) -> List[str]:
    """Load user favourite stocks from file"""
    ensure_favourites_dir()
    favourites_path = get_user_favourites_path(username)
    
    if os.path.exists(favourites_path):
        try:
            with open(favourites_path, 'r') as f:
                favourites = json.load(f)
                return favourites if isinstance(favourites, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    return []

def save_user_favourites(username: str, favourites: List[str]) -> bool:
    """Save user favourite stocks to file"""
    ensure_favourites_dir()
    favourites_path = get_user_favourites_path(username)
    
    try:
        with open(favourites_path, 'w') as f:
            json.dump(favourites, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving favourites: {e}")
        return False
