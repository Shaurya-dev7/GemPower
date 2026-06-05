from typing import List
from backend.schemas.ui_schema import UiSchema
from backend.schemas.runtime_application import RuntimeRoute

class RouteRegistry:
    def register(self, ui_schema: UiSchema) -> List[RuntimeRoute]:
        routes = []
        seen = set()
        for page in ui_schema.pages:
            if page.route not in seen:
                routes.append(RuntimeRoute(path=page.route, component_id=f"page_{page.name}"))
                seen.add(page.route)
        return routes
