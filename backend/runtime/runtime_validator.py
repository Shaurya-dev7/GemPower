from typing import List
from dataclasses import dataclass
from backend.schemas.runtime_application import RuntimeApplication

@dataclass
class RuntimeValidationError:
    component: str
    message: str

class RuntimeValidator:
    def validate(self, app: RuntimeApplication) -> List[RuntimeValidationError]:
        errors = []
        
        # 1. Renderable Pages Check
        for page in app.pages:
            if not page.renderable:
                errors.append(RuntimeValidationError(f"Page:{page.name}", "Page is not marked as renderable."))
                
        # 2. Valid Navigation Check
        valid_routes = [r.path for r in app.routes]
        for nav in app.navigation:
            if nav not in valid_routes:
                errors.append(RuntimeValidationError(f"Navigation:{nav}", "Navigation points to non-existent route."))
                
        # 3. Valid Bindings Check
        for form in app.forms:
            if not form.api_binding:
                errors.append(RuntimeValidationError(f"Form:{form.id}", "Form has no API binding."))
                
        # 4. Valid Routes Check
        if len(valid_routes) != len(set(valid_routes)):
            errors.append(RuntimeValidationError("Routes", "Duplicate routes detected in application."))
            
        return errors
