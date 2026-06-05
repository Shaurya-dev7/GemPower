from typing import List, Optional
from pydantic import BaseModel
from backend.schemas.provenance import Provenance

class Role(BaseModel):
    name: str
    description: str
    provenance: Optional[Provenance] = None

class RouteAccess(BaseModel):
    route: str
    allowed_roles: List[str]

class PageAccess(BaseModel):
    page_name: str
    allowed_roles: List[str]

class AuthSchema(BaseModel):
    roles: List[Role]
    route_access: List[RouteAccess]
    page_access: List[PageAccess]
