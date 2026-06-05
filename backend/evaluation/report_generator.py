import json
import os
from typing import Dict, Any

class ReportGenerator:
    def __init__(self, output_dir: str = "backend/evaluation"):
        self.output_dir = output_dir
        
    def generate(self, dashboard_data: Dict[str, Any]):
        json_path = os.path.join(self.output_dir, "evaluation_report.json")
        md_path = os.path.join(self.output_dir, "evaluation_report.md")
        
        # Write JSON
        with open(json_path, "w") as f:
            json.dump(dashboard_data, f, indent=2)
            
        # Write Markdown
        md = ["# AI Compiler Pipeline - Evaluation Report\n"]
        
        sys = dashboard_data["system_metrics"]
        md.append("## 1. System Overview")
        md.append(f"- **Total Success Rate:** {sys['total_success_rate']}%")
        md.append(f"- **Average Pipeline Latency:** {sys['avg_pipeline_latency']:.2f}s")
        md.append(f"- **Average LLM Calls:** {sys['avg_llm_calls']:.1f}")
        md.append(f"- **Determinism Score:** {sys['determinism_score']}%")
        
        rel = dashboard_data["reliability_report"]
        md.append("\n## 2. Reliability & Quality")
        md.append(f"- **Validation Accuracy:** {rel['validation_accuracy']}%")
        md.append(f"- **Repair Success Rate:** {rel['repair_success_rate']}%")
        md.append(f"- **Runtime Success Rate:** {rel['runtime_success_rate']}%")
        
        cost = dashboard_data["cost_analysis"]
        md.append("\n## 3. Cost Analysis")
        md.append(f"- **Total Tokens Consumed:** {cost['total_tokens']}")
        md.append(f"- **Average Tokens / Request:** {cost['avg_tokens_per_request']}")
        
        time = dashboard_data["avg_stage_timings"]
        md.append("\n## 4. Pipeline Stage Timings (ms)")
        md.append(f"- **Intent:** {time['intent_ms']:.1f} ms")
        md.append(f"- **Architecture:** {time['architecture_ms']:.1f} ms")
        md.append(f"- **Schema Generator:** {time['schema_ms']:.1f} ms")
        md.append(f"- **Validation:** {time['validation_ms']:.1f} ms")
        md.append(f"- **Runtime Generation:** {time['runtime_ms']:.1f} ms")
        
        with open(md_path, "w") as f:
            f.write("\n".join(md))
            
        print(f"Reports generated: {json_path}, {md_path}")
