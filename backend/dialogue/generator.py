"""Hybrid Template/LLM Dialogue Generator."""

from typing import Dict, Any
from .schemas import DialogueTags, DialogueImportance

class DialogueGenerator:
    def __init__(self):
        # Pre-written templates for low importance interactions
        self.templates = {
            "char_halku_v1": {
                "greet": ["Arre bhaiya!", "Namaste sir!", "Aaiye na!"],
                "sell_product": ["Asli maal hai sir!", "Aapke liye special discount!", "Yeh dekhiye sir."]
            },
            "char_policeman_v1": {
                "greet": ["Oye!", "Kaha jaa raha hai?"],
                "sell_product": ["Ye sab kya hai?"] # Not usually selling, but fallback
            }
        }
        
    def generate(self, actor_id: str, tags: DialogueTags, profile: Dict[str, Any], intent: str) -> str:
        """Generates Dialogue using templates for LOW/MEDIUM or Mock LLM for HIGH/CRITICAL."""
        
        # 1. Template Engine
        if tags.importance in [DialogueImportance.LOW, DialogueImportance.MEDIUM]:
            actor_templates = self.templates.get(actor_id, {})
            # Map intent to a simpler key
            key = "greet" if "greet" in intent else "sell_product" if "sell_product" in intent else None
            
            if key and key in actor_templates:
                # In real app, random choice. For mock, just grab the first one.
                return actor_templates[key][0]

        # 2. LLM Generator (Mock)
        # In a real app, this would construct a prompt using the character's profile, relationship history, etc.
        print(f"--- [MOCK LLM API CALL] ---")
        print(f"Actor: {actor_id}")
        print(f"Goal: {tags.speech_goal}")
        print(f"Profile: {profile.get('speech_style', 'default')}")
        print(f"---------------------------")
        
        if "argue" in intent:
            if actor_id == "char_halku_v1":
                return "Arre sir meri kya galti hai isme?"
            elif actor_id == "char_policeman_v1":
                return "Chup kar! Kanoon ko sikhayega?"
                
        if "question" in intent:
            if actor_id == "char_policeman_v1":
                return "Oye Halku, sach sach bata kya chakkar hai ye?"
                
        # LLM fallback
        return "Aur bhai, sab theek?"
