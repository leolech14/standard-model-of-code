#!/usr/bin/env python3
"""
SPECTROMETER API REST - FastAPI Server
Endpoints para análise de arquitetura on-demand
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import tempfile
import shutil
import asyncio
import uuid
from pathlib import Path
from datetime import datetime
import json
from spectrometer_v9_raw_haiku import SpectrometerV9

# ============== API MODELS ==============

class AnalysisRequest(BaseModel):
    """Model para requisição de análise"""
    repository_url: Optional[str] = None
    code_content: Optional[str] = None
    language: Optional[str] = None
    include_haiku: bool = True
    include_validation: bool = True

class AnalysisResponse(BaseModel):
    """Model para resposta da análise"""
    request_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    metrics: Optional[Dict[str, Any]] = None
    elements: Optional[List[Dict]] = None
    v9_score: Optional[float] = None
    error: Optional[str] = None

class AnalysisStatus(BaseModel):
    """Status da análise"""
    request_id: str
    status: str  # pending, running, completed, failed
    progress: float  # 0-100
    current_file: Optional[str] = None
    files_processed: int = 0
    total_files: Optional[int] = None

# ============== API STATE ==============

app = FastAPI(
    title="Spectrometer API",
    description="REST API para análise de arquitetura de código - Standard Model do Código",
    version="9.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS para frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estado global (em produção, usar Redis/DB)
analysis_jobs: Dict[str, Dict] = {}
spectrometer = SpectrometerV9()

# ============== ENDPOINTS PRINCIPAIS ==============

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página inicial com documentação"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Spectrometer API - Standard Model do Código</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; color: #2563eb; margin-bottom: 30px; }
            .endpoint { background: #f3f4f6; padding: 15px; margin: 10px 0; border-radius: 8px; }
            .method { color: #059669; font-weight: bold; }
            .version { color: #6b7280; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Spectrometer API v9.0</h1>
            <p>Análise de arquitetura com Standard Model do Código</p>
            <p class="version">RAW + HAIKU + VALENCE Engine</p>
        </div>

        <h2>📊 Endpoints Disponíveis</h2>

        <div class="endpoint">
            <span class="method">POST</span> /api/v1/analyze
            <br>Analisar repositório ou código
        </div>

        <div class="endpoint">
            <span class="method">POST</span> /api/v1/analyze/upload
            <br>Upload de arquivo para análise
        </div>

        <div class="endpoint">
            <span class="method">GET</span> /api/v1/status/{{request_id}}
            <br>Status da análise
        </div>

        <div class="endpoint">
            <span class="method">GET</span> /api/v1/result/{{request_id}}
            <br>Resultado completo da análise
        </div>

        <div class="endpoint">
            <span class="method">GET</span> /docs
            <br>Documentação interativa (Swagger)
        </div>

        <p style="text-align: center; margin-top: 30px;">
            <a href="/docs" style="background: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Ver Documentação Completa
            </a>
        </p>
    </body>
    </html>
    """

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "9.0.0",
        "engine": "RAW + HAIKU + VALENCE",
        "timestamp": datetime.now().isoformat(),
        "active_jobs": len(analysis_jobs)
    }

@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_repository(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Inicia análise de repositório ou código"""
    request_id = str(uuid.uuid4())

    # Validação
    if not request.repository_url and not request.code_content:
        raise HTTPException(status_code=400, detail="Fornecer URL do repositório OU conteúdo do código")

    # Cria job
    job = {
        "id": request_id,
        "status": "pending",
        "started_at": datetime.now(),
        "completed_at": None,
        "request": request.dict(),
        "result": None,
        "error": None
    }

    analysis_jobs[request_id] = job

    # Executa análise em background
    background_tasks.add_task(run_analysis, request_id)

    return AnalysisResponse(
        request_id=request_id,
        status="pending",
        started_at=job["started_at"]
    )

@app.post("/api/v1/analyze/upload", response_model=AnalysisResponse)
async def analyze_uploaded_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: Optional[str] = None
):
    """Upload e análise de arquivo"""
    request_id = str(uuid.uuid4())

    # Salva arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    # Cria job
    job = {
        "id": request_id,
        "status": "pending",
        "started_at": datetime.now(),
        "completed_at": None,
        "file_path": str(tmp_path),
        "language": language,
        "result": None,
        "error": None
    }

    analysis_jobs[request_id] = job

    # Executa análise
    background_tasks.add_task(run_file_analysis, request_id)

    return AnalysisResponse(
        request_id=request_id,
        status="pending",
        started_at=job["started_at"]
    )

@app.get("/api/v1/status/{request_id}", response_model=AnalysisStatus)
async def get_analysis_status(request_id: str):
    """Status da análise"""
    if request_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Análise não encontrada")

    job = analysis_jobs[request_id]

    return AnalysisStatus(
        request_id=request_id,
        status=job["status"],
        progress=job.get("progress", 0),
        current_file=job.get("current_file"),
        files_processed=job.get("files_processed", 0),
        total_files=job.get("total_files")
    )

@app.get("/api/v1/result/{request_id}")
async def get_analysis_result(request_id: str):
    """Resultado completo da análise"""
    if request_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Análise não encontrada")

    job = analysis_jobs[request_id]

    if job["status"] == "pending" or job["status"] == "running":
        return {"status": job["status"], "message": "Análise em andamento"}

    if job["status"] == "failed":
        return {
            "status": "failed",
            "error": job["error"],
            "started_at": job["started_at"].isoformat()
        }

    # Análise concluída
    return {
        "status": "completed",
        "request_id": request_id,
        "started_at": job["started_at"].isoformat(),
        "completed_at": job["completed_at"].isoformat(),
        "metrics": job["result"].get("metrics", {}),
        "elements": job["result"].get("classified_elements", []),
        "v9_score": job["result"].get("metrics", {}).get("v9_score"),
        "summary": {
            "total_elements": len(job["result"].get("classified_elements", [])),
            "haiku_classifications": job["result"].get("metrics", {}).get("haiku_classifications", 0),
            "confidence": job["result"].get("metrics", {}).get("average_confidence", 0)
        }
    }

@app.get("/api/v1/jobs")
async def list_all_jobs():
    """Lista todos os jobs (admin)"""
    return {
        "total_jobs": len(analysis_jobs),
        "active_jobs": len([j for j in analysis_jobs.values() if j["status"] in ["pending", "running"]]),
        "jobs": [
            {
                "id": job_id,
                "status": job["status"],
                "started_at": job["started_at"].isoformat()
            }
            for job_id, job in analysis_jobs.items()
        ]
    }

@app.delete("/api/v1/jobs/{request_id}")
async def delete_job(request_id: str):
    """Cancela/remove job"""
    if request_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job não encontrado")

    del analysis_jobs[request_id]
    return {"message": "Job removido com sucesso"}

# ============== BACKGROUND TASKS ==============

async def run_analysis(request_id: str):
    """Executa análise de repositório"""
    job = analysis_jobs[request_id]
    job["status"] = "running"
    job["progress"] = 10

    try:
        request = job["request"]

        if request["code_content"]:
            # Análise de código direto
            job["progress"] = 30
            result = await analyze_code_content(
                request["code_content"],
                request.get("language"),
                request.get("include_haiku", True),
                request.get("include_validation", True)
            )
            job["progress"] = 90
        else:
            # Análise de repositório URL
            # TODO: Implementar clone de repo
            raise NotImplementedError("Análise de URL ainda não implementada")

        job["result"] = result
        job["status"] = "completed"
        job["completed_at"] = datetime.now()
        job["progress"] = 100

    except Exception as e:
        job["error"] = str(e)
        job["status"] = "failed"
        job["completed_at"] = datetime.now()

async def run_file_analysis(request_id: str):
    """Executa análise de arquivo uploadado"""
    job = analysis_jobs[request_id]
    job["status"] = "running"
    job["progress"] = 10

    try:
        file_path = Path(job["file_path"])
        job["current_file"] = file_path.name
        job["files_processed"] = 1
        job["total_files"] = 1
        job["progress"] = 50

        # Analisa com Spectrometer V9
        result = spectrometer.analyze_file(file_path)

        # Converte para formato serializável
        serializable_result = {
            "metrics": result.metrics,
            "classified_elements": [
                {
                    "name": elem["name"],
                    "type": elem["type"],
                    "hadron": elem["hadron"],
                    "haiku": elem["haiku"].name if elem.get("haiku") else None,
                    "confidence": elem["confidence"],
                    "line": elem["line"],
                    "source": elem["source"],
                    "validation_issues": elem.get("validation_issues", [])
                }
                for elem in result.classified_elements
            ]
        }

        job["result"] = serializable_result
        job["status"] = "completed"
        job["completed_at"] = datetime.now()
        job["progress"] = 100

        # Limpa arquivo temporário
        file_path.unlink()

    except Exception as e:
        job["error"] = str(e)
        job["status"] = "failed"
        job["completed_at"] = datetime.now()

        # Limpa arquivo temporário
        try:
            Path(job["file_path"]).unlink()
        except:
            pass

async def analyze_code_content(code: str, language: Optional[str], include_haiku: bool, include_validation: bool) -> Dict:
    """Analisa conteúdo de código string"""
    # Cria arquivo temporário
    suffix = ".py"  # Default para Python
    if language:
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "java": ".java",
            "go": ".go",
            "rust": ".rs"
        }
        suffix = extensions.get(language.lower(), suffix)

    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as tmp:
        tmp.write(code)
        tmp_path = Path(tmp.name)

    try:
        # Analisa
        result = spectrometer.analyze_file(tmp_path)

        # Converte para formato serializável
        return {
            "metrics": result.metrics,
            "classified_elements": [
                {
                    "name": elem["name"],
                    "type": elem["type"],
                    "hadron": elem["hadron"],
                    "haiku": elem["haiku"].name if elem.get("haiku") else None,
                    "confidence": elem["confidence"],
                    "line": elem["line"],
                    "source": elem["source"],
                    "validation_issues": elem.get("validation_issues", [])
                }
                for elem in result.classified_elements
            ]
        }
    finally:
        # Limpa
        tmp_path.unlink()

# ============== MIDDLEWARE DE LOGGING ==============

@app.middleware("http")
async def log_requests(request, call_next):
    """Log de requisições"""
    start_time = datetime.now()

    response = await call_next(request)

    process_time = (datetime.now() - start_time).total_seconds()

    # Log simples (em produção usar logging configurado)
    if request.url.path.startswith("/api/"):
        print(f"{datetime.now().isoformat()} | {request.method} {request.url.path} | {response.status_code} | {process_time:.3f}s")

    return response

# ============== INICIAÇÃO ==============

if __name__ == "__main__":
    import uvicorn

    print("\n🚀 SPECTROMETER API REST v9.0")
    print("=" * 50)
    print("📊 Engine: RAW + HAIKU + VALENCE")
    print("🌐 Docs: http://localhost:8000/docs")
    print("🌐 ReDoc: http://localhost:8000/redoc")
    print("🌐 Health: http://localhost:8000/api/v1/health")
    print("=" * 50)

    uvicorn.run(
        "spectrometer_api_rest:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
