import os
import copy
from backend.schemas.intent_config import IntentConfig
from backend.schemas.architecture_config import ArchitectureConfig, Entity, Relationship, UserFlow, Permission, Module
from backend.pipeline.schema_generator import SchemaGenerator
from backend.runtime.runtime_engine import RuntimeEngine
from backend.runtime.runtime_validator import RuntimeValidator
from backend.runtime.runtime_simulator import RuntimeSimulator
from backend.evaluation.runtime_metrics import RuntimeMetrics

def test_runtime_engine():
    os.environ["TEST_MODE"] = "True"
    
    # 1. Base config
    arch = ArchitectureConfig(
        modules=[Module(name="core", description="core")],
        entities=[Entity(name="Contact", module_affiliation="core")],
        relationships=[],
        user_flows=[UserFlow(name="create_contact", steps=[], required_roles=["user"])],
        permissions=[Permission(role="user", actions=["read"])],
        system_components=[], external_dependencies=[], assumptions=[], confidence=1.0, completeness_score=1.0, ambiguity_score=0.0
    )
    generator = SchemaGenerator()
    valid_bundle, _ = generator.generate_schemas(arch)
    
    # 2. Runtime Engine
    engine = RuntimeEngine()
    validator = RuntimeValidator()
    simulator = RuntimeSimulator()
    
    valid_app = engine.compile(valid_bundle)
    valid_errors = validator.validate(valid_app)
    
    print("\n--- Valid Runtime App ---")
    print(f"Runtime Hash: {valid_app.runtime_hash}")
    print(f"Validation Errors: {len(valid_errors)}")
    
    metrics = RuntimeMetrics(
        page_count=len(valid_app.pages),
        route_count=len(valid_app.routes),
        form_count=len(valid_app.forms),
        table_count=len(valid_app.tables),
        render_success_rate=1.0 if not valid_errors else 0.0,
        runtime_validation_rate=1.0
    )
    print(metrics.model_dump_json(indent=2))
    
    simulator.simulate(valid_app, "d:/Projects/Intern_work/runtime_preview.html")
    print("Generated runtime_preview.html")

    # 3. Intentionally broken app (Simulate a broken schema generating an unrenderable app)
    print("\n--- Broken Runtime App ---")
    broken_app = copy.deepcopy(valid_app)
    # Break an API binding explicitly
    if broken_app.forms:
        broken_app.forms[0].api_binding = ""
    broken_errors = validator.validate(broken_app)
    print(f"Validation Errors: {len(broken_errors)}")
    for err in broken_errors:
        print(f" - [{err.component}]: {err.message}")

if __name__ == "__main__":
    test_runtime_engine()
