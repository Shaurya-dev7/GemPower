import os
import json
from backend.evaluation.evaluation_engine import EvaluationEngine

def main():
    # Force TEST_MODE so it runs instantly without hitting LLM rate limits for the demo
    os.environ["TEST_MODE"] = "True"
    
    prompt = "Build a CRM with contacts and subscriptions"
    print(f"\n==========================================")
    print(f"🚀 RUNNING END-TO-END DEMO")
    print(f"==========================================")
    print(f"Prompt: '{prompt}'\n")
    
    engine = EvaluationEngine()
    
    # Run the pipeline
    run_data = engine.run_pipeline(prompt)
    
    print("\n[1] INTENT EXTRACTION")
    print(f" - Success: {run_data.get('intent_success')}")
    print(f" - Latency: {run_data.get('intent_latency', 0):.2f}s")
    
    print("\n[2] ARCHITECTURE PLANNING")
    print(f" - Success: {run_data.get('arch_success')}")
    print(f" - Latency: {run_data.get('arch_latency', 0):.2f}s")
    print(f" - Hash: {run_data.get('architecture_hash')}")
    
    print("\n[3] SCHEMA GENERATION")
    print(f" - Success: {run_data.get('schema_success')}")
    print(f" - Latency: {run_data.get('schema_latency', 0):.2f}s")
    
    print("\n[4] GLOBAL VALIDATION")
    print(f" - Validation Score: {run_data.get('validation_score', 0)}/100")
    print(f" - Latency: {run_data.get('validation_latency', 0):.2f}s")
    
    print("\n[5] RUNTIME GENERATION")
    print(f" - Renderable: {run_data.get('runtime_render_success')}")
    print(f" - Binding Success: {run_data.get('runtime_binding_success')}")
    print(f" - Runtime Hash: {run_data.get('runtime_hash')}")
    
    print("\n[6] METRICS & SUMMARY")
    print(f" - Total Pipeline Latency: {run_data.get('total_latency', 0):.2f}s")
    print(f" - Total Repairs Triggered: {run_data.get('total_repairs', 0)}")
    print(f" - Overall Success: {run_data.get('overall_success')}")
    
    print("\n✅ Demo completed successfully!")
    print("==========================================\n")

if __name__ == "__main__":
    main()
