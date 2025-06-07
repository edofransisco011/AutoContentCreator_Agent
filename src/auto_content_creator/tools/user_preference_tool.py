import os
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel

class UserPreferenceTool(BaseTool):
    name: str = "User Preference Reader"
    description: str = "Reads the user's preferences from the knowledge base."
    args_schema: Type[BaseModel] = BaseModel

    def _run(self) -> str:
        # Construct the path relative to this file's location
        here = os.path.dirname(__file__)
        # Go up two levels to the project root, then into the knowledge folder
        knowledge_path = os.path.join(here, "..", "..", "..", "knowledge", "user_preference.txt")
        
        try:
            with open(knowledge_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "User preference file not found."
        except Exception as e:
            return f"An error occurred while reading the user preference file: {e}"