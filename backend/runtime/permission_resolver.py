from typing import Dict, List
from backend.schemas.auth_schema import AuthSchema

class PermissionResolver:
    def resolve(self, auth_schema: AuthSchema) -> Dict[str, List[str]]:
        # Map: Role -> List of accessible routes
        # In a real app this uses RouteAccess or PageAccess
        role_map = {role.name: [] for role in auth_schema.roles}
        
        # Here we map pages to roles
        for access in auth_schema.page_access:
            # We assume route roughly matches page_name logic for simplicity
            route = f"/{access.page_name}"
            for role in access.allowed_roles:
                if role in role_map:
                    role_map[role].append(route)
                    
        return role_map
