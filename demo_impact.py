import os
import json
from backend.evaluation.evaluation_engine import EvaluationEngine
from backend.validators.change_impact_analyzer import ChangeImpactAnalyzer

def print_section(title, data=None):
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")
    if data:
        if isinstance(data, list):
            for item in data:
                print(f" - {item}")
        else:
            print(data)

def main():
    # Force TEST_MODE so it runs instantly without hitting LLM rate limits for the demo
    os.environ["TEST_MODE"] = "True"
    
    engine = EvaluationEngine()
    analyzer = ChangeImpactAnalyzer()
    
    prompt = "Build a CRM with login, contacts, dashboard and subscriptions"
    print_section("1. SIMULATING INITIAL STATE (BEFORE)")
    print(f"Prompt: '{prompt}'")
    
    # We just want the bundle to analyze it
    run_data = engine.run_pipeline(prompt)
    
    if not run_data.get("schema_success"):
        print("Failed to generate initial schema. Cannot demo impact.")
        return
        
    print(f"✅ Generated Initial Architecture with {run_data['summary']['modules']} modules and {run_data['summary']['entities']} entities.")
    print(f"✅ Generated Initial Schema with {run_data['summary']['pages']} pages and {run_data['summary']['api_endpoints']} API endpoints.")
    
    print_section("2. SIMULATING REQUIREMENT CHANGE (AFTER)")
    print("User Request: 'Remove subscriptions'")
    print("Target Entity to Remove: 'subscription'")
    
    print_section("3. IMPACT SUMMARY")
    
    # Let's get the schema bundle by calling the engine's internal methods directly to get the object
    intent, _, _ = engine.intent_extractor.extract_intent(prompt)
    arch, _ = engine.arch_planner.generate_architecture(intent)
    bundle, _ = engine.schema_gen.generate_schemas(arch)
    
    impact = analyzer.analyze_removal(bundle, "subscription")
    
    print("\n🚨 The following components will be DELETED or MODIFIED:\n")
    print("Entities Affected:")
    for ent in impact.affected_entities:
        print(f"  - {ent}")
        
    print("\nDatabase Tables Affected:")
    for table in impact.affected_tables:
        print(f"  - {table}")
        
    print("\nAPI Endpoints Affected:")
    for api in impact.affected_endpoints:
        print(f"  - {api}")
        
    print("\nUI Pages/Flows Affected:")
    for page in impact.affected_pages:
        print(f"  - {page}")
        
    print("\nPermissions Affected:")
    print("  - Any role with 'view_subscriptions' or 'manage_subscriptions' will have these permissions revoked.")
        
    print("\n✅ Requirement change impact analysis complete.")

if __name__ == "__main__":
    main()
