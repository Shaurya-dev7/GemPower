from backend.schemas.schema_bundle import SchemaBundle
from backend.schemas.runtime_application import RuntimeApplication
from backend.runtime.page_renderer import PageRenderer
from backend.runtime.form_renderer import FormRenderer
from backend.runtime.table_renderer import TableRenderer
from backend.runtime.navigation_builder import NavigationBuilder
from backend.runtime.route_registry import RouteRegistry
from backend.runtime.permission_resolver import PermissionResolver
from backend.runtime.api_binding_engine import ApiBindingEngine

class RuntimeEngine:
    def __init__(self):
        self.page_renderer = PageRenderer()
        self.form_renderer = FormRenderer()
        self.table_renderer = TableRenderer()
        self.nav_builder = NavigationBuilder()
        self.route_registry = RouteRegistry()
        self.perm_resolver = PermissionResolver()
        self.binding_engine = ApiBindingEngine()

    def compile(self, bundle: SchemaBundle) -> RuntimeApplication:
        # 1. Render Pages, Forms, Tables
        pages = self.page_renderer.render(bundle.ui)
        forms = self.form_renderer.render(bundle.ui)
        tables = self.table_renderer.render(bundle.database)
        
        # 2. Build Navigation & Routes
        nav = self.nav_builder.build(bundle.ui)
        routes = self.route_registry.register(bundle.ui)
        
        # 3. Resolve Permissions
        permissions = self.perm_resolver.resolve(bundle.auth)
        
        # 4. Bind APIs
        bindings = self.binding_engine.bind(bundle.api, forms, tables)
        
        app = RuntimeApplication(
            pages=pages,
            navigation=nav,
            routes=routes,
            forms=forms,
            tables=tables,
            permissions=permissions,
            api_bindings=bindings
        )
        app.runtime_hash = app.compute_hash()
        return app
