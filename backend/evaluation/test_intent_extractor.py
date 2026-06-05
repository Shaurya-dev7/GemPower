import sys
import os
import json
import time

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.pipeline.intent_extractor import IntentExtractor

def run_evaluation():
    extractor = IntentExtractor()
    
    # Load golden cases
    with open("backend/evaluation/golden_outputs.json", "r") as f:
        golden_data = json.load(f)
    golden_cases = {case["prompt"]: case["expected_app_type"] for case in golden_data["golden_cases"]}
        
    # We select a subset of 5 representative prompts to avoid hitting the 5 RPM rate limit (each prompt takes 2 LLM requests)
    eval_prompts = [
        "Build a CRM with login, contacts, dashboard, role-based access, and premium subscriptions.",
        "Create an e-commerce store with a shopping cart, product catalog, user reviews, and Stripe checkout.",
        "Build a marketplace for freelancers",
        "I need something for schools",
        "Build a marketplace but don't allow sellers"
    ]
    
    print("=== Intent Extraction Engine Test Suite (Rate-Limited Safe Run) ===\n", flush=True)
    
    success_count = 0
    repair_count = 0
    correct_intent_count = 0
    total_latency = 0.0
    
    for idx, prompt in enumerate(eval_prompts):
        print(f"Running [{idx+1}/{len(eval_prompts)}]: {prompt[:50]}...", flush=True)
        
        success = False
        attempts = 3
        while attempts > 0 and not success:
            try:
                # Sleep only when hitting actual APIs to avoid RPM limits
                if not extractor.test_mode:
                    time.sleep(26.0)
                
                config, repaired, latency = extractor.extract_intent(prompt)
                success_count += 1
                total_latency += latency
                if repaired:
                    repair_count += 1
                    
                # Intent Accuracy Check
                expected = golden_cases.get(prompt, "").lower()
                actual = config.app_type.lower()
                
                # Fuzzy match: check if expected matches or is substring of actual
                if expected in actual or actual in expected or any(word in actual for word in expected.split('_')):
                    correct_intent_count += 1
                    print(f"  -> Match! (Expected: {expected}, Actual: {config.app_type})", flush=True)
                else:
                    print(f"  -> Mismatch! (Expected: {expected}, Actual: {config.app_type})", flush=True)
                success = True
                    
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    print("  -> Hit rate limit (429). Backing off for 30 seconds...", flush=True)
                    time.sleep(30.0)
                    attempts -= 1
                else:
                    print(f"  -> FAILED: {e}", flush=True)
                    break
                    
    total_prompts = len(eval_prompts)
    success_rate = (success_count / total_prompts) * 100
    intent_accuracy = (correct_intent_count / success_count * 100) if success_count > 0 else 0
    repair_rate = (repair_count / total_prompts) * 100
    avg_latency = total_latency / success_count if success_count > 0 else 0
    
    print("\n=== METRICS ===")
    print(f"Extraction Success Rate: {success_rate:.2f}%")
    print(f"Intent Accuracy: {intent_accuracy:.2f}%")
    print(f"Repair Rate: {repair_rate:.2f}%")
    print(f"Average Latency: {avg_latency:.2f} seconds")

if __name__ == "__main__":
    run_evaluation()
