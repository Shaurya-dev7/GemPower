import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.pipeline.intent_extractor import IntentExtractor

def run_evaluation():
    extractor = IntentExtractor()
    
    print("=== Intent Extraction Engine Test Suite ===\n", flush=True)
    
    # Run the 4 key scenarios explicitly
    key_scenarios = {
        "Easy": "Build a CRM with login, contacts, dashboard, role-based access, and premium subscriptions.",
        "Medium": "Build a marketplace for freelancers",
        "Hard": "I need something for schools",
        "Evil Test": "Build a marketplace but don't allow sellers"
    }
    
    print("--- 4 KEY SCENARIOS ---", flush=True)
    for level, prompt in key_scenarios.items():
        print(f"\n[{level}] Prompt: {prompt}", flush=True)
        try:
            config, repaired, latency = extractor.extract_intent(prompt)
            print(f"Confidence: {config.confidence}", flush=True)
            print(f"App Type: {config.app_type}", flush=True)
            print(f"Features: {config.features}", flush=True)
            print(f"Assumptions: {config.assumptions}", flush=True)
            print(f"Missing Info: {config.missing_information}", flush=True)
            if repaired:
                print(f"** Repaired **", flush=True)
        except Exception as e:
            print(f"FAILED: {e}", flush=True)
            
if __name__ == "__main__":
    run_evaluation()
