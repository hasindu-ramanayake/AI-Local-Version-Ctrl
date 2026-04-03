import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class FileAction(str, Enum):
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"

class FileChange(BaseModel):
    path: str
    action: FileAction
    content_before: Optional[str] = None
    content_after: Optional[str] = None
    diff: str

class Changelist(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    prompt: Optional[str] = None
    branch: str = "main"
    parent_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    files_changed: List[FileChange] = Field(default_factory=list)
