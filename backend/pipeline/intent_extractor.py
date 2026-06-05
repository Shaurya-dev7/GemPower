import os
import json
import re
import time
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
from backend.pipeline.prompts import EXTRACTION_SYSTEM_PROMPT, REPAIR_PROMPT

# File-based caching configuration
CACHE_FILE = "backend/pipeline/intent_cache.json"

# ---------------------------------------------------------------------------
# SYNONYM MAPS — each key is a canonical feature, values are trigger phrases
# ---------------------------------------------------------------------------
FEATURE_SYNONYMS = {
    "crm": {
        "contacts":      ["contacts", "contact management", "contact list", "address book"],
        "subscriptions": ["subscriptions", "subscription management", "plans", "membership"],
        "billing":       ["billing", "invoice", "invoices", "payment", "payments", "subscription billing", "charges"],
        "audit_logs":    ["audit", "audit logs", "audit log", "activity logs", "activity log", "compliance logs", "event log"],
        "rbac":          ["rbac", "roles", "permissions", "role based access", "role-based access", "access control"],
        "sso":           ["sso", "single sign on", "single sign-on", "oauth", "saml"],
        "reporting":     ["reporting", "reports", "analytics", "dashboards", "insights"],
        "workflows":     ["workflows", "workflow", "automation", "automations", "pipeline"],
        "dashboard":     ["dashboard", "admin panel", "control panel", "overview"],
        "multi_tenancy": ["multi tenant", "multi-tenant", "multitenancy", "multi tenancy", "tenant", "tenants"],
        "authentication":["authentication", "login", "signup", "sign up", "sign in", "auth", "register"],
    },
    "marketplace": {
        "profiles":      ["profiles", "profile", "freelancer profiles", "user profiles"],
        "projects":      ["projects", "project", "jobs", "job listings", "gigs"],
        "proposals":     ["proposals", "proposal", "bids", "bid", "bidding"],
        "billing":       ["billing", "invoice", "payment", "payments", "escrow"],
        "clients":       ["clients", "client", "buyers", "employers"],
        "freelancers":   ["freelancers", "freelancer", "sellers", "providers", "talent"],
        "messaging":     ["messaging", "messages", "chat", "communication"],
        "reviews":       ["reviews", "review", "ratings", "feedback"],
        "search":        ["search", "browse", "discover", "find"],
        "dashboard":     ["dashboard", "admin panel", "overview"],
    },
    "school": {
        "student_roster":     ["student", "students", "student roster", "student management", "enrollment"],
        "grading_sheets":     ["grading", "grades", "grade", "grading sheets", "marks", "marksheet", "report card"],
        "attendance":         ["attendance", "attendance tracking", "presence", "absence"],
        "teacher_management": ["teacher", "teachers", "teacher management", "staff", "faculty"],
        "parent_portal":      ["parent", "parents", "parent portal", "guardian", "guardians"],
        "timetable":          ["timetable", "schedule", "class schedule", "periods"],
        "examinations":       ["exam", "exams", "examination", "examinations", "tests"],
        "dashboard":          ["dashboard", "admin panel", "overview"],
    },
}

# Maps canonical features to the entities they produce
FEATURE_ENTITY_MAP = {
    "crm": {
        "contacts": ["contact"],
        "subscriptions": ["subscription"],
        "billing": ["invoice", "payment"],
        "audit_logs": ["audit_entry"],
        "rbac": ["role", "permission"],
        "sso": ["sso_session"],
        "reporting": ["report"],
        "workflows": ["workflow"],
        "dashboard": [],
        "multi_tenancy": ["tenant"],
        "authentication": ["user"],
    },
    "marketplace": {
        "profiles": ["freelancer"],
        "projects": ["project"],
        "proposals": ["proposal"],
        "billing": ["invoice"],
        "clients": ["client"],
        "freelancers": ["freelancer"],
        "messaging": ["message"],
        "reviews": ["review"],
        "search": [],
        "dashboard": [],
    },
    "school": {
        "student_roster": ["student"],
        "grading_sheets": ["grade"],
        "attendance": ["attendance"],
        "teacher_management": ["teacher"],
        "parent_portal": ["parent"],
        "timetable": ["timetable"],
        "examinations": ["exam"],
        "dashboard": [],
    },
}

# Negative / exclusion keywords
NEGATIVE_PATTERNS = [
    r"don'?t\s+allow\s+(\w+)",
    r"no\s+(\w+)",
    r"without\s+(\w+)",
    r"disable\s+(\w+)",
    r"exclude\s+(\w+)",
    r"remove\s+(\w+)",
    r"block\s+(\w+)",
]


def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache: dict):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


class IntentExtractor:
    """
    Compiler Stage 1: Intent Extractor
    Converts raw natural language into a strictly validated IntentConfig.
    Supports Single-Call Architecture, Exponential Backoff, Caching, and Test Mode.
    """
    def __init__(self):
        self.test_mode = os.getenv("TEST_MODE", "False").lower() in ("true", "1", "yes")
        
        # Instantiate client only if not in test mode
        if not self.test_mode:
            self.client = genai.Client()
            self.model_name = "gemini-2.5-flash"
        else:
            self.client = None
            self.model_name = "mock-model"
            
        self.cache = load_cache()

    def _call_gemini_with_backoff(self, prompt: str, is_repair: bool = False, error_msg: str = "", raw_json: str = "") -> str:
        """Call Gemini API utilizing Exponential Backoff for 429/503 errors."""
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                system_content = REPAIR_PROMPT.format(error_msg=error_msg, raw_json=raw_json) if is_repair else EXTRACTION_SYSTEM_PROMPT
                contents = f"{system_content}\n\nInput Prompt:\n{prompt}"
                
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                return response.text
            except APIError as e:
                # Catch 429 / 503 rate/demand errors
                if e.code in (429, 503) and attempt < max_attempts - 1:
                    sleep_time = 2 ** attempt
                    print(f"    [API Warning] Received {e.code}. Backing off for {sleep_time}s...", flush=True)
                    time.sleep(sleep_time)
                else:
                    raise e
            except Exception as e:
                if attempt < max_attempts - 1:
                    sleep_time = 2 ** attempt
                    time.sleep(sleep_time)
                else:
                    raise e
        raise RuntimeError("API failed after maximum backoff attempts.")

    def _calculate_confidence(self, prompt: str, assumptions: list, missing_information: list) -> float:
        base = min(0.9, 0.4 + (len(prompt.split()) * 0.05))
        penalty = (len(assumptions) * 0.05) + (len(missing_information) * 0.1)
        confidence = base - penalty
        return max(0.3, min(0.98, round(confidence, 2)))

    def _detect_domain(self, prompt_lower: str) -> str:
        """Detect the primary application domain from the prompt."""
        if "crm" in prompt_lower:
            return "crm"
        elif any(kw in prompt_lower for kw in ["marketplace", "freelancer", "freelancers", "gig"]):
            return "marketplace"
        elif any(kw in prompt_lower for kw in ["school", "teacher", "student", "classroom", "education"]):
            return "school"
        elif any(kw in prompt_lower for kw in ["ecommerce", "e-commerce", "store", "shop"]):
            return "ecommerce"
        return "generic"

    def _scan_features(self, prompt_lower: str, domain: str) -> list:
        """Scan prompt for feature keywords using synonym map. Returns list of canonical feature names."""
        synonym_map = FEATURE_SYNONYMS.get(domain, {})
        found_features = []
        for canonical, synonyms in synonym_map.items():
            for syn in synonyms:
                if syn in prompt_lower:
                    if canonical not in found_features:
                        found_features.append(canonical)
                    break
        return found_features

    def _scan_entities(self, features: list, domain: str) -> list:
        """Derive entities from detected features."""
        entity_map = FEATURE_ENTITY_MAP.get(domain, {})
        entities = []
        for feature in features:
            for ent in entity_map.get(feature, []):
                if ent not in entities:
                    entities.append(ent)
        return entities

    def _extract_negative_requirements(self, prompt_lower: str) -> tuple:
        """Extract forbidden features/entities from negative phrases in the prompt."""
        forbidden_features = []
        forbidden_entities = []
        for pattern in NEGATIVE_PATTERNS:
            matches = re.findall(pattern, prompt_lower)
            for match in matches:
                match = match.strip().rstrip("s")  # normalize plural
                if match not in forbidden_features:
                    forbidden_features.append(match)
                    forbidden_entities.append(match)
        return forbidden_features, forbidden_entities

    def _get_mock_response(self, prompt: str) -> dict:
        """Prompt-aware mock response with synonym scanning and negative requirement support."""
        p_lower = prompt.lower()
        domain = self._detect_domain(p_lower)

        # --- Negative requirements ---
        forbidden_features, forbidden_entities = self._extract_negative_requirements(p_lower)

        # --- Domain: CRM ---
        if domain == "crm":
            features = self._scan_features(p_lower, "crm")
            # Ensure minimum baseline features
            for base in ["authentication", "contacts", "dashboard"]:
                if base not in features:
                    features.append(base)
            entities = self._scan_entities(features, "crm")
            if "user" not in entities:
                entities.append("user")
            assumptions = []
            missing = []
            if "billing" in features:
                assumptions.append("Stripe is preferred payment processor")
            if "sso" in features:
                assumptions.append("OAuth 2.0 provider assumed")
            if len(features) <= 3:
                missing.append("detailed workflow specifications")
            roles = ["admin", "user"]
            if "rbac" in features:
                roles.extend(["manager", "viewer"])
            if "multi_tenancy" in features:
                roles.append("tenant_admin")
            biz_reqs = ["role_based_access"]
            if "multi_tenancy" in features:
                biz_reqs.append("tenant_isolation")
            if "billing" in features:
                biz_reqs.append("payment_processing")

            return self._build_response(
                domain="crm", prompt=prompt, features=features, entities=entities,
                roles=roles, biz_reqs=biz_reqs, assumptions=assumptions,
                missing=missing, forbidden_features=forbidden_features,
                forbidden_entities=forbidden_entities,
                normalized=f"A CRM application with {', '.join(features)}."
            )

        # --- Domain: Marketplace (with seller exclusion) ---
        elif domain == "marketplace":
            # Check for "no seller" variant
            is_no_seller = "seller" in forbidden_features or any(
                kw in p_lower for kw in ["don't allow seller", "no seller", "without seller"]
            )
            if is_no_seller and "seller" not in forbidden_features:
                forbidden_features.append("seller")
                forbidden_entities.append("seller")

            features = self._scan_features(p_lower, "marketplace")
            if not features:
                features = ["profiles", "projects", "proposals"]
            entities = self._scan_entities(features, "marketplace")

            if is_no_seller:
                # Remove seller-related items
                features = [f for f in features if "seller" not in f.lower()]
                entities = [e for e in entities if "seller" not in e.lower()]
                roles = ["client", "freelancer"]
                biz_reqs = ["no_sellers_allowed", "escrow_protection"]
                assumptions = ["Free exchange model without dedicated sellers"]
            else:
                roles = ["client", "freelancer", "admin"]
                biz_reqs = ["escrow_protection"]
                assumptions = ["Stripe escrow for payment"]

            return self._build_response(
                domain="marketplace", prompt=prompt, features=features, entities=entities,
                roles=roles, biz_reqs=biz_reqs, assumptions=assumptions,
                missing=[], forbidden_features=forbidden_features,
                forbidden_entities=forbidden_entities,
                normalized=f"Freelancer marketplace with {', '.join(features)}."
            )

        # --- Domain: School ---
        elif domain == "school":
            features = self._scan_features(p_lower, "school")
            if not features:
                features = ["student_roster", "grading_sheets", "attendance"]
            # Ensure minimum for school domain
            for base in ["student_roster", "grading_sheets", "attendance", "teacher_management", "parent_portal"]:
                if base not in features:
                    features.append(base)
            entities = self._scan_entities(features, "school")
            roles = ["admin", "teacher", "student", "parent"]
            assumptions = ["US K-12 style"]
            missing = ["grading scale details"]
            biz_reqs = ["grade_gating", "attendance_tracking"]

            return self._build_response(
                domain="school_management", prompt=prompt, features=features, entities=entities,
                roles=roles, biz_reqs=biz_reqs, assumptions=assumptions,
                missing=missing, forbidden_features=forbidden_features,
                forbidden_entities=forbidden_entities,
                normalized=f"School management platform with {', '.join(features)}."
            )

        # --- Domain: E-commerce ---
        elif domain == "ecommerce":
            features = ["catalog", "cart", "payment", "authentication"]
            entities = ["product", "order", "user", "cart"]
            roles = ["shopper", "admin"]
            assumptions = []
            missing = []
            biz_reqs = ["payment_processing"]

            return self._build_response(
                domain="ecommerce", prompt=prompt, features=features, entities=entities,
                roles=roles, biz_reqs=biz_reqs, assumptions=assumptions,
                missing=missing, forbidden_features=forbidden_features,
                forbidden_entities=forbidden_entities,
                normalized="E-commerce store with product catalog, cart, and payment."
            )

        # --- Fallback: Generic ---
        else:
            features = ["home", "authentication"]
            entities = ["item", "user"]
            roles = ["user"]
            assumptions = []
            missing = ["core app logic"]
            biz_reqs = []

            return self._build_response(
                domain="utility", prompt=prompt, features=features, entities=entities,
                roles=roles, biz_reqs=biz_reqs, assumptions=assumptions,
                missing=missing, forbidden_features=forbidden_features,
                forbidden_entities=forbidden_entities,
                normalized="Generic application utility."
            )

    def _build_response(self, domain: str, prompt: str, features: list, entities: list,
                        roles: list, biz_reqs: list, assumptions: list, missing: list,
                        forbidden_features: list, forbidden_entities: list,
                        normalized: str) -> dict:
        """Build the structured mock response with coverage metrics."""
        # Filter out forbidden items
        features = [f for f in features if not any(fb in f.lower() for fb in forbidden_features)]
        entities = [e for e in entities if not any(fb in e.lower() for fb in forbidden_entities)]

        # Deduplicate
        features = list(dict.fromkeys(features))
        entities = list(dict.fromkeys(entities))
        roles = list(dict.fromkeys(roles))

        confidence = self._calculate_confidence(prompt, assumptions, missing)

        return {
            "normalized_requirements": normalized,
            "intent_config": {
                "app_type": domain,
                "features": features,
                "roles": roles,
                "entities": entities,
                "business_requirements": biz_reqs,
                "confidence": confidence,
                "assumptions": assumptions,
                "missing_information": missing,
                "forbidden_features": forbidden_features,
                "forbidden_entities": forbidden_entities,
            },
            "coverage": {
                "requested_features": len(features),
                "implemented_features": len(features),
                "coverage_score": 100,
            }
        }

    def extract_intent(self, raw_prompt: str, max_retries: int = 2) -> tuple[IntentConfig, bool, float]:
        """
        Single-call extraction pipeline with Caching, Backoff, and Test Mode.
        """
        start_time = time.time()
        
        # 1. Cache Check
        if raw_prompt in self.cache:
            print("    [Cache Hit] Returning cached intent.", flush=True)
            cached_data = self.cache[raw_prompt]
            intent_config = IntentConfig(**cached_data["intent_config"])
            return intent_config, False, time.time() - start_time
            
        # 2. Test Mode Check
        if self.test_mode:
            mock_data = self._get_mock_response(raw_prompt)
            intent_config = IntentConfig(**mock_data["intent_config"])
            # Save to runtime memory cache
            self.cache[raw_prompt] = mock_data
            save_cache(self.cache)
            return intent_config, False, time.time() - start_time

        # 3. Direct Single API Call
        raw_json_str = self._call_gemini_with_backoff(raw_prompt)
        was_repaired = False
        
        # Validation & Repair Loop
        for attempt in range(max_retries + 1):
            try:
                # Clean Markdown if LLM wrapping occurred
                if raw_json_str.strip().startswith("```"):
                    lines = raw_json_str.strip().split("\n")
                    if lines[0].startswith("```"): lines = lines[1:]
                    if lines[-1].startswith("```"): lines = lines[:-1]
                    raw_json_str = "\n".join(lines).strip()
                    
                parsed_json = json.loads(raw_json_str)
                
                # Check envelope structure
                if "intent_config" not in parsed_json:
                    raise KeyError("Missing 'intent_config' wrapper in response envelope.")
                
                # Validate intent config matching Pydantic (Layer 2)
                intent_config = IntentConfig(**parsed_json["intent_config"])
                
                # 4. Save to Cache on success
                self.cache[raw_prompt] = parsed_json
                save_cache(self.cache)
                
                latency = time.time() - start_time
                return intent_config, was_repaired, latency
                
            except (json.JSONDecodeError, ValidationError, KeyError) as e:
                if attempt == max_retries:
                    raise RuntimeError(f"Failed to extract and parse intent. Error: {str(e)}")
                
                was_repaired = True
                print(f"    [Repairing] Validation failed: {str(e)}. Triggering repair pass...", flush=True)
                raw_json_str = self._call_gemini_with_backoff(
                    raw_prompt, is_repair=True, error_msg=str(e), raw_json=raw_json_str
                )
                
        raise RuntimeError("Unexpected failure in extraction loop.")
