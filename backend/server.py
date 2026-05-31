"""Bull-AI Research backend.

Exposes standard HTTP REST API endpoints for the React frontend, 
an MCP (Model Context Protocol) SSE server for web integration,
and a stdio MCP server for agent subprocess execution.
"""
from __future__ import annotations

import logging
import os
import uuid
import base64
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware

from services.extractor import extract_many
from services.llm_extractor import extract_structured
from services.pdf_generator import build_pdf

from mcp.server.fastmcp import FastMCP

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ---- storage ------------------------------------------------------------
GENERATED_DIR = ROOT_DIR / "generated_reports"
GENERATED_DIR.mkdir(exist_ok=True)

# ---- Mongo --------------------------------------------------------------
mongo_url = os.environ["MONGO_URL"]
mongo_client = AsyncIOMotorClient(mongo_url)
db = mongo_client[os.environ["DB_NAME"]]

# ---- FastMCP Server -----------------------------------------------------
mcp = FastMCP("bull-ai-research")

@mcp.tool()
async def mcp_generate_report(company_name: str, files: list[dict]) -> dict:
    """
    Generate a retail equity research PDF report for a company from uploaded text/CSV documents.
    
    Arguments:
    - company_name: Name of the company to analyze (e.g. JSW Energy, ICICI Bank).
    - files: A list of dicts, each containing 'filename' (e.g. 'notes.txt', 'table.csv') and 'content' (the plain text content of the file).
    """
    if not company_name.strip():
        raise ValueError("company_name is required")
    if not files:
        raise ValueError("At least one document must be provided")

    blobs: list[tuple[str, bytes]] = []
    for f in files:
        filename = f.get("filename") or "upload.txt"
        content_str = f.get("content") or ""
        blobs.append((filename, content_str.encode("utf-8")))

    logger.info("[MCP] Extracting text from %d files for %s", len(blobs), company_name)
    raw_text = extract_many(blobs)
    if not raw_text.strip():
        raise ValueError("Could not extract any readable text from provided documents")

    logger.info("[MCP] Calling Groq for structured extraction…")
    try:
        structured = extract_structured(company_name, raw_text)
    except Exception as e:
        logger.exception("[MCP] LLM extraction failed")
        raise RuntimeError(f"LLM extraction failed: {e}")

    logger.info("[MCP] Building PDF…")
    pdf_bytes = build_pdf(structured)

    report_id = str(uuid.uuid4())
    out_path = GENERATED_DIR / f"{report_id}.pdf"
    out_path.write_bytes(pdf_bytes)

    backend_url = os.environ.get("PUBLIC_BACKEND_URL", "")
    download_url = f"{backend_url}/api/report/{report_id}/pdf" if backend_url else f"/api/report/{report_id}/pdf"

    record = {
        "id": report_id,
        "company_name": structured.get("company_name") or company_name,
        "report_title": structured.get("report_title"),
        "rating": structured.get("rating"),
        "target_price": structured.get("target_price"),
        "cmp": structured.get("cmp"),
        "sector": structured.get("sector"),
        "headline": structured.get("headline"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "file_size": len(pdf_bytes),
        "file_path": str(out_path),
    }
    await db.reports.insert_one(record.copy())

    return {
        "report_id": report_id,
        "company_name": record["company_name"],
        "rating": record["rating"],
        "target_price": record["target_price"],
        "headline": record.get("headline"),
        "download_url": download_url,
        "summary": {
            "sector": record["sector"],
            "report_title": record["report_title"],
            "cmp": record["cmp"],
        },
    }

@mcp.tool()
async def mcp_list_reports(limit: int = 20) -> list[dict]:
    """
    Retrieve a list of recently generated retail equity research reports.
    
    Arguments:
    - limit: Maximum number of recent reports to return (default is 20).
    """
    docs = await db.reports.find({}, {"_id": 0, "file_path": 0}).sort("created_at", -1).to_list(limit)
    return docs

@mcp.tool()
async def mcp_download_report(report_id: str) -> dict:
    """
    Download the generated PDF report bytes as a base64 encoded string.
    
    Arguments:
    - report_id: The unique UUID of the generated report.
    """
    path = GENERATED_DIR / f"{report_id}.pdf"
    if not path.exists():
        raise ValueError(f"Report with ID {report_id} not found")

    record = await db.reports.find_one({"id": report_id}, {"_id": 0})
    pdf_bytes = path.read_bytes()
    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

    return {
        "report_id": report_id,
        "company_name": record.get("company_name") if record else "Unknown",
        "created_at": record.get("created_at") if record else None,
        "pdf_base64": pdf_base64,
        "file_size": len(pdf_bytes),
    }

@mcp.tool()
async def mcp_health_check() -> dict:
    """
    Perform a system health check and verify Groq configuration.
    """
    return {
        "status": "ok",
        "service": "bull-ai-research",
        "groq_configured": bool(os.environ.get("GROQ_API_KEY")),
    }


# ---- FastAPI REST Server ------------------------------------------------
app = FastAPI(title="Bull-AI Research")
api = APIRouter(prefix="/api")

ALLOWED_EXTS = {".pdf", ".csv", ".txt", ".md", ".text"}


class ReportSummary(BaseModel):
    id: str
    company_name: str
    report_title: Optional[str] = None
    rating: Optional[str] = None
    target_price: Optional[str] = None
    cmp: Optional[str] = None
    sector: Optional[str] = None
    created_at: str
    file_size: int


class GenerateResponse(BaseModel):
    report_id: str
    company_name: str
    rating: Optional[str] = None
    target_price: Optional[str] = None
    headline: Optional[str] = None
    download_url: str
    summary: dict = Field(default_factory=dict)


@api.get("/health")
async def health():
    return await mcp_health_check()


@api.post("/generate-report", response_model=GenerateResponse)
async def generate_report(
    company_name: str = Form(...),
    files: List[UploadFile] = File(...),
):
    if not company_name.strip():
        raise HTTPException(400, "company_name is required")
    if not files:
        raise HTTPException(400, "at least one document must be uploaded")

    # Read files
    blobs: list[tuple[str, bytes]] = []
    for f in files:
        ext = Path(f.filename or "").suffix.lower()
        if ext not in ALLOWED_EXTS:
            raise HTTPException(400, f"Unsupported file type: {f.filename}. Allowed: PDF, CSV, TXT")
        content = await f.read()
        if len(content) > 25 * 1024 * 1024:
            raise HTTPException(400, f"{f.filename} exceeds 25MB limit")
        blobs.append((f.filename or "upload", content))

    logger.info("Extracting text from %d files for %s", len(blobs), company_name)
    raw_text = extract_many(blobs)
    if not raw_text.strip():
        raise HTTPException(400, "Could not extract any readable text from uploaded files")

    logger.info("Calling Groq for structured extraction…")
    try:
        structured = extract_structured(company_name, raw_text)
    except Exception as e:
        logger.exception("LLM extraction failed")
        raise HTTPException(502, f"LLM extraction failed: {e}")

    logger.info("Building PDF…")
    pdf_bytes = build_pdf(structured)

    report_id = str(uuid.uuid4())
    out_path = GENERATED_DIR / f"{report_id}.pdf"
    out_path.write_bytes(pdf_bytes)

    backend_url = os.environ.get("PUBLIC_BACKEND_URL", "")
    download_url = f"{backend_url}/api/report/{report_id}/pdf" if backend_url else f"/api/report/{report_id}/pdf"

    record = {
        "id": report_id,
        "company_name": structured.get("company_name") or company_name,
        "report_title": structured.get("report_title"),
        "rating": structured.get("rating"),
        "target_price": structured.get("target_price"),
        "cmp": structured.get("cmp"),
        "sector": structured.get("sector"),
        "headline": structured.get("headline"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "file_size": len(pdf_bytes),
        "file_path": str(out_path),
    }
    await db.reports.insert_one(record.copy())

    return GenerateResponse(
        report_id=report_id,
        company_name=record["company_name"],
        rating=record["rating"],
        target_price=record["target_price"],
        headline=record.get("headline"),
        download_url=download_url,
        summary={
            "sector": record["sector"],
            "report_title": record["report_title"],
            "cmp": record["cmp"],
        },
    )


@api.get("/report/{report_id}/pdf")
async def download_report(report_id: str):
    path = GENERATED_DIR / f"{report_id}.pdf"
    if not path.exists():
        raise HTTPException(404, "Report not found")
    return Response(
        content=path.read_bytes(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="bull-ai-{report_id[:8]}.pdf"'},
    )


@api.get("/reports", response_model=List[ReportSummary])
async def list_reports(limit: int = 20):
    docs = await db.reports.find({}, {"_id": 0, "file_path": 0}).sort("created_at", -1).to_list(limit)
    return [ReportSummary(**d) for d in docs]


app.include_router(api)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the MCP SSE Server endpoints under /mcp
app.mount("/mcp", mcp.sse_app())


@app.on_event("shutdown")
async def shutdown_db_client():
    mongo_client.close()


if __name__ == "__main__":
    import sys
    if "--mcp" in sys.argv or "mcp" in sys.argv:
        import asyncio
        logger.info("Starting Bull-AI Stdio MCP Server...")
        asyncio.run(mcp.run_stdio_async())
    else:
        import uvicorn
        port = int(os.environ.get("PORT", 8000))
        logger.info("Starting Bull-AI FastAPI server on port %d...", port)
        uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
