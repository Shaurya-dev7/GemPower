from typing import List
from backend.schemas.database_schema import DatabaseSchema
from backend.schemas.runtime_application import RuntimeTable

class TableRenderer:
    def render(self, db_schema: DatabaseSchema) -> List[RuntimeTable]:
        tables = []
        for t in db_schema.tables:
            cols = [c.name for c in t.columns]
            tables.append(RuntimeTable(
                id=f"{t.name}_table",
                columns=cols,
                api_binding=""
            ))
        return tables
