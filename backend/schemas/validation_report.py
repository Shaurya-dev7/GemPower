from typing import List
from pydantic import BaseModel, Field

class ValidationError(BaseModel):
    rule_id: str
    severity: str  # "HIGH", "MEDIUM", "LOW"
    section: str
    message: str
    repair_hint: str

class ImpactReport(BaseModel):
    affected_entities: List[str]
    affected_tables: List[str]
    affected_endpoints: List[str]
    affected_pages: List[str]

class ValidationReport(BaseModel):
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    failed_sections: List[str]
    validation_score: float = Field(..., ge=0.0, le=100.0)
