import os
import json
from pathlib import Path
from typing import Optional, List
from .models import Changelist

DIR_NAME = ".ai-changelist"

class Repository:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.ai_path = self.root_path / DIR_NAME
        self.changelists_path = self.ai_path / "changelists"
        self.head_path = self.ai_path / "HEAD.json"
        
    @property
    def is_initialized(self) -> bool:
        return self.ai_path.exists() and self.changelists_path.exists()

    def initialize(self):
        if self.is_initialized:
            return False
            
        self.ai_path.mkdir(exist_ok=True)
        self.changelists_path.mkdir(exist_ok=True)
        
        # Initialize HEAD.json
        self.update_head(branch="main", current_id=None)
        
        # Append to .gitignore
        self._append_to_gitignore()
        return True
        
    def _append_to_gitignore(self):
        gitignore_path = self.root_path / ".gitignore"
        ignore_entry = f"\n# AI Changelist CLI\n{DIR_NAME}/\n"
        
        if gitignore_path.exists():
            content = gitignore_path.read_text(encoding="utf-8")
            if f"{DIR_NAME}/" not in content and DIR_NAME not in content:
                with open(gitignore_path, "a", encoding="utf-8") as f:
                    f.write(ignore_entry)
        else:
            with open(gitignore_path, "w", encoding="utf-8") as f:
                f.write(ignore_entry)
                
    def update_head(self, branch: str, current_id: Optional[str] = None):
        head_data = {"branch": branch, "head_id": current_id}
        with open(self.head_path, "w", encoding="utf-8") as f:
            json.dump(head_data, f, indent=2)
            
    def get_head(self) -> dict:
        if not self.head_path.exists():
            return {"branch": "main", "head_id": None}
        with open(self.head_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    def get_current_branch(self) -> str:
        return self.get_head().get("branch", "main")
        
    def get_head_id(self) -> Optional[str]:
        return self.get_head().get("head_id")

    def save_changelist(self, cl: Changelist):
        cl_path = self.changelists_path / f"{cl.id}.json"
        with open(cl_path, "w", encoding="utf-8") as f:
            f.write(cl.model_dump_json(indent=2))
            
    def get_changelist(self, cl_id: str) -> Optional[Changelist]:
        cl_path = self.changelists_path / f"{cl_id}.json"
        if not cl_path.exists():
            return None
        with open(cl_path, "r", encoding="utf-8") as f:
            return Changelist.model_validate_json(f.read())
            
    def get_all_changelists(self) -> List[Changelist]:
        changelists = []
        if not self.changelists_path.exists():
            return changelists
            
        for file_path in self.changelists_path.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                changelists.append(Changelist.model_validate_json(f.read()))
        
        # Sort by timestamp (oldest first or newest first, let's do newest first)
        changelists.sort(key=lambda x: x.timestamp, reverse=True)
        return changelists
        
    def delete_changelist(self, cl_id: str) -> bool:
        cl_path = self.changelists_path / f"{cl_id}.json"
        if cl_path.exists():
            cl_path.unlink()
            return True
        return False
