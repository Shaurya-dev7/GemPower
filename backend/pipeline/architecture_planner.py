import os
import json
import time
import hashlib
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import ValidationError

from backend.schemas.intent_config import IntentConfig
from backend.schemas.architecture_config import ArchitectureConfig
from backend.validators.architecture_validator import ArchitectureValidator
from backend.repair.architecture_repair import ArchitectureRepairEngine

ARCHITECTURE_SYSTEM_PROMPT = """You are an Architecture Planner for an AI compiler.
Your job is to transform the provided IntentConfig into a deterministic, robust ArchitectureConfig.
The output MUST be a valid JSON exactly matching the ArchitectureConfig schema:
{
  "modules": [{"name": "string", "description": "string"}],
  "entities": [{"name": "string", "module_affiliation": "string"}],
  "relationships": [{"source_entity": "string", "target_entity": "string", "type": "one_to_one|one_to_many|many_to_many", "description": "string"}],
  "user_flows": [{"name": "string", "steps": ["string"], "required_roles": ["string"]}],
  "permissions": [{"role": "string", "actions": ["string"]}],
  "system_components": [{"name": "string", "type": "service|database|gateway|queue|cache"}],
  "external_dependencies": [{"name": "string", "purpose": "string"}],
  "assumptions": ["string"],
  "confidence": float,
  "completeness_score": float,
  "ambiguity_score": float
}
Rules:
- No orphan modules or entities.
- Every feature extracted from Intent must generate at least 1 module, 1 entity, and 1 user flow.
- Every role listed in the Intent must have generated permissions. No role may exist without permissions.
- Do NOT include any Markdown formatting. Return raw JSON.
"""

# ---------------------------------------------------------------------------
# DOMAIN MODULE DEFINITIONS — business-aware defaults for each domain
# ---------------------------------------------------------------------------
DOMAIN_MODULES = {
    "crm": {
        "authentication": {"entity": "user",         "flow": "manage_authentication", "flow_steps": ["navigate to login", "enter credentials", "authenticate", "redirect to dashboard"]},
        "contacts":       {"entity": "contact",      "flow": "manage_contacts",       "flow_steps": ["open contacts list", "search or filter contacts", "view contact details", "add or edit contact"]},
        "subscriptions":  {"entity": "subscription", "flow": "manage_subscriptions",  "flow_steps": ["view subscription plans", "select plan", "enter payment details", "confirm subscription"]},
        "billing":        {"entity": "invoice",      "flow": "billing_dashboard",     "flow_steps": ["view billing overview", "generate invoice", "track payment status", "download receipt"]},
        "audit_logs":     {"entity": "audit_entry",  "flow": "manage_audit_logs",     "flow_steps": ["open audit log", "filter by date or action", "view event details", "export logs"]},
        "rbac":           {"entity": "role",         "flow": "manage_rbac",           "flow_steps": ["view roles list", "create or edit role", "assign permissions", "assign users to role"]},
        "sso":            {"entity": "sso_session",  "flow": "manage_sso",            "flow_steps": ["redirect to SSO provider", "authenticate externally", "receive token", "create session"]},
        "reporting":      {"entity": "report",       "flow": "manage_reporting",      "flow_steps": ["select report type", "configure filters", "generate report", "export or share"]},
        "workflows":      {"entity": "workflow",     "flow": "manage_workflows",      "flow_steps": ["open workflow editor", "add workflow steps", "configure triggers", "activate workflow"]},
        "dashboard":      {"entity": "dashboard_widget", "flow": "admin_dashboard",   "flow_steps": ["view KPI cards", "review recent activity", "check system health"]},
        "multi_tenancy":  {"entity": "tenant",       "flow": "manage_multi_tenancy",  "flow_steps": ["view tenant list", "create new tenant", "configure tenant settings", "manage tenant users"]},
    },
    "marketplace": {
        "profiles":    {"entity": "freelancer", "flow": "manage_profiles",     "flow_steps": ["browse freelancer profiles", "view skills and ratings", "contact freelancer"]},
        "projects":    {"entity": "project",    "flow": "manage_projects",     "flow_steps": ["browse available projects", "filter by category or budget", "view project details", "save project"]},
        "proposals":   {"entity": "proposal",   "flow": "manage_proposals",    "flow_steps": ["select project", "write cover letter", "set bid amount", "submit proposal"]},
        "billing":     {"entity": "invoice",    "flow": "billing_dashboard",   "flow_steps": ["view earnings", "generate invoice", "track payment status", "withdraw funds"]},
        "clients":     {"entity": "client",     "flow": "manage_clients",      "flow_steps": ["view posted projects", "review proposals", "hire freelancer", "release payment"]},
        "freelancers": {"entity": "freelancer", "flow": "manage_freelancers",  "flow_steps": ["browse freelancer profiles", "view skills and ratings", "contact freelancer"]},
        "messaging":   {"entity": "message",    "flow": "manage_messaging",    "flow_steps": ["open inbox", "select conversation", "send message", "attach files"]},
        "reviews":     {"entity": "review",     "flow": "manage_reviews",      "flow_steps": ["view completed projects", "write review", "rate freelancer", "submit feedback"]},
        "search":      {"entity": "search_index", "flow": "manage_search",     "flow_steps": ["enter search query", "apply filters", "view results", "open project"]},
        "dashboard":   {"entity": "dashboard_widget", "flow": "admin_dashboard", "flow_steps": ["view platform stats", "review recent activity", "manage disputes"]},
    },
    "school": {
        "student_roster":     {"entity": "student",    "flow": "manage_student_roster",     "flow_steps": ["view student list", "search by class or section", "add new student", "edit student details"]},
        "grading_sheets":     {"entity": "grade",      "flow": "manage_grading_sheets",     "flow_steps": ["select class and subject", "enter marks", "calculate grades", "publish report cards"]},
        "attendance":         {"entity": "attendance", "flow": "manage_attendance",         "flow_steps": ["select date and class", "mark attendance", "review absentees", "generate attendance report"]},
        "teacher_management": {"entity": "teacher",    "flow": "manage_teacher_management", "flow_steps": ["view teacher profiles", "assign classes", "manage schedules", "review performance"]},
        "parent_portal":      {"entity": "parent",     "flow": "manage_parent_portal",      "flow_steps": ["login as parent", "view child's grades", "check attendance", "communicate with teacher"]},
        "timetable":          {"entity": "timetable",  "flow": "manage_timetable",          "flow_steps": ["view weekly schedule", "assign periods", "manage substitutions"]},
        "examinations":       {"entity": "exam",       "flow": "manage_examinations",       "flow_steps": ["create exam schedule", "assign hall tickets", "enter results", "publish results"]},
        "dashboard":          {"entity": "dashboard_widget", "flow": "admin_dashboard", "flow_steps": ["view school stats", "review announcements", "check calendar"]},
    },
}

# ---------------------------------------------------------------------------
# DOMAIN RELATIONSHIPS — entity relationships per domain
# ---------------------------------------------------------------------------
DOMAIN_RELATIONSHIPS = {
    "crm": [
        {"source": "user",          "target": "contact",      "type": "one_to_many",  "desc": "user manages contacts"},
        {"source": "user",          "target": "subscription", "type": "one_to_many",  "desc": "user holds subscriptions"},
        {"source": "user",          "target": "invoice",      "type": "one_to_many",  "desc": "user receives invoices"},
        {"source": "tenant",        "target": "user",         "type": "one_to_many",  "desc": "tenant contains users"},
        {"source": "tenant",        "target": "contact",      "type": "one_to_many",  "desc": "tenant owns contacts"},
        {"source": "tenant",        "target": "subscription", "type": "one_to_many",  "desc": "tenant manages subscriptions"},
        {"source": "user",          "target": "audit_entry",  "type": "one_to_many",  "desc": "user generates audit entries"},
        {"source": "role",          "target": "user",         "type": "many_to_many", "desc": "roles assigned to users"},
        {"source": "workflow",      "target": "user",         "type": "many_to_many", "desc": "workflows assigned to users"},
    ],
    "marketplace": [
        {"source": "client",     "target": "project",    "type": "one_to_many",  "desc": "client posts projects"},
        {"source": "project",    "target": "proposal",   "type": "one_to_many",  "desc": "project receives proposals"},
        {"source": "freelancer", "target": "proposal",   "type": "one_to_many",  "desc": "freelancer submits proposals"},
        {"source": "client",     "target": "invoice",    "type": "one_to_many",  "desc": "client receives invoices"},
        {"source": "freelancer", "target": "review",     "type": "one_to_many",  "desc": "freelancer receives reviews"},
        {"source": "client",     "target": "review",     "type": "one_to_many",  "desc": "client writes reviews"},
    ],
    "school": [
        {"source": "student",  "target": "attendance", "type": "one_to_many", "desc": "student has attendance records"},
        {"source": "student",  "target": "grade",      "type": "one_to_many", "desc": "student receives grades"},
        {"source": "teacher",  "target": "grade",      "type": "one_to_many", "desc": "teacher assigns grades"},
        {"source": "parent",   "target": "student",    "type": "one_to_many", "desc": "parent has children"},
        {"source": "teacher",  "target": "timetable",  "type": "one_to_many", "desc": "teacher assigned to timetable"},
    ],
}


class ArchitecturePlanner:
    def __init__(self):
        self.test_mode = os.getenv("TEST_MODE", "False").lower() in ("true", "1", "yes")
        if not self.test_mode:
            self.client = genai.Client()
            self.model_name = "gemini-2.5-flash"
        else:
            self.client = None
            self.model_name = "mock-model"
            
        self.validator = ArchitectureValidator()
        self.repair_engine = ArchitectureRepairEngine()

    def generate_architecture(self, intent: IntentConfig, max_repairs: int = 2) -> tuple[ArchitectureConfig, dict]:
        """
        Flow: Prompt -> Gemini -> ArchitectureConfig -> Validator -> Repair -> Final Config
        Returns (ArchitectureConfig, metrics_dict)
        """
        start_time = time.time()
        
        if self.test_mode:
            # Simple mock for test mode
            arch = self._get_mock_architecture(intent)
            errors = self.validator.validate(intent, arch)
            metrics = {
                "latency": time.time() - start_time,
                "repair_count": 0,
                "validation_passed": len(errors) == 0
            }
            arch.architecture_hash = arch.compute_hash()
            return arch, metrics

        # Generate initial architecture
        prompt = f"{ARCHITECTURE_SYSTEM_PROMPT}\n\nIntentConfig:\n{intent.model_dump_json(indent=2)}"
        raw_json = self._call_with_backoff(prompt)
        
        try:
            parsed = self._parse_json(raw_json)
            arch = ArchitectureConfig(**parsed)
        except (json.JSONDecodeError, ValidationError) as e:
            # Fallback naive repair attempt if completely malformed
            raise RuntimeError(f"Initial architecture generation completely failed to parse: {e}")

        repair_count = 0
        validation_passed = False
        
        # Validation & Repair Loop
        for _ in range(max_repairs + 1):
            errors = self.validator.validate(intent, arch)
            if not errors:
                validation_passed = True
                break
                
            print(f"    [Validator] Found {len(errors)} errors. Triggering Repair Engine...", flush=True)
            arch = self.repair_engine.repair(intent, arch, errors)
            repair_count += 1
            
        arch.architecture_hash = arch.compute_hash()
        
        metrics = {
            "latency": time.time() - start_time,
            "repair_count": repair_count,
            "validation_passed": validation_passed
        }
        
        return arch, metrics
        
    def _parse_json(self, raw_str: str) -> dict:
        s = raw_str.strip()
        if s.startswith("```"):
            lines = s.split("\n")
            if lines[0].startswith("```"): lines = lines[1:]
            if lines[-1].startswith("```"): lines = lines[:-1]
            s = "\n".join(lines).strip()
        return json.loads(s)

    def _call_with_backoff(self, prompt: str) -> str:
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # Basic rate limiting sleep before call to avoid 5 RPM limit
                time.sleep(12.0)
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

    def generate_mermaid_diagram(self, arch: ArchitectureConfig) -> str:
        """
        Deterministically generates a Mermaid Architecture diagram directly from the Pydantic model.
        Zero token cost, highly deterministic.
        """
        mermaid = ["graph TD"]
        
        # 1. Group entities by module
        module_entities = {}
        for ent in arch.entities:
            module_entities.setdefault(ent.module_affiliation, []).append(ent.name)
            
        for mod in arch.modules:
            mod_label = mod.name.replace("_", " ").title()
            mermaid.append(f"    subgraph {mod.name}[\"{mod_label}\"]")
            for ent in module_entities.get(mod.name, []):
                ent_label = ent.replace("_", " ").title()
                mermaid.append(f"        {ent}[\"{ent_label}\"]")
            mermaid.append("    end")
            
        # 2. Add Relationships
        for rel in arch.relationships:
            if rel.type == "one_to_one": arrow = "---"
            elif rel.type == "one_to_many": arrow = "-->"
            else: arrow = "<-->"
            desc = rel.description.replace('"', "'")
            mermaid.append(f"    {rel.source_entity} {arrow}|\"{desc}\"| {rel.target_entity}")
            
        # 3. System Components mapped to Modules
        if arch.system_components:
            mermaid.append("    subgraph Infrastructure[\"Infrastructure\"]")
            for comp in arch.system_components:
                comp_label = comp.name.replace("_", " ").title()
                mermaid.append(f"        {comp.name}((\"{comp_label}\"))")
            mermaid.append("    end")
            
        return "\n".join(mermaid)

    def _get_mock_architecture(self, intent: IntentConfig) -> ArchitectureConfig:
        """Domain-aware architecture generation — no placeholder names, no padding loops."""
        app_type = intent.app_type.lower()
        domain_key = None
        if "crm" in app_type:
            domain_key = "crm"
        elif "marketplace" in app_type or "resource_sharing" in app_type:
            domain_key = "marketplace"
        elif "school" in app_type:
            domain_key = "school"

        modules = []
        entities = []
        user_flows = []
        permissions = []
        relationships = []
        seen_modules = set()
        seen_entities = set()

        domain_module_map = DOMAIN_MODULES.get(domain_key, {}) if domain_key else {}
        forbidden = set(getattr(intent, "forbidden_entities", []) or [])

        # 1. Generate from intent features using domain map
        for feature in intent.features:
            f_name = feature.replace(" ", "_").lower()
            mod_def = domain_module_map.get(f_name)

            if mod_def:
                # Domain-aware generation
                if f_name not in seen_modules:
                    modules.append({"name": f_name, "description": f"Module for {feature.replace('_', ' ')}"})
                    seen_modules.add(f_name)

                ent_name = mod_def["entity"]
                if ent_name not in seen_entities and ent_name not in forbidden:
                    entities.append({"name": ent_name, "module_affiliation": f_name})
                    seen_entities.add(ent_name)

                user_flows.append({
                    "name": mod_def["flow"],
                    "steps": mod_def["flow_steps"],
                    "required_roles": intent.roles
                })
            else:
                # Feature not in domain map — generate sensible names
                if f_name not in seen_modules:
                    modules.append({"name": f_name, "description": f"Module for {feature.replace('_', ' ')}"})
                    seen_modules.add(f_name)

                ent_name = f_name[:-1] if f_name.endswith('s') else f_name
                if ent_name not in seen_entities and ent_name not in forbidden:
                    entities.append({"name": ent_name, "module_affiliation": f_name})
                    seen_entities.add(ent_name)

                user_flows.append({
                    "name": f"manage_{f_name}",
                    "steps": [f"navigate to {f_name.replace('_', ' ')}", f"view {f_name.replace('_', ' ')} list", f"add or edit {f_name.replace('_', ' ')}"],
                    "required_roles": intent.roles
                })

        # 2. Generate from intent entities not yet covered
        for ent_name in intent.entities:
            if ent_name not in seen_entities and ent_name not in forbidden:
                # Find a parent module or create one
                parent_mod = ent_name + "s"
                if parent_mod not in seen_modules:
                    modules.append({"name": parent_mod, "description": f"Module for {ent_name.replace('_', ' ')} management"})
                    seen_modules.add(parent_mod)
                entities.append({"name": ent_name, "module_affiliation": parent_mod})
                seen_entities.add(ent_name)

        # 3. Generate permissions for every role
        for role in intent.roles:
            actions = []
            for f in intent.features:
                f_lower = f.replace(" ", "_").lower()
                actions.append(f"view_{f_lower}")
                if role in ["admin", "tenant_admin", "manager"]:
                    actions.extend([f"create_{f_lower}", f"edit_{f_lower}", f"delete_{f_lower}"])
            if role == "admin":
                actions.append("manage_system")
            permissions.append({"role": role, "actions": list(dict.fromkeys(actions))})

        # 4. Generate relationships from domain map
        if domain_key and domain_key in DOMAIN_RELATIONSHIPS:
            for rel in DOMAIN_RELATIONSHIPS[domain_key]:
                if rel["source"] in seen_entities and rel["target"] in seen_entities:
                    relationships.append({
                        "source_entity": rel["source"],
                        "target_entity": rel["target"],
                        "type": rel["type"],
                        "description": rel["desc"]
                    })

        # 5. Safety fallback if nothing was generated
        if not modules:
            modules = [{"name": "core", "description": "Core application logic"}]
            entities = [{"name": "user", "module_affiliation": "core"}]
            user_flows = [{"name": "login", "steps": ["enter credentials", "authenticate"], "required_roles": intent.roles}]

        # 6. System components based on features
        system_components = [{"name": "auth_service", "type": "service"}]
        if "billing" in seen_modules:
            system_components.append({"name": "payment_gateway", "type": "gateway"})
        if "sso" in seen_modules:
            system_components.append({"name": "sso_provider", "type": "service"})
        if domain_key:
            system_components.append({"name": "primary_database", "type": "database"})

        # 7. External dependencies
        external_deps = []
        if "billing" in seen_modules:
            external_deps.append({"name": "stripe", "purpose": "Payment processing"})
        if "sso" in seen_modules:
            external_deps.append({"name": "oauth_provider", "purpose": "Single sign-on authentication"})

        return ArchitectureConfig(
            modules=modules,
            entities=entities,
            relationships=relationships,
            user_flows=user_flows,
            permissions=permissions,
            system_components=system_components,
            external_dependencies=external_deps,
            assumptions=[],
            confidence=0.9,
            completeness_score=1.0,
            ambiguity_score=0.0
        )
