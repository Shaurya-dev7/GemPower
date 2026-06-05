from typing import List
from pydantic import BaseModel, Field

class IntentConfig(BaseModel):
    """
    Structured output extracted from user natural language prompt.
    """
    app_type: str = Field(..., description="The primary type of the application, e.g., crm, marketplace, saas")
    features: List[str] = Field(..., description="A list of core features extracted from the prompt")
    roles: List[str] = Field(..., description="User roles mentioned or implied")
    entities: List[str] = Field(..., description="Core data entities (e.g., contact, subscription, product)")
    business_requirements: List[str] = Field(..., description="Business logic rules or constraints")
    
    # Execution Awareness & Confidence
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0 on how well the prompt was understood")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made by the model to fill in vague details")
    missing_information: List[str] = Field(default_factory=list, description="Critical missing details that might require user clarification")
    
    # Negative Requirements
    forbidden_features: List[str] = Field(default_factory=list, description="Features explicitly excluded by the user")
    forbidden_entities: List[str] = Field(default_factory=list, description="Entities explicitly excluded by the user")
