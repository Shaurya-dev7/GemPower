from typing import List, Tuple
from backend.schemas.intent_config import IntentConfig
from backend.schemas.architecture_config import ArchitectureConfig
from backend.schemas.schema_bundle import SchemaBundle
from backend.schemas.validation_report import ValidationReport, ValidationError
from backend.validators.change_impact_analyzer import ChangeImpactAnalyzer
from backend.validators.rule_registry import RuleRegistry

class GlobalValidator:
    def __init__(self):
        self.impact_analyzer = ChangeImpactAnalyzer()
        self.registry = RuleRegistry()

    def validate(self, intent: IntentConfig, arch: ArchitectureConfig, bundle: SchemaBundle) -> ValidationReport:
        errors = []
        warnings = []

        # Iterate through modular rules instead of hardcoded logic
        for rule in self.registry.rules:
            rule_errors = rule.validate(intent, arch, bundle)
            for err in rule_errors:
                if err.severity == "LOW" or err.rule_id == "INT_001": # Treat INT_001 or LOW as warnings
                    warnings.append(err)
                else:
                    errors.append(err)

        # Calculate Score
        score = 100.0
        for err in errors:
            if err.severity == "HIGH": score -= 10.0
            elif err.severity == "MEDIUM": score -= 5.0
            else: score -= 2.0
            
        for warn in warnings:
            if warn.severity == "HIGH": score -= 5.0
            elif warn.severity == "MEDIUM": score -= 2.0
            else: score -= 1.0

        score = max(0.0, score)

        failed_sections = list(set([e.section for e in errors]))

        return ValidationReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            failed_sections=failed_sections,
            validation_score=score
        )
