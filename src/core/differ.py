import os
import shutil
import difflib
from pathlib import Path
from typing import List, Optional
import pathspec

from .models import FileChange, FileAction
from .repository import Repository

class Differ:
    def __init__(self, repo: Repository):
        self.repo = repo
        self.root_path = repo.root_path
        self.state_path = repo.ai_path / "state"
        self.ignore_spec = self._load_gitignore()
        
    def _load_gitignore(self) -> pathspec.PathSpec:
        ignore_lines = [
            ".git/",
            ".ai-changelist/",
            "__pycache__/",
            "*.pyc",
            "venv/",
            ".venv/"
        ]
        
        gitignore_path = self.root_path / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, "r", encoding="utf-8") as f:
                ignore_lines.extend(f.readlines())
                
        return pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, ignore_lines)
        
    def is_ignored(self, path: Path) -> bool:
        try:
            rel_path = path.relative_to(self.root_path)
            # Ensure directories have trailing slashes for pathspec matching
            path_str = str(rel_path).replace("\\", "/")
            if path.is_dir() and not path_str.endswith("/"):
                path_str += "/"
            return self.ignore_spec.match_file(path_str)
        except ValueError:
            return True

    def get_tracked_files(self) -> List[Path]:
        tracked = []
        for root, dirs, files in os.walk(self.root_path):
            root_path = Path(root)
            
            # Filter ignored directories
            dirs[:] = [d for d in dirs if not self.is_ignored(root_path / d)]

            for file in files:
                file_path = root_path / file
                if not self.is_ignored(file_path):
                    tracked.append(file_path)
                    
        return tracked

    def snapshot_to_state(self, file_paths: List[Path]):
        """Copy current files into the shadow state directory."""
        if not self.state_path.exists():
            self.state_path.mkdir(parents=True, exist_ok=True)
            
        for path in file_paths:
            rel_path = path.relative_to(self.root_path)
            dest = self.state_path / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(path, dest)
            except Exception:
                pass # Skip files we can't read

    def get_status(self) -> List[FileChange]:
        """Compare current working directory against the shadow state."""
        changes = []
        current_files = self.get_tracked_files()
        
        state_files = set()
        if self.state_path.exists():
            for root, _, files in os.walk(self.state_path):
                r_path = Path(root)
                for f in files:
                    state_files.add(r_path / f)
                    
        # Check for modifications and creations
        for current_file in current_files:
            rel_path = current_file.relative_to(self.root_path)
            state_file = self.state_path / rel_path
            
            try:
                with open(current_file, "r", encoding="utf-8") as f:
                    curr_content = f.read()
            except UnicodeDecodeError:
                continue # Skip binary files
                
            if state_file.exists():
                try:
                    with open(state_file, "r", encoding="utf-8") as f:
                        state_content = f.read()
                except UnicodeDecodeError:
                    continue # Skip binary files
                    
                if curr_content != state_content:
                    diff = "\n".join(difflib.unified_diff(
                        state_content.splitlines(),
                        curr_content.splitlines(),
                        fromfile=f"a/{rel_path}",
                        tofile=f"b/{rel_path}",
                        lineterm=""
                    ))
                    changes.append(FileChange(
                        path=str(rel_path).replace("\\", "/"),
                        action=FileAction.MODIFY,
                        content_before=state_content,
                        content_after=curr_content,
                        diff=diff
                    ))
                state_files.remove(state_file)
            else:
                # CREATED file
                diff = "\n".join(difflib.unified_diff(
                    [],
                    curr_content.splitlines(),
                    fromfile="/dev/null",
                    tofile=f"b/{rel_path}",
                    lineterm=""
                ))
                changes.append(FileChange(
                    path=str(rel_path).replace("\\", "/"),
                    action=FileAction.CREATE,
                    content_before=None,
                    content_after=curr_content,
                    diff=diff
                ))

        # Check for deletions
        for state_file in state_files:
            rel_path = state_file.relative_to(self.state_path)
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state_content = f.read()
            except UnicodeDecodeError:
                continue # Skip binary
                
            diff = "\n".join(difflib.unified_diff(
                state_content.splitlines(),
                [],
                fromfile=f"a/{rel_path}",
                tofile="/dev/null",
                lineterm=""
            ))
            changes.append(FileChange(
                path=str(rel_path).replace("\\", "/"),
                action=FileAction.DELETE,
                content_before=state_content,
                content_after=None,
                diff=diff
            ))
            
        return changes
        
    def sync_state(self, changes: List[FileChange]):
        """Update the state directory based on the saved changes."""
        for change in changes:
            dest = self.state_path / change.path
            
            if change.action == FileAction.DELETE:
                if dest.exists():
                    dest.unlink()
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                if change.content_after is not None:
                    with open(dest, "w", encoding="utf-8") as f:
                        f.write(change.content_after)
