from enum import Enum
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field, EmailStr, ConfigDict, StringConstraints
from typing_extensions import Annotated

# --- Enums for Strong Typing ---

class ArchitectureStyle(str, Enum):
    MONOLITH = "monolith"
    MICROSERVICES = "microservices"
    SERVERLESS = "serverless"

class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

class FieldType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    JSON = "json"
    UUID = "uuid"

class ComponentType(str, Enum):
    FORM = "form"
    TABLE = "table"
    DASHBOARD = "dashboard"
    LIST = "list"
    DETAILS = "details"
    MODAL = "modal"

class AuthProvider(str, Enum):
    JWT = "jwt"
    OAUTH2 = "oauth2"
    SAML = "saml"
    MAGIC_LINK = "magic_link"

class PaymentProvider(str, Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    BRAINTREE = "braintree"
    CUSTOM = "custom"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"

# --- Models ---

class MetadataConfig(BaseModel):
    model_config = ConfigDict(extra='allow')
    app_name: str = Field(..., min_length=2, max_length=100)
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    description: Optional[str] = None
    author: Optional[EmailStr] = None

class AssumptionConfig(BaseModel):
    id: str
    description: str
    impact_level: str = Field(pattern="^(low|medium|high)$")

class ArchitectureConfig(BaseModel):
    style: ArchitectureStyle
    technologies: List[str]
    deployment_target: Optional[str] = None

class DbColumn(BaseModel):
    name: str = Field(..., pattern=r"^[a-z_]+$")
    type: FieldType
    is_primary_key: bool = False
    is_required: bool = True
    is_unique: bool = False
    references: Optional[str] = Field(None, description="Format: table_name.column_name")

class DbTable(BaseModel):
    name: str = Field(..., pattern=r"^[a-z_]+$")
    columns: List[DbColumn]

class DatabaseConfig(BaseModel):
    provider: str = Field(default="postgresql")
    tables: List[DbTable]

class ApiParameter(BaseModel):
    name: str
    in_location: str = Field(pattern="^(query|path|body|header)$")
    type: FieldType
    required: bool = True

class ApiEndpoint(BaseModel):
    path: str = Field(..., pattern=r"^\/[a-zA-Z0-9\/\-\{\}_]*$")
    method: HttpMethod
    summary: Optional[str] = None
    parameters: List[ApiParameter] = []
    response_schema_ref: Optional[str] = None
    required_roles: List[str] = []

class ApiConfig(BaseModel):
    base_url: str = "/api/v1"
    endpoints: List[ApiEndpoint]

class UIComponent(BaseModel):
    id: str
    type: ComponentType
    title: Optional[str] = None
    data_source: Optional[str] = Field(None, description="Reference to API endpoint or state")
    fields: List[str] = []

class UIPage(BaseModel):
    path: str
    name: str
    components: List[UIComponent]
    required_roles: List[str] = []

class UIConfig(BaseModel):
    theme: str = "light"
    pages: List[UIPage]

class Role(BaseModel):
    name: str
    permissions: List[str]

class AuthConfig(BaseModel):
    providers: List[AuthProvider]
    roles: List[Role]

class BusinessRule(BaseModel):
    id: str
    description: str
    condition: str
    action: str

class BusinessLogicConfig(BaseModel):
    rules: List[BusinessRule]

class Integration(BaseModel):
    name: str
    provider: str
    purpose: str
    config_keys: List[str]

class IntegrationsConfig(BaseModel):
    services: List[Integration]

class PaymentsConfig(BaseModel):
    enabled: bool
    provider: Optional[PaymentProvider] = None
    currency: Optional[str] = "USD"
    webhook_endpoint: Optional[str] = None

class NotificationTemplate(BaseModel):
    id: str
    channel: NotificationChannel
    subject: Optional[str] = None
    body_template: str

class NotificationsConfig(BaseModel):
    enabled: bool
    templates: List[NotificationTemplate]

class AnalyticsEvent(BaseModel):
    name: str
    properties: List[str]

class AnalyticsConfig(BaseModel):
    enabled: bool
    provider: str
    events: List[AnalyticsEvent]

class FeatureFlag(BaseModel):
    name: str
    default_state: bool
    description: Optional[str] = None

class FeatureFlagsConfig(BaseModel):
    flags: List[FeatureFlag]

class ValidationRule(BaseModel):
    id: str
    description: str
    severity: str = Field(pattern="^(warning|error)$")
    expression: str

class ValidationRulesConfig(BaseModel):
    cross_layer_rules: List[ValidationRule]

# --- Master AppConfig Schema ---

class AppConfig(BaseModel):
    """
    The Single Source of Truth for the AI Compiler System.
    """
    model_config = ConfigDict(extra='allow')
    
    metadata: MetadataConfig
    assumptions: List[AssumptionConfig] = []
    architecture: ArchitectureConfig
    database: DatabaseConfig
    api: ApiConfig
    ui: UIConfig
    auth: AuthConfig
    business_logic: BusinessLogicConfig
    integrations: IntegrationsConfig = Field(default_factory=lambda: IntegrationsConfig(services=[]))
    payments: PaymentsConfig = Field(default_factory=lambda: PaymentsConfig(enabled=False))
    notifications: NotificationsConfig = Field(default_factory=lambda: NotificationsConfig(enabled=False, templates=[]))
    analytics: AnalyticsConfig = Field(default_factory=lambda: AnalyticsConfig(enabled=False, provider="none", events=[]))
    feature_flags: FeatureFlagsConfig = Field(default_factory=lambda: FeatureFlagsConfig(flags=[]))
    validation_rules: ValidationRulesConfig = Field(default_factory=lambda: ValidationRulesConfig(cross_layer_rules=[]))
