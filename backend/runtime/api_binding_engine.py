from typing import Dict, List
from backend.schemas.api_schema import ApiSchema
from backend.schemas.runtime_application import RuntimeForm, RuntimeTable

class ApiBindingEngine:
    def bind(self, api_schema: ApiSchema, forms: List[RuntimeForm], tables: List[RuntimeTable]) -> Dict[str, str]:
        bindings = {}
        api_paths = {ep.path: ep.method for ep in api_schema.endpoints}
        
        # Heuristic binding for forms
        for form in forms:
            # e.g., create_contact_form -> POST /contacts
            # Simple heuristic mapping for simulation
            target = form.id.replace("_form", "").replace("create_", "").replace("update_", "").replace("manage_", "")
            endpoint = f"/{target}s"
            if endpoint in api_paths:
                bindings[form.id] = f"POST {endpoint}"
            elif f"/{target}" in api_paths:
                bindings[form.id] = f"POST /{target}"
            else:
                post_endpoints = [ep.path for ep in api_schema.endpoints if ep.method == "POST"]
                if post_endpoints:
                    bindings[form.id] = f"POST {post_endpoints[0]}"
                else:
                    bindings[form.id] = "POST /api_fallback"
            form.api_binding = bindings[form.id]
                
        # Heuristic binding for tables
        for table in tables:
            target = table.id.replace("_table", "")
            endpoint = f"/{target}"
            if endpoint in api_paths:
                bindings[table.id] = f"GET {endpoint}"
                table.api_binding = bindings[table.id]
                
        return bindings
