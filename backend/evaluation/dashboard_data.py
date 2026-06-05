from pydantic import BaseModel
from typing import Dict, Any

class StageTiming(BaseModel):
    intent_ms: float
    architecture_ms: float
    schema_ms: float
    validation_ms: float
    runtime_ms: float

class IntentMetrics(BaseModel):
    extraction_success_rate: float
    repair_rate: float
    avg_latency: float
    avg_confidence: float

class ArchitectureMetrics(BaseModel):
    generation_success_rate: float
    validation_pass_rate: float
    repair_rate: float

class SchemaMetrics(BaseModel):
    generation_success_rate: float
    repair_rate: float
    validation_pass_rate: float

class RuntimeMetrics(BaseModel):
    render_success_rate: float
    route_generation_success_rate: float
    binding_success_rate: float

class SystemMetrics(BaseModel):
    total_success_rate: float
    avg_pipeline_latency: float
    avg_llm_calls: float
    avg_repair_count: float
    avg_validation_score: float
    determinism_score: float

class CostAnalysis(BaseModel):
    total_tokens: int
    avg_tokens_per_request: float
    avg_llm_calls: float
    avg_latency: float
    success_rate: float

class ReliabilityReport(BaseModel):
    success_rate: float
    repair_success_rate: float
    validation_accuracy: float
    runtime_success_rate: float

class DashboardData(BaseModel):
    intent_metrics: IntentMetrics
    architecture_metrics: ArchitectureMetrics
    schema_metrics: SchemaMetrics
    runtime_metrics: RuntimeMetrics
    system_metrics: SystemMetrics
    cost_analysis: CostAnalysis
    reliability_report: ReliabilityReport
    avg_stage_timings: StageTiming
    
    def to_frontend_json(self) -> Dict[str, Any]:
        return self.model_dump()
