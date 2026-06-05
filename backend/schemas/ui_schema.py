from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.schemas.provenance import Provenance

class FormField(BaseModel):
    name: str
    type: str
    required: bool

class UIComponent(BaseModel):
    id: str
    type: str
    props: Dict[str, Any]
    form_fields: List[FormField] = []

class Page(BaseModel):
    name: str
    route: str
    layout: str
    components: List[UIComponent]
    provenance: Optional[Provenance] = None

class UiSchema(BaseModel):
    pages: List[Page]
    navigation: List[str]
