import re
from typing import List, Tuple
from abc import ABC, abstractmethod
from backend.schemas.intent_config import IntentConfig
from backend.schemas.architecture_config import ArchitectureConfig
from backend.schemas.schema_bundle import SchemaBundle
from backend.schemas.validation_report import ValidationError

class ValidationRule(ABC):
    @property
    @abstractmethod
    def rule_id(self) -> str: pass
    
    @property
    @abstractmethod
    def section(self) -> str: pass
    
    @property
    @abstractmethod
    def severity(self) -> str: pass

    @abstractmethod
    def validate(self, intent: IntentConfig, arch: ArchitectureConfig, bundle: SchemaBundle) -> List[ValidationError]:
        pass

# ---------------------------------------------------------------------------
# 1. Intent Rules
# ---------------------------------------------------------------------------
class RuleIntent001(ValidationRule):
    rule_id = "INT_001"
    section = "architecture"
    severity = "LOW"
    def validate(self, intent, arch, bundle):
        errors = []
        for feature in intent.features:
            if not any(feature.lower() in mod.name.lower() or feature.lower() in mod.description.lower() for mod in arch.modules):
                errors.append(ValidationError(
                    rule_id=self.rule_id, severity=self.severity, section=self.section,
                    message=f"Feature '{feature}' may not be mapped to any module.",
                    repair_hint="Review module names and descriptions."
                ))
        return errors

class RuleIntent002(ValidationRule):
    rule_id = "INT_002"
    section = "architecture"
    severity = "HIGH"
    def validate(self, intent, arch, bundle):
        errors = []
        for role in intent.roles:
            if not any(p.role == role for p in arch.permissions):
                errors.append(ValidationError(
                    rule_id=self.rule_id, severity=self.severity, section=self.section,
                    message=f"Role '{role}' defined in intent has no permissions in architecture.",
                    repair_hint="Add permissions for this role."
                ))
        return errors

class RuleIntent003(ValidationRule):
    rule_id = "INT_003"
    section = "architecture"
    severity = "HIGH"
    def validate(self, intent, arch, bundle):
        errors = []
        for feature in intent.features:
            f_lower = feature.lower().replace(" ", "_")
            related_modules = [mod.name for mod in arch.modules if f_lower in mod.name.lower() or f_lower in mod.description.lower()]
            related_entities = [ent.name for ent in arch.entities if ent.module_affiliation in related_modules]
            
            has_mod = bool(related_modules)
            has_page = any(f_lower in page.name.lower() for page in bundle.ui.pages)
            has_api = any(f_lower in ep.path.lower() or any(ent in ep.path.lower() for ent in related_entities) for ep in bundle.api.endpoints)
            
            if not has_mod or not has_page or not has_api:
                errors.append(ValidationError(
                    rule_id=self.rule_id, severity=self.severity, section=self.section,
                    message=f"Feature '{feature}' lacks full architectural representation (missing module, page, or API).",
                    repair_hint="Ensure the feature generates a module, a page, and an endpoint."
                ))
        return errors

class RuleARCH001(ValidationRule):
    rule_id = "ARCH_001"
    section = "architecture"
    severity = "HIGH"
    def validate(self, intent, arch, bundle):
        errors = []
        app_type = intent.app_type.lower()
        min_mods, min_ents, min_pages = 0, 0, 0
        if "crm" in app_type:
            min_mods, min_ents, min_pages = 4, 3, 4
        elif "marketplace" in app_type:
            min_mods, min_ents, min_pages = 5, 4, 5
        elif "school" in app_type:
            min_mods, min_ents, min_pages = 5, 5, 5
            
        if min_mods > 0:
            if len(arch.modules) < min_mods:
                errors.append(ValidationError(rule_id=self.rule_id, severity=self.severity, section=self.section, message=f"App type '{app_type}' requires >= {min_mods} modules, found {len(arch.modules)}.", repair_hint="Generate more modules."))
            if len(arch.entities) < min_ents:
                errors.append(ValidationError(rule_id=self.rule_id, severity=self.severity, section=self.section, message=f"App type '{app_type}' requires >= {min_ents} entities, found {len(arch.entities)}.", repair_hint="Generate more entities."))
            if len(bundle.ui.pages) < min_pages:
                errors.append(ValidationError(rule_id=self.rule_id, severity=self.severity, section=self.section, message=f"App type '{app_type}' requires >= {min_pages} pages, found {len(bundle.ui.pages)}.", repair_hint="Generate more user flows/pages."))
        return errors

# ---------------------------------------------------------------------------
# 2. Database Rules
# ---------------------------------------------------------------------------
class RuleDB001(ValidationRule):
    rule_id = "DB_001"
    section = "database"
    severity = "HIGH"
    def validate(self, intent, arch, bundle):
        errors = []
        db_tables = {t.name: t for t in bundle.database.tables}
        for ent in arch.entities:
            expected_table = f"{ent.name.lower()}s"
            if expected_table not in db_tables:
                errors.append(ValidationError(
                    rule_id=self.rule_id, severity=self.severity, section=self.section,
                    message=f"Entity '{ent.name}' has no corresponding database table.",
                    repair_hint=f"Create a table named '{expected_table}'."
                ))
        return errors

class RuleDB002(ValidationRule):
    rule_id = "DB_002"
    section = "database"
    severity = "MEDIUM"
    def validate(self, intent, arch, bundle):
        errors = []
        db_tables = {t.name: t for t in bundle.database.tables}
        for rel in arch.relationships:
            if rel.type in ("one_to_many", "many_to_many"):
                target_table = f"{rel.target_entity.lower()}s"
                source_col = f"{rel.source_entity.lower()}_id"
                if target_table in db_tables:
                    has_fk = any(fk.column_name == source_col for fk in db_tables[target_table].foreign_keys)
                    if not has_fk:
                        errors.append(ValidationError(
                            rule_id=self.rule_id, severity=self.severity, section=self.section,
                            message=f"Missing foreign key '{source_col}' in table '{target_table}'.",
                            repair_hint="Add a ForeignKey object linking to the source entity."
                        ))
        return errors

# ---------------------------------------------------------------------------
# 3. API Rules
# ---------------------------------------------------------------------------
class RuleAPI001(ValidationRule):
    rule_id = "API_001"
    section = "api"
    severity = "HIGH"
    def validate(self, intent, arch, bundle):
        errors = []
        for ent in arch.entities:
            base_path = f"/{ent.name.lower()}s"
            methods = [e.method for e in bundle.api.endpoints if e.path == base_path or e.path.startswith(f"{base_path}/")]
            if "GET" not in methods or "POST" not in methods:
                errors.append(ValidationError(
                    rule_id=self.rule_id, severity=self.severity, section=self.section,
                    message=f"Incomplete CRUD coverage for entity '{ent.name}'.",
                    repair_hint=f"Generate missing GET/POST endpoints at {base_path}."
                ))
        return errors

# ---------------------------------------------------------------------------
# 4. UI Rules
# ---------------------------------------------------------------------------
class RuleUI001(ValidationRule):
    rule_id = "UI_001"
    section = "ui"
    severity = "HIGH"
    def validate(self, intent, arch, bundle):
        errors = []
        for flow in arch.user_flows:
            p_name = flow.name.replace(" ", "_").lower()
            if not any(page.name == p_name for page in bundle.ui.pages):
                errors.append(ValidationError(
                    rule_id=self.rule_id, severity=self.severity, section=self.section,
                    message=f"User flow '{flow.name}' is missing a corresponding UI page.",
                    repair_hint=f"Generate a Page named '{p_name}'."
                ))
        return errors

# ---------------------------------------------------------------------------
# 5. Auth Rules
# ---------------------------------------------------------------------------
class RuleAUTH001(ValidationRule):
    rule_id = "AUTH_001"
    section = "auth"
    severity = "MEDIUM"
    def validate(self, intent, arch, bundle):
        errors = []
        for page in bundle.ui.pages:
            has_access_rule = any(pa.page_name == page.name for pa in bundle.auth.page_access)
            if not has_access_rule:
                errors.append(ValidationError(
                    rule_id=self.rule_id, severity=self.severity, section=self.section,
                    message=f"Page '{page.name}' is unprotected (no access rules).",
                    repair_hint="Add a PageAccess rule defining allowed roles."
                ))
        return errors

# ---------------------------------------------------------------------------
# 6. Provenance Rules
# ---------------------------------------------------------------------------
class RulePROV001(ValidationRule):
    rule_id = "PROV_001"
    section = "database"
    severity = "LOW"
    def validate(self, intent, arch, bundle):
        errors = []
        for table in bundle.database.tables:
            if not table.provenance:
                errors.append(ValidationError(
                    rule_id=self.rule_id, severity=self.severity, section=self.section,
                    message=f"Table '{table.name}' is missing provenance data.",
                    repair_hint="Attach a Provenance object."
                ))
        return errors

class RulePROV002(ValidationRule):
    rule_id = "PROV_002"
    section = "api"
    severity = "LOW"
    def validate(self, intent, arch, bundle):
        errors = []
        for ep in bundle.api.endpoints:
            if not ep.provenance:
                errors.append(ValidationError(
                    rule_id=self.rule_id, severity=self.severity, section=self.section,
                    message=f"Endpoint '{ep.method} {ep.path}' is missing provenance data.",
                    repair_hint="Attach a Provenance object."
                ))
        return errors

# ---------------------------------------------------------------------------
# 7. Runtime Rules
# ---------------------------------------------------------------------------
class RuleRUN001(ValidationRule):
    rule_id = "RUN_001"
    section = "ui"
    severity = "HIGH"
    def validate(self, intent, arch, bundle):
        errors = []
        for page in bundle.ui.pages:
            if not page.route.startswith("/"):
                errors.append(ValidationError(
                    rule_id=self.rule_id, severity=self.severity, section=self.section,
                    message=f"Page '{page.name}' has invalid route format '{page.route}'.",
                    repair_hint="Routes must start with '/'."
                ))
        return errors

class RuleRUN002(ValidationRule):
    rule_id = "RUN_002"
    section = "api"
    severity = "HIGH"
    def validate(self, intent, arch, bundle):
        errors = []
        valid_methods = {"GET", "POST", "PUT", "DELETE", "PATCH"}
        for ep in bundle.api.endpoints:
            if ep.method not in valid_methods:
                errors.append(ValidationError(
                    rule_id=self.rule_id, severity=self.severity, section=self.section,
                    message=f"Endpoint '{ep.path}' has invalid method '{ep.method}'.",
                    repair_hint=f"Use one of: {valid_methods}"
                ))
        return errors

# ---------------------------------------------------------------------------
# 8. STRICT QUALITY RULES — Placeholder Rejection
# ---------------------------------------------------------------------------
FORBIDDEN_FIELDS = {"field1", "field2", "field3", "placeholder", "temp", "dummy", "sample", "test_field"}
PLACEHOLDER_PAGE_PATTERNS = [r"^flow_.*", r"^mod_.*", r"^temp_.*", r"^placeholder_.*", r"^generated_.*"]

class RuleFIELD001(ValidationRule):
    """Reject placeholder/generic field names in database tables."""
    rule_id = "FIELD_001"
    section = "database"
    severity = "HIGH"
    def validate(self, intent, arch, bundle):
        errors = []
        for table in bundle.database.tables:
            for col in table.columns:
                if col.name.lower() in FORBIDDEN_FIELDS:
                    errors.append(ValidationError(
                        rule_id=self.rule_id, severity=self.severity, section=self.section,
                        message=f"Table '{table.name}' contains forbidden placeholder field '{col.name}'.",
                        repair_hint=f"Replace '{col.name}' with a domain-specific field name."
                    ))
        return errors

class RuleFIELD002(ValidationRule):
    """Every entity table must have >= 4 business columns (excluding id, created_at, updated_at)."""
    rule_id = "FIELD_002"
    section = "database"
    severity = "MEDIUM"
    def validate(self, intent, arch, bundle):
        errors = []
        meta_cols = {"id", "created_at", "updated_at"}
        for table in bundle.database.tables:
            biz_cols = [c for c in table.columns if c.name not in meta_cols]
            if len(biz_cols) < 4:
                errors.append(ValidationError(
                    rule_id=self.rule_id, severity=self.severity, section=self.section,
                    message=f"Table '{table.name}' has only {len(biz_cols)} business columns (minimum 4 required).",
                    repair_hint="Add domain-specific columns to this table."
                ))
        return errors

class RulePAGE001(ValidationRule):
    """Reject placeholder page names matching forbidden patterns."""
    rule_id = "PAGE_001"
    section = "ui"
    severity = "HIGH"
    def validate(self, intent, arch, bundle):
        errors = []
        for page in bundle.ui.pages:
            for pattern in PLACEHOLDER_PAGE_PATTERNS:
                if re.match(pattern, page.name):
                    errors.append(ValidationError(
                        rule_id=self.rule_id, severity=self.severity, section=self.section,
                        message=f"Page '{page.name}' matches forbidden placeholder pattern '{pattern}'.",
                        repair_hint="Use a meaningful business page name like 'manage_contacts' or 'billing_dashboard'."
                    ))
                    break
        return errors

# ---------------------------------------------------------------------------
# 9. FEATURE COVERAGE RULES — full traceability chain
# ---------------------------------------------------------------------------
class RuleFCOV001(ValidationRule):
    """Validates feature→module→entity→table→API→page→permission chain."""
    rule_id = "FCOV_001"
    section = "coverage"
    severity = "HIGH"
    def validate(self, intent, arch, bundle):
        errors = []
        for feature in intent.features:
            f_lower = feature.lower().replace(" ", "_")
            
            # Check module
            has_module = any(f_lower in mod.name.lower() or f_lower in mod.description.lower() for mod in arch.modules)
            
            # Check entity (at least one entity in a module related to this feature)
            related_modules = [mod.name for mod in arch.modules if f_lower in mod.name.lower() or f_lower in mod.description.lower()]
            has_entity = any(ent.module_affiliation in related_modules for ent in arch.entities)
            
            # Check table
            related_entities = [ent.name for ent in arch.entities if ent.module_affiliation in related_modules]
            has_table = any(f"{ent}s" in [t.name for t in bundle.database.tables] for ent in related_entities)
            
            # Check API
            has_api = any(f_lower in ep.path.lower() or any(ent in ep.path.lower() for ent in related_entities) for ep in bundle.api.endpoints)
            
            # Check page
            has_page = any(f_lower in page.name.lower() for page in bundle.ui.pages)
            
            # Check permission
            has_permission = any(
                any(f_lower in action or f"view_{f_lower}" in action for action in perm.actions)
                for perm in arch.permissions
            )
            
            missing = []
            if not has_module: missing.append("module")
            if not has_entity: missing.append("entity")
            if not has_table: missing.append("table")
            if not has_api: missing.append("API endpoint")
            if not has_page: missing.append("UI page")
            if not has_permission: missing.append("permission")
            
            if missing:
                errors.append(ValidationError(
                    rule_id=self.rule_id, severity=self.severity, section=self.section,
                    message=f"Feature '{feature}' missing traceability: {', '.join(missing)}.",
                    repair_hint=f"Ensure '{feature}' has representation at every pipeline stage."
                ))
        return errors

# ---------------------------------------------------------------------------
# 10. NEGATIVE REQUIREMENT RULES — forbidden features must not appear
# ---------------------------------------------------------------------------
class RuleNEG001(ValidationRule):
    """Validates that forbidden features/entities do not appear anywhere in the output."""
    rule_id = "NEG_001"
    section = "coverage"
    severity = "HIGH"
    def validate(self, intent, arch, bundle):
        errors = []
        forbidden = set(getattr(intent, "forbidden_entities", []) or [])
        forbidden.update(getattr(intent, "forbidden_features", []) or [])
        
        if not forbidden:
            return errors
        
        for fb in forbidden:
            fb_lower = fb.lower()
            # Check modules
            if any(fb_lower in mod.name.lower() for mod in arch.modules):
                errors.append(ValidationError(
                    rule_id=self.rule_id, severity=self.severity, section=self.section,
                    message=f"Forbidden feature '{fb}' found in architecture modules.",
                    repair_hint=f"Remove any module containing '{fb}'."
                ))
            # Check entities
            if any(fb_lower in ent.name.lower() for ent in arch.entities):
                errors.append(ValidationError(
                    rule_id=self.rule_id, severity=self.severity, section=self.section,
                    message=f"Forbidden entity '{fb}' found in architecture entities.",
                    repair_hint=f"Remove entity '{fb}'."
                ))
            # Check pages
            if any(fb_lower in page.name.lower() for page in bundle.ui.pages):
                errors.append(ValidationError(
                    rule_id=self.rule_id, severity=self.severity, section=self.section,
                    message=f"Forbidden feature '{fb}' found in UI pages.",
                    repair_hint=f"Remove page containing '{fb}'."
                ))
            # Check API endpoints
            if any(fb_lower in ep.path.lower() for ep in bundle.api.endpoints):
                errors.append(ValidationError(
                    rule_id=self.rule_id, severity=self.severity, section=self.section,
                    message=f"Forbidden feature '{fb}' found in API endpoints.",
                    repair_hint=f"Remove endpoint containing '{fb}'."
                ))
        return errors


# ---------------------------------------------------------------------------
# REGISTRY
# ---------------------------------------------------------------------------
class RuleRegistry:
    def __init__(self):
        self.rules: List[ValidationRule] = [
            # Intent rules
            RuleIntent001(), RuleIntent002(), RuleIntent003(), RuleARCH001(),
            # Database rules
            RuleDB001(), RuleDB002(),
            # API rules
            RuleAPI001(),
            # UI rules
            RuleUI001(),
            # Auth rules
            RuleAUTH001(),
            # Provenance rules
            RulePROV001(), RulePROV002(),
            # Runtime rules
            RuleRUN001(), RuleRUN002(),
            # Strict quality rules (Phase 8)
            RuleFIELD001(), RuleFIELD002(), RulePAGE001(),
            # Feature coverage (Phase 1/8)
            RuleFCOV001(),
            # Negative requirements (Phase 8)
            RuleNEG001(),
        ]
