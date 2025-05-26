import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import asyncio
from unittest.mock import AsyncMock

from app.services.analysis_orchestrator import AnalysisOrchestrator
from app.models.schemas import BugPrediction, SuggestedPatch

class MockLLMService:
    async def mock_predict_bug_from_logs(self, logs, code_snippet):
        return [
            {
                "type": "MockBug",
                "description": "Mock bug detected",
                "severity": "High",
                "location": "mockfile.py:10",
                "confidence": 0.9,
                "explanation": "This is a mock bug prediction."
            }
        ]

    async def mock_suggest_patch_for_bug(self, bug_description, code_snippet, language):
        return [
            {
                "code_diff": "Mock patch suggestion",
                "description": "This is a mock patch suggestion."
            }
        ]

@pytest.mark.asyncio
async def test_analysis_orchestrator_with_mocks():
    mock_llm_service = MockLLMService()
    orchestrator = AnalysisOrchestrator(llm_service=mock_llm_service)

    logs = "Example log data"
    code_snippet = "def foo(): pass"
    platform = "test_platform"
    language = "python"

    analysis_id = orchestrator.start_analysis_background(logs, code_snippet, platform, language)

    # Wait for the async task to complete
    await asyncio.sleep(1)

    result = orchestrator.get_analysis_results(analysis_id)
    assert result is not None
    assert result.status == "COMPLETED"
    assert len(result.predicted_bugs) > 0
    assert any(bug.type.startswith("StaticAnalysis_") or bug.type == "MockBug" for bug in result.predicted_bugs)
    assert len(result.suggested_patches) > 0

    # Check that mock bug prediction is included
    mock_bug_found = any(bug.type == "MockBug" for bug in result.predicted_bugs)
    assert mock_bug_found

    # Check that mock patch suggestion is included
    mock_patch_found = any(patch.description == "This is a mock patch suggestion." for patch in result.suggested_patches)
    assert mock_patch_found
