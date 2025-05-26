from fastapi import APIRouter, HTTPException, BackgroundTasks, Response, status
from typing import Dict, Optional
import uuid

from app.models.schemas import LogSubmissionRequest, AnalysisResult
from app.services.analysis_orchestrator import AnalysisOrchestrator

router = APIRouter()

analysis_orchestrator = AnalysisOrchestrator()

@router.post("/analyze-logs", response_model=Dict[str, str], status_code=status.HTTP_202_ACCEPTED)
async def analyze_logs(request: LogSubmissionRequest, background_tasks: BackgroundTasks, response: Response):
    if not request.logs and not request.code_snippet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'logs' or 'code_snippet' must be provided."
        )
    analysis_id = analysis_orchestrator.start_analysis_background(
        logs=request.logs,
        code_snippet=request.code_snippet,
        platform=request.platform or "",
        language=request.language or ""
    )
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'; sandbox"
    response.headers["Referrer-Policy"] = "no-referrer"
    return {"analysis_id": analysis_id, "status": "QUEUED"}


@router.get("/status/{analysis_id}", response_model=Optional[AnalysisResult])
async def get_analysis_status(analysis_id: str, response: Response):
    result = analysis_orchestrator.get_analysis_results(analysis_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis ID not found or expired")
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'; sandbox"
    response.headers["Referrer-Policy"] = "no-referrer"
    return result
