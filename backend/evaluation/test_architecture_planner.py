import os
import json
from backend.schemas.intent_config import IntentConfig
from backend.pipeline.architecture_planner import ArchitecturePlanner
from backend.validators.architecture_validator import ArchitectureValidator

def test_architecture_planner():
    # Set to test mode for local unit tests without API key limits
    os.environ["TEST_MODE"] = "True"
    
    intent_data = {
        "app_type": "crm",
        "features": ["authentication", "contacts", "dashboard"],
        "roles": ["admin", "user"],
        "entities": ["contact", "user"],
        "business_requirements": ["role_based_access"],
        "confidence": 0.95,
        "assumptions": [],
        "missing_information": []
    }
    
    intent = IntentConfig(**intent_data)
    
    planner = ArchitecturePlanner()
    arch, metrics = planner.generate_architecture(intent)
    
    print("\n--- Architecture Hash ---")
    print(arch.architecture_hash)
    
    print("\n--- Metrics ---")
    print(json.dumps(metrics, indent=2))
    
    print("\n--- Generated Mermaid Diagram ---")
    print(planner.generate_mermaid_diagram(arch))

if __name__ == "__main__":
    test_architecture_planner()
