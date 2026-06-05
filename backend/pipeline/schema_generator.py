import os
import json
import time
from typing import Dict, Any, Tuple
from google import genai
from google.genai import types
from google.genai.errors import APIError
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from backend.schemas.architecture_config import ArchitectureConfig
from backend.schemas.database_schema import DatabaseSchema, Table, Column, ForeignKey
from backend.schemas.api_schema import ApiSchema, Endpoint
from backend.schemas.ui_schema import UiSchema, Page, UIComponent, FormField
from backend.schemas.auth_schema import AuthSchema, Role, RouteAccess, PageAccess
from backend.schemas.schema_bundle import SchemaBundle
from backend.schemas.provenance import Provenance
from backend.validators.schema_generator_validator import SchemaValidator
from backend.repair.schema_repair import SchemaRepairEngine

ENRICHMENT_PROMPT = """You are a Schema Enrichment Engine.
I have deterministically scaffolded the structural schema based on the architecture. 
Your task is to ENRICH the schema by filling in missing business logic, specific fields, and column types.

Architecture Context:
{arch_json}

Base Structural Schema:
{base_schema_json}

INSTRUCTIONS:
1. For Database: Add appropriate business columns (e.g., 'email', 'status') with standard SQL data types. Do NOT remove the structural primary/foreign keys.
2. For API: Populate the request_schema and response_schema dicts for each endpoint based on the new DB columns. Add validation rules.
3. For UI: Add specific FormFields to the UI components corresponding to the API schemas.
4. For Auth: Do not change structural roles. You may adjust route access if complex workflows demand it.

Return ONLY the enriched JSON matching the SchemaBundle structure. Do not include markdown tags.
"""

# ---------------------------------------------------------------------------
# COMPREHENSIVE DOMAIN FIELD MAPS
# ---------------------------------------------------------------------------
DOMAIN_FIELDS = {
    # CRM entities
    "contact": [
        ("full_name", "string", True),
        ("email", "string", True),
        ("phone", "string", False),
        ("company", "string", False),
        ("lead_source", "string", False),
        ("status", "string", True),
    ],
    "subscription": [
        ("plan_name", "string", True),
        ("billing_cycle", "string", True),
        ("amount", "decimal", True),
        ("start_date", "date", True),
        ("expiry_date", "date", False),
        ("status", "string", True),
    ],
    "user": [
        ("first_name", "string", True),
        ("last_name", "string", True),
        ("email", "string", True),
        ("role", "string", True),
        ("last_login", "datetime", False),
    ],
    "invoice": [
        ("invoice_number", "string", True),
        ("customer_id", "uuid", True),
        ("amount", "decimal", True),
        ("currency", "string", True),
        ("due_date", "date", True),
        ("payment_status", "string", True),
    ],
    "payment": [
        ("invoice_id", "uuid", True),
        ("amount", "decimal", True),
        ("method", "string", True),
        ("transaction_id", "string", False),
        ("paid_at", "datetime", True),
        ("status", "string", True),
    ],
    "audit_entry": [
        ("action", "string", True),
        ("performed_by", "uuid", True),
        ("resource_type", "string", True),
        ("resource_id", "string", True),
        ("timestamp", "datetime", True),
        ("ip_address", "string", False),
    ],
    "role": [
        ("role_name", "string", True),
        ("description", "text", False),
        ("is_system_role", "boolean", True),
        ("priority", "integer", False),
    ],
    "permission": [
        ("role_id", "uuid", True),
        ("resource", "string", True),
        ("action", "string", True),
        ("is_allowed", "boolean", True),
    ],
    "sso_session": [
        ("user_id", "uuid", True),
        ("provider", "string", True),
        ("access_token", "string", True),
        ("refresh_token", "string", False),
        ("expires_at", "datetime", True),
    ],
    "report": [
        ("report_name", "string", True),
        ("report_type", "string", True),
        ("generated_by", "uuid", True),
        ("parameters", "json", False),
        ("output_url", "string", False),
        ("generated_at", "datetime", True),
    ],
    "workflow": [
        ("workflow_name", "string", True),
        ("trigger_event", "string", True),
        ("steps", "json", True),
        ("is_active", "boolean", True),
        ("created_by", "uuid", True),
    ],
    "tenant": [
        ("tenant_name", "string", True),
        ("domain", "string", True),
        ("plan", "string", True),
        ("is_active", "boolean", True),
        ("owner_id", "uuid", True),
    ],
    "dashboard_widget": [
        ("widget_name", "string", True),
        ("widget_type", "string", True),
        ("data_source", "string", True),
        ("position", "integer", False),
        ("config", "json", False),
    ],

    # Marketplace entities
    "freelancer": [
        ("full_name", "string", True),
        ("skills", "text", True),
        ("hourly_rate", "decimal", True),
        ("experience_years", "integer", True),
        ("rating", "decimal", False),
    ],
    "project": [
        ("title", "string", True),
        ("budget", "decimal", True),
        ("deadline", "date", True),
        ("status", "string", True),
        ("client_id", "uuid", True),
    ],
    "proposal": [
        ("project_id", "uuid", True),
        ("freelancer_id", "uuid", True),
        ("bid_amount", "decimal", True),
        ("cover_letter", "text", True),
        ("status", "string", True),
    ],
    "client": [
        ("company_name", "string", True),
        ("contact_person", "string", True),
        ("email", "string", True),
        ("phone", "string", False),
        ("industry", "string", False),
    ],
    "message": [
        ("sender_id", "uuid", True),
        ("receiver_id", "uuid", True),
        ("content", "text", True),
        ("sent_at", "datetime", True),
        ("is_read", "boolean", True),
    ],
    "review": [
        ("reviewer_id", "uuid", True),
        ("reviewee_id", "uuid", True),
        ("project_id", "uuid", True),
        ("rating", "integer", True),
        ("comment", "text", False),
    ],
    "search_index": [
        ("entity_type", "string", True),
        ("entity_id", "uuid", True),
        ("content", "text", True),
        ("keywords", "text", False),
    ],

    # School entities
    "student": [
        ("roll_number", "string", True),
        ("student_name", "string", True),
        ("class_name", "string", True),
        ("section", "string", True),
        ("date_of_birth", "date", True),
        ("guardian_name", "string", True),
    ],
    "attendance": [
        ("student_id", "uuid", True),
        ("date", "date", True),
        ("status", "string", True),
        ("remarks", "text", False),
    ],
    "grade": [
        ("student_id", "uuid", True),
        ("subject", "string", True),
        ("marks", "decimal", True),
        ("grade", "string", True),
        ("teacher_id", "uuid", True),
    ],
    "teacher": [
        ("employee_id", "string", True),
        ("teacher_name", "string", True),
        ("department", "string", True),
        ("qualification", "string", True),
        ("joining_date", "date", True),
    ],
    "parent": [
        ("parent_name", "string", True),
        ("phone", "string", True),
        ("email", "string", True),
        ("relation", "string", True),
    ],
    "timetable": [
        ("class_name", "string", True),
        ("day_of_week", "string", True),
        ("period", "integer", True),
        ("subject", "string", True),
        ("teacher_id", "uuid", True),
    ],
    "exam": [
        ("exam_name", "string", True),
        ("subject", "string", True),
        ("exam_date", "date", True),
        ("max_marks", "integer", True),
        ("class_name", "string", True),
    ],
}


class SchemaGenerator:
    def __init__(self):
        self.test_mode = os.getenv("TEST_MODE", "False").lower() in ("true", "1", "yes")
        if not self.test_mode:
            self.client = genai.Client()
            self.model_name = "gemini-2.5-flash"
        else:
            self.client = None
            self.model_name = "mock-model"
            
        self.validator = SchemaValidator()
        self.repair_engine = SchemaRepairEngine()

    def generate_schemas(self, arch: ArchitectureConfig, max_repairs: int = 2) -> Tuple[SchemaBundle, Dict[str, Any]]:
        start_time = time.time()
        
        # 1. Deterministic Scaffolding
        base_bundle = self._deterministic_scaffold(arch)
        
        if self.test_mode:
            bundle = base_bundle
            errors = self.validator.validate(arch, bundle)
            metrics = {
                "latency": time.time() - start_time,
                "repair_count": 0,
                "validation_passed": len(errors) == 0
            }
            return bundle, metrics
            
        # 2. LLM Enrichment
        prompt = ENRICHMENT_PROMPT.format(
            arch_json=arch.model_dump_json(indent=2),
            base_schema_json=base_bundle.model_dump_json(indent=2)
        )
        
        raw_json = self._call_with_backoff(prompt)
        try:
            parsed = self._parse_json(raw_json)
            bundle = SchemaBundle(**parsed)
        except Exception as e:
            print(f"Enrichment failed, falling back to deterministic base: {e}")
            bundle = base_bundle
            
        repair_count = 0
        validation_passed = False
        
        # 3. Validation & Targeted Repair Loop
        for _ in range(max_repairs + 1):
            errors = self.validator.validate(arch, bundle)
            if not errors:
                validation_passed = True
                break
                
            print(f"    [Validator] Found {len(errors)} errors. Triggering Domain-Specific Repair...", flush=True)
            bundle = self.repair_engine.repair(arch, bundle, errors)
            repair_count += 1
            
        metrics = {
            "latency": time.time() - start_time,
            "repair_count": repair_count,
            "validation_passed": validation_passed
        }
        
        return bundle, metrics

    def _get_domain_fields(self, entity_name: str) -> list:
        """Returns domain-aware columns for an entity using the comprehensive field map."""
        en = entity_name.lower().replace(" ", "_")
        field_defs = DOMAIN_FIELDS.get(en)
        if field_defs:
            return [
                Column(name=name, data_type=dtype, is_nullable=not required, is_unique=(name == "email"))
                for name, dtype, required in field_defs
            ]
        # Fallback — still meaningful, never just "title"/"description"
        return [
            Column(name="name", data_type="string", is_nullable=False),
            Column(name="status", data_type="string", is_nullable=True),
            Column(name="description", data_type="text", is_nullable=True),
            Column(name="owner_id", data_type="uuid", is_nullable=True),
        ]

    def _deterministic_scaffold(self, arch: ArchitectureConfig) -> SchemaBundle:
        """
        Pure Python mapping logic:
        Entities -> Tables
        Relationships -> Foreign Keys
        Entities -> CRUD APIs
        Flows -> Pages
        Permissions -> Roles/Access
        """
        # Database
        tables = []
        for ent in arch.entities:
            t_name = f"{ent.name.lower()}s"
            cols = [
                Column(name="id", data_type="uuid", is_primary=True, is_nullable=False, is_unique=True)
            ]
            
            # Domain-aware business fields
            cols.extend(self._get_domain_fields(ent.name))
            
            cols.extend([
                Column(name="created_at", data_type="datetime"),
                Column(name="updated_at", data_type="datetime")
            ])
            
            prov = Provenance(source_type="entity", source_id=ent.name, architecture_hash=arch.architecture_hash)
            tables.append(Table(name=t_name, columns=cols, foreign_keys=[], indexes=[], provenance=prov))
            
        table_dict = {t.name: t for t in tables}
        for rel in arch.relationships:
            s_table = f"{rel.source_entity.lower()}s"
            t_table = f"{rel.target_entity.lower()}s"
            if rel.type in ("one_to_many", "many_to_many") and t_table in table_dict:
                fk_col = f"{rel.source_entity.lower()}_id"
                # Don't add duplicate FK columns
                existing_cols = {c.name for c in table_dict[t_table].columns}
                if fk_col not in existing_cols:
                    fk = ForeignKey(column_name=fk_col, referenced_table=s_table, referenced_column="id")
                    table_dict[t_table].foreign_keys.append(fk)
                    table_dict[t_table].columns.append(Column(name=fk_col, data_type="uuid"))
                
        db_schema = DatabaseSchema(tables=list(table_dict.values()))
        
        # API — Full CRUD including GET by ID
        endpoints = []
        for t in tables:
            base_path = f"/{t.name}"
            prov = Provenance(source_type="entity", source_id=t.provenance.source_id, architecture_hash=arch.architecture_hash)
            
            # Extract request schema directly from business columns (exclude id, created_at, updated_at)
            req_props = {col.name: col.data_type for col in t.columns if col.name not in ["id", "created_at", "updated_at"]}
            res_props = {col.name: col.data_type for col in t.columns}
            
            endpoints.append(Endpoint(path=base_path, method="GET", operation_id=f"list_{t.name}", description=f"List all {t.name}", request_schema={}, response_schema={"type": "array", "items": {"type": "object", "properties": res_props}}, validation_rules=[], provenance=prov))
            endpoints.append(Endpoint(path=f"{base_path}/{{id}}", method="GET", operation_id=f"get_{t.name}", description=f"Get a single {t.provenance.source_id} by ID", request_schema={}, response_schema={"type": "object", "properties": res_props}, validation_rules=[], provenance=prov))
            endpoints.append(Endpoint(path=base_path, method="POST", operation_id=f"create_{t.name}", description=f"Create a new {t.provenance.source_id}", request_schema={"type": "object", "properties": req_props}, response_schema={"type": "object", "properties": res_props}, validation_rules=[], provenance=prov))
            endpoints.append(Endpoint(path=f"{base_path}/{{id}}", method="PUT", operation_id=f"update_{t.name}", description=f"Update a {t.provenance.source_id}", request_schema={"type": "object", "properties": req_props}, response_schema={"type": "object", "properties": res_props}, validation_rules=[], provenance=prov))
            endpoints.append(Endpoint(path=f"{base_path}/{{id}}", method="DELETE", operation_id=f"delete_{t.name}", description=f"Delete a {t.provenance.source_id}", request_schema={}, response_schema={"success": "boolean"}, validation_rules=[], provenance=prov))
        api_schema = ApiSchema(endpoints=endpoints)
        
        # UI — derive form fields from entity columns, never use title/description fallback
        pages = []
        for flow in arch.user_flows:
            p_name = flow.name.replace(" ", "_").lower()
            prov = Provenance(source_type="flow", source_id=flow.name, architecture_hash=arch.architecture_hash)
            
            # Match flow to entity table
            target_candidates = [
                p_name.replace("manage_", ""),
                p_name.replace("browse_", ""),
                p_name.replace("submit_", ""),
                p_name.replace("_dashboard", ""),
                p_name.replace("_portal", ""),
                p_name.replace("_builder", ""),
                p_name,
            ]
            
            matched_table = None
            for candidate in target_candidates:
                # Try direct plural match
                for tbl in tables:
                    tbl_base = tbl.name.rstrip("s")
                    if candidate == tbl.name or candidate == tbl_base or candidate.rstrip("s") == tbl_base:
                        matched_table = tbl
                        break
                if matched_table:
                    break
            
            if matched_table:
                form_fields = [
                    FormField(
                        name=col.name,
                        type="email" if "email" in col.name else ("number" if col.data_type in ["decimal", "integer"] else ("date" if col.data_type in ["date", "datetime"] else "text")),
                        required=not col.is_nullable
                    )
                    for col in matched_table.columns
                    if col.name not in ["id", "created_at", "updated_at"]
                ]
            else:
                # Derive from any entity that partially matches the flow name
                form_fields = [
                    FormField(name="name", type="text", required=True),
                    FormField(name="status", type="text", required=True),
                    FormField(name="description", type="text", required=False),
                    FormField(name="owner_id", type="text", required=False),
                ]
                
            components = [UIComponent(id=f"{p_name}_form", type="form", props={}, form_fields=form_fields)]
            pages.append(Page(name=p_name, route=f"/{p_name}", layout="default", components=components, provenance=prov))
        ui_schema = UiSchema(pages=pages, navigation=[p.route for p in pages])
        
        # Auth
        roles = []
        route_access = []
        page_access = []
        for p in arch.permissions:
            prov = Provenance(source_type="role", source_id=p.role, architecture_hash=arch.architecture_hash)
            roles.append(Role(name=p.role, description=f"Role {p.role}", provenance=prov))
            
        for page in pages:
            # By default give access to all roles for scaffolding
            page_access.append(PageAccess(page_name=page.name, allowed_roles=[r.name for r in roles]))
            
        auth_schema = AuthSchema(roles=roles, route_access=route_access, page_access=page_access)
        
        return SchemaBundle(database=db_schema, api=api_schema, ui=ui_schema, auth=auth_schema)

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
