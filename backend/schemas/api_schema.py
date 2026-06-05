from typing import List, Dict, Any, Literal, Optional
from pydantic import BaseModel
from backend.schemas.provenance import Provenance

class Endpoint(BaseModel):
    path: str
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
    operation_id: str
    description: str
    request_schema: Dict[str, Any]
    response_schema: Dict[str, Any]
    validation_rules: List[str]
    provenance: Optional[Provenance] = None

class ApiSchema(BaseModel):
    endpoints: List[Endpoint]
