import hashlib
import json
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class Module(BaseModel):
    name: str = Field(..., description="Unique name of the module, e.g., 'auth', 'billing'")
    description: str

class Entity(BaseModel):
    name: str = Field(..., description="Entity name, typically singular, e.g., 'user', 'contact'")
    module_affiliation: str = Field(..., description="The module this entity belongs to")

class Relationship(BaseModel):
    source_entity: str
    target_entity: str
    type: Literal["one_to_one", "one_to_many", "many_to_many"]
    description: str = Field(..., description="e.g., 'user owns contact'")

class UserFlow(BaseModel):
    name: str = Field(..., description="e.g., 'login', 'create_contact'")
    steps: List[str]
    required_roles: List[str]

class Permission(BaseModel):
    role: str
    actions: List[str] = Field(..., description="e.g., ['create_user', 'delete_user']")

class SystemComponent(BaseModel):
    name: str = Field(..., description="e.g., 'authentication_service', 'api_gateway'")
    type: Literal["service", "database", "gateway", "queue", "cache"]

class ExternalDependency(BaseModel):
    name: str = Field(..., description="e.g., 'stripe', 'oauth_provider'")
    purpose: str

class ArchitectureConfig(BaseModel):
    modules: List[Module]
    entities: List[Entity]
    relationships: List[Relationship]
    user_flows: List[UserFlow]
    permissions: List[Permission]
    system_components: List[SystemComponent]
    external_dependencies: List[ExternalDependency]
    
    assumptions: List[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
    completeness_score: float = Field(..., ge=0.0, le=1.0)
    ambiguity_score: float = Field(..., ge=0.0, le=1.0)
    
    architecture_hash: Optional[str] = None
    
    def compute_hash(self) -> str:
        """
        Generates a deterministic hash of the core architecture components.
        Used for Caching, Version Tracking, and Diff Detection.
        """
        core_data = {
            "modules": sorted([m.name for m in self.modules]),
            "entities": sorted([e.name for e in self.entities]),
            "relationships": sorted([f"{r.source_entity}-{r.type}-{r.target_entity}" for r in self.relationships]),
            "flows": sorted([f.name for f in self.user_flows])
        }
        json_str = json.dumps(core_data, sort_keys=True)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
