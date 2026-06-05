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

from backend.schemas.intent_config import IntentConfig
from backend.schemas.architecture_config import ArchitectureConfig
from backend.validators.architecture_validator import ValidationError

ARCHITECTURE_REPAIR_PROMPT = """You are an Architecture Repair Engine.
The generated architecture configuration failed validation for specific sections.

Intent Requirements:
{intent_json}

Validation Errors:
{error_list}

Current Broken Section ({section_name}):
{broken_section_json}

Your task is to REGENERATE ONLY THE '{section_name}' section.
Fix the errors listed above.
Do not return the entire architecture. Return ONLY a JSON array/object representing the fixed '{section_name}'.
Do not include markdown tags.
"""

class ArchitectureRepairEngine:
    def __init__(self):
        self.test_mode = os.getenv("TEST_MODE", "False").lower() in ("true", "1", "yes")
        if not self.test_mode:
            self.client = genai.Client()
            self.model_name = "gemini-2.5-flash"
        else:
            self.client = None
            self.model_name = "mock-model"

    def repair(self, intent: IntentConfig, arch: ArchitectureConfig, errors: List[ValidationError]) -> ArchitectureConfig:
        """
        Targeted Repair: Group errors by section and query LLM to regenerate only the broken sections.
        """
        if not errors:
            return arch
            
        # Group errors by section
        sections_to_repair = {}
        for err in errors:
            sections_to_repair.setdefault(err.section, []).append(err.message)
            
        arch_dict = arch.model_dump()
        
        for section, error_msgs in sections_to_repair.items():
            if section not in arch_dict:
                continue # Skip scores/hashes for LLM repair
                
            print(f"    [Repair] Targeting section '{section}' due to {len(error_msgs)} errors...", flush=True)
            
            if self.test_mode:
                # Mock repair just returns an empty list or a naive fix depending on the field
                # In real test cases, we might mock this explicitly.
                if isinstance(arch_dict[section], list):
                    arch_dict[section] = [] 
                continue
                
            prompt = ARCHITECTURE_REPAIR_PROMPT.format(
                intent_json=intent.model_dump_json(),
                error_list="\n".join([f"- {msg}" for msg in error_msgs]),
                section_name=section,
                broken_section_json=json.dumps(arch_dict[section], indent=2)
            )
            
            # Call Gemini
            repaired_section = self._call_with_backoff(prompt)
            try:
                if repaired_section.strip().startswith("```"):
                    lines = repaired_section.strip().split("\n")
                    if lines[0].startswith("```"): lines = lines[1:]
                    if lines[-1].startswith("```"): lines = lines[:-1]
                    repaired_section = "\n".join(lines).strip()
                    
                parsed_section = json.loads(repaired_section)
                arch_dict[section] = parsed_section
            except json.JSONDecodeError as e:
                print(f"    [Repair Warning] Failed to parse repaired JSON for {section}: {e}", flush=True)
                
        # Reconstruct ArchitectureConfig with repaired sections
        return ArchitectureConfig(**arch_dict)
        
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
        return "[]"
