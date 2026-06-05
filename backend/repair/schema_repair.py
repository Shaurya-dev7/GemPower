import json
import time
from typing import List, Dict
from google import genai
from google.genai import types
from google.genai.errors import APIError
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from backend.schemas.architecture_config import ArchitectureConfig
from backend.schemas.schema_bundle import SchemaBundle
from backend.validators.schema_generator_validator import ValidationError

SCHEMA_REPAIR_PROMPT = """You are a Schema Repair Engine.
The generated {domain} schema failed validation.

Architecture Context:
{arch_json}

Validation Errors for {domain}:
{error_list}

Current Broken Schema:
{broken_schema_json}

Your task is to REGENERATE ONLY THE '{domain}' schema.
Fix the errors listed above.
Do not return the entire bundle. Return ONLY a JSON object representing the fixed '{domain}' schema.
Do not include markdown tags.
"""

class SchemaRepairEngine:
    def __init__(self):
        self.test_mode = os.getenv("TEST_MODE", "False").lower() in ("true", "1", "yes")
        if not self.test_mode:
            self.client = genai.Client()
            self.model_name = "gemini-2.5-flash"
        else:
            self.client = None
            self.model_name = "mock-model"

    def repair(self, arch: ArchitectureConfig, bundle: SchemaBundle, errors: List[ValidationError]) -> SchemaBundle:
        """
        Targeted Repair: Group errors by domain (database, api, ui, auth) and regenerate only the broken domains.
        """
        if not errors:
            return bundle
            
        domain_errors = {}
        for err in errors:
            domain_errors.setdefault(err.domain, []).append(err.message)
            
        bundle_dict = bundle.model_dump()
        
        for domain, error_msgs in domain_errors.items():
            if domain not in bundle_dict:
                continue
                
            print(f"    [Repair] Targeting domain '{domain}' due to {len(error_msgs)} errors...", flush=True)
            
            if self.test_mode:
                # Mock repair just returns empty or naive fix
                if domain == "database" and "Duplicate tables found." in error_msgs:
                    # fake a fix
                    bundle_dict["database"]["tables"] = [bundle_dict["database"]["tables"][0]]
                continue
                
            prompt = SCHEMA_REPAIR_PROMPT.format(
                domain=domain,
                arch_json=arch.model_dump_json(),
                error_list="\n".join([f"- {msg}" for msg in error_msgs]),
                broken_schema_json=json.dumps(bundle_dict[domain], indent=2)
            )
            
            repaired_section = self._call_with_backoff(prompt)
            try:
                if repaired_section.strip().startswith("```"):
                    lines = repaired_section.strip().split("\n")
                    if lines[0].startswith("```"): lines = lines[1:]
                    if lines[-1].startswith("```"): lines = lines[:-1]
                    repaired_section = "\n".join(lines).strip()
                    
                parsed_section = json.loads(repaired_section)
                bundle_dict[domain] = parsed_section
            except json.JSONDecodeError as e:
                print(f"    [Repair Warning] Failed to parse repaired JSON for {domain}: {e}", flush=True)
                
        return SchemaBundle(**bundle_dict)

    def _call_with_backoff(self, prompt: str) -> str:
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                return response.text
            except APIError as e:
                if e.code in (429, 503) and attempt < max_attempts - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise e
        return "{}"
