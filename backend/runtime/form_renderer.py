from typing import List
from backend.schemas.ui_schema import UiSchema
from backend.schemas.runtime_application import RuntimeForm

class FormRenderer:
    def render(self, ui_schema: UiSchema) -> List[RuntimeForm]:
        forms = []
        for page in ui_schema.pages:
            for comp in page.components:
                if comp.type == "form":
                    fields = [f.name for f in comp.form_fields]
                    # The binding will be mapped properly by the binding engine later
                    forms.append(RuntimeForm(
                        id=comp.id,
                        fields=fields,
                        api_binding="" 
                    ))
        return forms
