# backend/app/models/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class LogSubmissionRequest(BaseModel):
    logs: Optional[str] = None
    code_snippet: Optional[str] = None
    platform: str  # e.g., "iOS", "Android", "Backend"
    language: str  # e.g., "Swift", "Kotlin", "Python", "Java"

class BugPrediction(BaseModel):
    type: str
    description: str
    severity: str  # e.g., "Low", "Medium", "High", "Critical"
    confidence: float  # 0.0 to 1.0

class SuggestedPatch(BaseModel):
    description: str
    code_diff: str  # Markdown formatted code diff

class AnalysisResult(BaseModel):
    analysis_id: str
    status: str  # e.g., "QUEUED", "IN_PROGRESS", "COMPLETED", "FAILED"
    predicted_bugs: List[BugPrediction] = []
    suggested_patches: List[SuggestedPatch] = []
    error_message: Optional[str] = None