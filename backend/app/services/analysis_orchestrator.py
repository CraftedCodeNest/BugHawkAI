# backend/app/services/analysis_orchestrator.py
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

from app.models.schemas import BugPrediction, SuggestedPatch, AnalysisResult, LogSubmissionRequest

from app.services.llm_service import LLMService
from app.services.static_analysis_service import StaticAnalysisService
from app.utils.log_parser import LogParser

logger = logging.getLogger(__name__)

class AnalysisOrchestrator:
    """
    Orchestrates the entire analysis workflow:
    1. Parses logs.
    2. Runs static analysis (if code provided).
    3. Uses LLM for bug prediction.
    4. Uses LLM for patch suggestion.
    5. Stores results in the database.
    """
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service if llm_service else LLMService()
        self.static_analysis_service = StaticAnalysisService()
        self.log_parser = LogParser()
        self._in_memory_results: Dict[str, AnalysisResult] = {}

    def start_analysis_background(
        self, logs: Optional[str], code_snippet: Optional[str], platform: str, language: str
    ) -> str:
        analysis_id = str(uuid.uuid4())
        initial_report = AnalysisResult(
            analysis_id=analysis_id,
            status="QUEUED",
            predicted_bugs=[],
            suggested_patches=[],
            error_message=None
        )
        self._in_memory_results[analysis_id] = initial_report

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(
                self._perform_analysis(analysis_id, logs, code_snippet, platform, language)
            )
        except RuntimeError:
            asyncio.run(self._perform_analysis(analysis_id, logs, code_snippet, platform, language))

        return analysis_id

    async def _perform_analysis(
        self, analysis_id: str, logs: Optional[str], code_snippet: Optional[str], platform: str, language: str
    ):
        try:
            logger.info(f"Starting detailed analysis for ID: {analysis_id}")
            self._update_in_memory_report(analysis_id=analysis_id, status="IN_PROGRESS", error_message="Performing analysis...")

            predicted_bugs: List[BugPrediction] = []
            suggested_patches: List[SuggestedPatch] = []

            parsed_log_summary = self.log_parser.parse(logs) if logs else "No logs provided."

            static_analysis_findings = []
            if code_snippet:
                logger.info(f"Running static analysis for {language}...")
                if language.lower() in ["python", "swift", "ios", "kotlin", "android", "java"]:
                    static_analysis_findings = await self.static_analysis_service.run_analysis(code_snippet, language)
                else:
                    static_analysis_findings = []

                for finding in static_analysis_findings:
                    predicted_bugs.append(BugPrediction(
                        type=f"StaticAnalysis_{finding.get('rule', finding.get('check', 'Generic'))}",
                        description=finding.get('reason', finding.get('message', 'Static analysis issue.')),
                        severity="Medium",
                        location=f"{finding.get('file', 'N/A')}:{finding.get('line', 'N/A')}",
                        confidence=0.7,
                        explanation=f"Detected by static analysis tool. Rule: {finding.get('rule', finding.get('check', 'N/A'))}"
                    ))

            if logs or code_snippet:
                logger.info("Running LLM for bug prediction...")
                if hasattr(self.llm_service, "mock_predict_bug_from_logs"):
                    llm_bug_predictions = await self.llm_service.mock_predict_bug_from_logs(logs, code_snippet)
                else:
                    llm_bug_predictions = await self.llm_service.predict_bug_from_logs(logs, code_snippet)
                for bug in llm_bug_predictions:
                    predicted_bugs.append(BugPrediction(**bug))

            if predicted_bugs:
                logger.info("Running LLM for patch suggestion...")
                top_bug = sorted(predicted_bugs, key=lambda b: b.confidence, reverse=True)[0]
                if top_bug and code_snippet:
                    if hasattr(self.llm_service, "mock_suggest_patch_for_bug"):
                        llm_patch_suggestions = await self.llm_service.mock_suggest_patch_for_bug(top_bug.description, code_snippet, language)
                    else:
                        llm_patch_suggestions = await self.llm_service.suggest_patch_for_bug(top_bug.description, code_snippet, language)
                    for patch in llm_patch_suggestions:
                        suggested_patches.append(SuggestedPatch(**patch))

            final_report = AnalysisResult(
                analysis_id=analysis_id,
                status="COMPLETED",
                error_message=None,
                predicted_bugs=predicted_bugs,
                suggested_patches=suggested_patches,
            )
            report_dict = final_report.dict()
            if 'analysis_id' in report_dict:
                del report_dict['analysis_id']
            self._update_in_memory_report(analysis_id=analysis_id, **report_dict)
            logger.info(f"Analysis {analysis_id} completed.")

        except Exception as e:
            logger.error(f"Analysis {analysis_id} failed: {e}", exc_info=True)
            self._update_in_memory_report(analysis_id=analysis_id, status="FAILED", error_message=f"Analysis failed: {str(e)}")

    def get_analysis_results(self, analysis_id: str) -> Optional[AnalysisResult]:
        return self._in_memory_results.get(analysis_id)

    def _update_in_memory_report(self, analysis_id: str, **kwargs):
        if analysis_id in self._in_memory_results:
            existing_report = self._in_memory_results[analysis_id]
            updated_data = existing_report.dict(exclude_unset=True)
            updated_data.update(kwargs)
            if 'analysis_id' in updated_data:
                del updated_data['analysis_id']
            self._in_memory_results[analysis_id] = AnalysisResult(analysis_id=analysis_id, **updated_data)
