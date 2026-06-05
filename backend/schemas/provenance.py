from typing import Optional
from pydantic import BaseModel

class Provenance(BaseModel):
    source_type: str  # e.g., 'entity', 'module', 'flow', 'role'
    source_id: str    # e.g., 'Contact', 'core', 'login', 'user'
    architecture_hash: Optional[str] = None
