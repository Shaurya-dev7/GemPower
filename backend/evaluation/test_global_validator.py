import json
import os
import copy
from backend.schemas.intent_config import IntentConfig
from backend.schemas.architecture_config import ArchitectureConfig, Entity, Relationship, UserFlow, Permission, Module
from backend.pipeline.schema_generator import SchemaGenerator
from backend.validators.global_validator import GlobalValidator

def test_global_validator():
    os.environ["TEST_MODE"] = "True"
    
    # 1. Setup Valid Base Pipeline
    intent = IntentConfig(
        app_type="crm",
        features=["contacts"],
        roles=["user"],
        entities=["Contact"],
        business_requirements=[],
        confidence=1.0,
        assumptions=[],
        missing_information=[]
    )
    
    arch = ArchitectureConfig(
        modules=[Module(name="core", description="core")],
        entities=[Entity(name="Contact", module_affiliation="core")],
        relationships=[],
        user_flows=[UserFlow(name="view_contacts", steps=[], required_roles=["user"])],
        permissions=[Permission(role="user", actions=["read"])],
        system_components=[], external_dependencies=[], assumptions=[], confidence=1.0, completeness_score=1.0, ambiguity_score=0.0
    )
    
    generator = SchemaGenerator()
    valid_bundle, _ = generator.generate_schemas(arch)
    
    validator = GlobalValidator()
    
    print("\n--- Testing Valid Pipeline ---")
    valid_report = validator.validate(intent, arch, valid_bundle)
    print(f"Score: {valid_report.validation_score}/100")
    print(f"Is Valid: {valid_report.is_valid}")
    if valid_report.errors:
        for err in valid_report.errors: print(f" - {err.message}")

    # 2. Setup Broken Pipeline (Mutate Bundle)
    print("\n--- Testing Broken Pipeline ---")
    broken_bundle = copy.deepcopy(valid_bundle)
    
    # Intentionally orphan an API (Delete table, keep API)
    broken_bundle.database.tables = []
    
    # Intentionally remove provenance
    broken_bundle.api.endpoints[0].provenance = None
    
    # Intentionally break runtime format
    broken_bundle.ui.pages[0].route = "invalid_route_no_slash"

    broken_report = validator.validate(intent, arch, broken_bundle)
    print(f"Score: {broken_report.validation_score}/100")
    print(f"Is Valid: {broken_report.is_valid}")
    for err in broken_report.errors:
        print(f"[{err.severity}] {err.rule_id} ({err.section}): {err.message}")
        
    print("\n--- Change Impact Analyzer ---")
    impact = validator.impact_analyzer.analyze_removal(valid_bundle, "Contact")
    print(json.dumps(impact.model_dump(), indent=2))

if __name__ == "__main__":
    test_global_validator()
