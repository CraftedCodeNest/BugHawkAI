import pytest
import asyncio
from app.services.static_analysis_service import StaticAnalysisService

@pytest.mark.asyncio
async def test_run_analysis_with_pylint():
    service = StaticAnalysisService()
    code_snippet = """
def foo():
    pass
"""
    results = await service.run_analysis(code_snippet, "python")
    assert isinstance(results, list)
    # Each finding should have required keys
    for finding in results:
        assert "type" in finding
        assert "message" in finding
        assert "file" in finding
        assert "line" in finding
        assert "severity" in finding

@pytest.mark.asyncio
async def test_run_analysis_with_unknown_language():
    service = StaticAnalysisService()
    code_snippet = "some code"
    results = await service.run_analysis(code_snippet, "unknownlang")
    assert results == []
