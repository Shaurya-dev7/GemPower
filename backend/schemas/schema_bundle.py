from pydantic import BaseModel
from backend.schemas.database_schema import DatabaseSchema
from backend.schemas.api_schema import ApiSchema
from backend.schemas.ui_schema import UiSchema
from backend.schemas.auth_schema import AuthSchema

class SchemaBundle(BaseModel):
    database: DatabaseSchema
    api: ApiSchema
    ui: UiSchema
    auth: AuthSchema
