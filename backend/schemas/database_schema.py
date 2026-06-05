from typing import List, Optional, Literal
from pydantic import BaseModel
from backend.schemas.provenance import Provenance

class Column(BaseModel):
    name: str
    data_type: str
    is_primary: bool = False
    is_nullable: bool = True
    is_unique: bool = False

class ForeignKey(BaseModel):
    column_name: str
    referenced_table: str
    referenced_column: str

class Table(BaseModel):
    name: str
    columns: List[Column]
    foreign_keys: List[ForeignKey]
    indexes: List[str]
    provenance: Optional[Provenance] = None

class DatabaseSchema(BaseModel):
    tables: List[Table]
