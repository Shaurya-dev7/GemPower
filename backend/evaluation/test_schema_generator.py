import os
import json
from backend.schemas.architecture_config import ArchitectureConfig, Entity, Relationship, UserFlow, Permission, Module
from backend.pipeline.schema_generator import SchemaGenerator

def test_schema_generator():
    os.environ["TEST_MODE"] = "True"
    
    # Mock an ArchitectureConfig
    arch = ArchitectureConfig(
        modules=[Module(name="core", description="core")],
        entities=[
            Entity(name="User", module_affiliation="core"),
            Entity(name="Contact", module_affiliation="core")
        ],
        relationships=[
            Relationship(source_entity="User", target_entity="Contact", type="one_to_many", description="User owns Contacts")
        ],
        user_flows=[
            UserFlow(name="login", steps=["enter email"], required_roles=["user"]),
            UserFlow(name="create_contact", steps=["submit form"], required_roles=["user"])
        ],
        permissions=[
            Permission(role="user", actions=["read", "write"])
        ],
        system_components=[],
        external_dependencies=[],
        assumptions=[],
        confidence=1.0,
        completeness_score=1.0,
        ambiguity_score=0.0
    )
    
    generator = SchemaGenerator()
    bundle, metrics = generator.generate_schemas(arch)
    
    print("\n--- Schema Generation Metrics ---")
    print(json.dumps(metrics, indent=2))
    
    print("\n--- Generated Database Schema (Tables) ---")
    for table in bundle.database.tables:
        print(f"Table: {table.name} (Source: {table.provenance.source_id if table.provenance else 'Unknown'})")
        for col in table.columns:
            print(f"  - {col.name} ({col.data_type})")
        for fk in table.foreign_keys:
            print(f"  * FK: {fk.column_name} -> {fk.referenced_table}.{fk.referenced_column}")
            
    print("\n--- Generated API Endpoints ---")
    for ep in bundle.api.endpoints:
        print(f"{ep.method} {ep.path} (Source: {ep.provenance.source_id if ep.provenance else 'Unknown'})")

if __name__ == "__main__":
    test_schema_generator()
