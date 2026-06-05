from typing import List
from backend.schemas.ui_schema import UiSchema

class NavigationBuilder:
    def build(self, ui_schema: UiSchema) -> List[str]:
        # Ensures every route declared in navigation exists in pages
        valid_routes = [p.route for p in ui_schema.pages]
        nav = []
        for route in ui_schema.navigation:
            if route in valid_routes:
                nav.append(route)
        return nav
