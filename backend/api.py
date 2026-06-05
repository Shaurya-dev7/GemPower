import os
import json
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.services.compiler_service import CompilerService

app = FastAPI(title="AI Compiler API")

FRONTEND_URL = os.getenv("FRONTEND_URL", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

compiler_service = CompilerService()

class CompileRequest(BaseModel):
    prompt: str

@app.post("/api/compile")
def compile_prompt(req: CompileRequest):
    """
    Executes the full AI compiler pipeline and returns the structured stages.
    """
    # Enforce test mode for safe, instant demo simulation
    os.environ["TEST_MODE"] = "True"
    return compiler_service.compile(req.prompt)

@app.get("/api/metrics")
def get_metrics():
    """
    Returns the pre-calculated evaluation report.
    """
    report_path = "backend/evaluation/evaluation_report.json"
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            data = json.load(f)
            # Infer test mode if TEST_MODE env var is set, or if avg_tokens is very low
            is_test_env = os.environ.get("TEST_MODE") == "True"
            tokens = data.get("cost_analysis", {}).get("avg_tokens_per_request", 0)
            data["is_test_mode"] = is_test_env or (tokens < 1 and tokens > 0)
            return data
    return {"error": "Evaluation report not generated yet. Run 'python backend/evaluation/run_full_evaluation.py' first."}

@app.get("/runtime-preview")
def get_runtime_preview():
    """
    Serves the latest generated runtime preview HTML.
    """
    file_path = "runtime_preview.html"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse(status_code=404, content={"detail": "Not Found"})
