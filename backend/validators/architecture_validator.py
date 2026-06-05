from typing import List
from dataclasses import dataclass
from backend.schemas.architecture_config import ArchitectureConfig
from backend.schemas.intent_config import IntentConfig

@dataclass
class ValidationError:
    section: str
    message: str

class ArchitectureValidator:
    def validate(self, intent: IntentConfig, arch: ArchitectureConfig) -> List[ValidationError]:
        errors = []
        
        # 1. Module Validation
        module_names = set()
        for mod in arch.modules:
            if mod.name in module_names:
                errors.append(ValidationError("modules", f"Duplicate module name found: {mod.name}"))
            module_names.add(mod.name)
            
        if not module_names:
            errors.append(ValidationError("modules", "Architecture must have at least one module."))
            
        # Ensure every feature roughly corresponds to module/entities (Heuristic check)
        # We'll just enforce no orphan modules (each module must have an entity)
        modules_with_entities = set(e.module_affiliation for e in arch.entities)
        for mod in arch.modules:
            if mod.name not in modules_with_entities:
                errors.append(ValidationError("modules", f"Orphan module '{mod.name}' has no entities associated with it."))
                
        # 2. Entity Validation
        entity_names = set()
        for ent in arch.entities:
            if ent.name in entity_names:
                errors.append(ValidationError("entities", f"Duplicate entity name found: {ent.name}"))
            entity_names.add(ent.name)
            if ent.module_affiliation not in module_names:
                errors.append(ValidationError("entities", f"Entity '{ent.name}' belongs to non-existent module '{ent.module_affiliation}'"))

        # 3. Relationship Validation
        entities_in_relations = set()
        for rel in arch.relationships:
            if rel.source_entity not in entity_names:
                errors.append(ValidationError("relationships", f"Source entity '{rel.source_entity}' does not exist."))
            if rel.target_entity not in entity_names:
                errors.append(ValidationError("relationships", f"Target entity '{rel.target_entity}' does not exist."))
            entities_in_relations.add(rel.source_entity)
            entities_in_relations.add(rel.target_entity)
            
        for ent in entity_names:
            if ent not in entities_in_relations:
                errors.append(ValidationError("entities", f"Orphan entity '{ent}' does not participate in any relationships."))

        # 4. Flows Validation
        flow_names = set()
        for flow in arch.user_flows:
            if flow.name in flow_names:
                errors.append(ValidationError("user_flows", f"Duplicate user flow found: {flow.name}"))
            flow_names.add(flow.name)
            for role in flow.required_roles:
                if role not in intent.roles:
                    errors.append(ValidationError("user_flows", f"Flow '{flow.name}' requires role '{role}' which is not in IntentConfig."))
                    
        # 5. Permission Validation
        perm_roles = set()
        for perm in arch.permissions:
            if perm.role in perm_roles:
                errors.append(ValidationError("permissions", f"Duplicate permission entry for role: {perm.role}"))
            perm_roles.add(perm.role)
            if perm.role not in intent.roles:
                errors.append(ValidationError("permissions", f"Permission role '{perm.role}' not in IntentConfig roles."))
                
        # 6. Components Validation
        comp_names = set()
        for comp in arch.system_components:
            if comp.name in comp_names:
                errors.append(ValidationError("system_components", f"Duplicate system component: {comp.name}"))
            comp_names.add(comp.name)
            
        # 7. Scores Validation
        if not (0.0 <= arch.confidence <= 1.0):
            errors.append(ValidationError("confidence", "Confidence score must be between 0 and 1."))
        if not (0.0 <= arch.completeness_score <= 1.0):
            errors.append(ValidationError("completeness_score", "Completeness score must be between 0 and 1."))
        if not (0.0 <= arch.ambiguity_score <= 1.0):
            errors.append(ValidationError("ambiguity_score", "Ambiguity score must be between 0 and 1."))

        return errors
