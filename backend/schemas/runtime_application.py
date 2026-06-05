from typing import List, Dict, Any, Optional
import hashlib
import json
from pydantic import BaseModel

class RuntimeRoute(BaseModel):
    path: str
    component_id: str

class RuntimeForm(BaseModel):
    id: str
    fields: List[str]
    api_binding: str # e.g. "POST /contacts"

class RuntimeTable(BaseModel):
    id: str
    columns: List[str]
    api_binding: str # e.g. "GET /contacts"

class RuntimePage(BaseModel):
    route: str
    name: str
    page_type: str # "form", "table", "dashboard", "mixed"
    renderable: bool
    components: List[str]

class RuntimeApplication(BaseModel):
    pages: List[RuntimePage]
    navigation: List[str] # routes
    routes: List[RuntimeRoute]
    forms: List[RuntimeForm]
    tables: List[RuntimeTable]
    permissions: Dict[str, List[str]] # role -> list of routes
    api_bindings: Dict[str, str] # component_id -> endpoint
    runtime_hash: Optional[str] = None
    
    def compute_hash(self) -> str:
        """
        Generates a deterministic hash of the core runtime components.
        """
        core_data = {
            "pages": sorted([p.name for p in self.pages]),
            "routes": sorted([r.path for r in self.routes]),
            "forms": sorted([f.id for f in self.forms]),
            "tables": sorted([t.id for t in self.tables]),
            "bindings": sorted([f"{k}:{v}" for k, v in self.api_bindings.items()])
        }
        json_str = json.dumps(core_data, sort_keys=True)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
