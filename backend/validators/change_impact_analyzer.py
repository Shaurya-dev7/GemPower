from typing import List
from backend.schemas.schema_bundle import SchemaBundle
from backend.schemas.validation_report import ImpactReport

class ChangeImpactAnalyzer:
    def analyze_removal(self, bundle: SchemaBundle, entity_name: str) -> ImpactReport:
        """
        Calculates the downstream impact if a specific entity (e.g. 'Subscription') is removed.
        Traces provenance across DB, API, and UI.
        """
        affected_entities = [entity_name]
        affected_tables = []
        affected_endpoints = []
        affected_pages = []

        # Find DB tables generated from this entity
        for table in bundle.database.tables:
            if table.provenance and table.provenance.source_id.lower() == entity_name.lower():
                affected_tables.append(table.name)
            # Also check if it's impacted by foreign keys
            elif any(fk.referenced_table.startswith(entity_name.lower()) for fk in table.foreign_keys):
                if table.name not in affected_tables:
                    affected_tables.append(table.name)

        # Find APIs generated from this entity
        for ep in bundle.api.endpoints:
            if ep.provenance and ep.provenance.source_id.lower() == entity_name.lower():
                affected_endpoints.append(ep.path)
            elif any(t in ep.path for t in affected_tables):
                # Fallback heuristic if provenance is missing
                if ep.path not in affected_endpoints:
                    affected_endpoints.append(ep.path)

        # Find UI Pages generated from this entity (Assuming flows are named similarly to entities, e.g., create_subscription)
        for page in bundle.ui.pages:
            # Check provenance if it explicitly links back to the entity (unlikely since it links to flows, but workflows often share naming)
            if entity_name.lower() in page.name.lower():
                affected_pages.append(page.name)

        # Deduplicate
        affected_endpoints = list(set(affected_endpoints))
        affected_tables = list(set(affected_tables))
        
        return ImpactReport(
            affected_entities=affected_entities,
            affected_tables=affected_tables,
            affected_endpoints=affected_endpoints,
            affected_pages=affected_pages
        )
