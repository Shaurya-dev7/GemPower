from typing import List
from backend.schemas.ui_schema import UiSchema
from backend.schemas.runtime_application import RuntimePage

class PageRenderer:
    def render(self, ui_schema: UiSchema) -> List[RuntimePage]:
        pages = []
        for p in ui_schema.pages:
            # Determine type based on components
            page_type = "mixed"
            if len(p.components) == 1:
                page_type = p.components[0].type
                
            comps = [c.id for c in p.components]
            pages.append(RuntimePage(
                route=p.route,
                name=p.name,
                page_type=page_type,
                renderable=True, # structural reachability ensures this is theoretically renderable
                components=comps
            ))
        return pages
