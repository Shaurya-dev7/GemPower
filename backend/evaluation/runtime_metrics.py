from pydantic import BaseModel

class RuntimeMetrics(BaseModel):
    page_count: int
    route_count: int
    form_count: int
    table_count: int
    render_success_rate: float
    runtime_validation_rate: float
