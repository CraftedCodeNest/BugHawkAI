import subprocess
import json
import tempfile
from typing import Dict, Any, List, Optional
import os
import logging

logger = logging.getLogger(__name__)

class StaticAnalysisService:
    """
    Orchestrates external static analysis tools based on language.
    This service runs tools like Clang-Tidy, SwiftLint, Detekt, ESLint, Pylint.
    """

    def __init__(self):
        pass

    async def run_analysis(self, code_snippet: str, language: str) -> List[Dict[str, Any]]:
        """
        Runs static analysis on the provided code snippet.
        Currently returns mock data or calls real tool integration methods.
        """
        findings = []
        try:
            if language.lower() in ["python"]:
                findings = await self._run_pylint(code_snippet)
            elif language.lower() in ["swift", "ios"]:
                findings = await self._run_swiftlint(code_snippet)
            elif language.lower() in ["kotlin", "android", "java"]:
                findings = await self._run_detekt(code_snippet)
            else:
                logger.warning(f"No specific static analysis tool configured for language: {language}")
        except Exception as e:
            logger.error(f"Error during static analysis: {e}", exc_info=True)
        return findings

    async def _run_pylint(self, code_snippet: str) -> List[Dict[str, Any]]:
        """
        Runs Pylint on Python code snippet by:
        1. Saving code to a temporary file.
        2. Running pylint CLI with JSON output.
        3. Parsing JSON output into internal findings format.
        """
        logger.info("Running Pylint analysis")
        findings = []
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=True) as temp_file:
            temp_file.write(code_snippet)
            temp_file.flush()
            try:
                # Run pylint with JSON output format
                result = subprocess.run(
                    ["pylint", temp_file.name, "-f", "json", "--disable=all", "--enable=all"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                pylint_output = result.stdout
                parsed = json.loads(pylint_output)
                for issue in parsed:
                    findings.append({
                        "type": issue.get("type"),
                        "message": issue.get("message"),
                        "file": issue.get("path"),
                        "line": issue.get("line"),
                        "severity": self._map_pylint_type_to_severity(issue.get("type"))
                    })
            except subprocess.CalledProcessError as e:
                logger.error(f"Pylint failed: {e.stderr}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse pylint output: {e}")
        return findings

    def _map_pylint_type_to_severity(self, pylint_type: Optional[str]) -> str:
        """
        Maps pylint message types to severity levels.
        """
        mapping = {
            "convention": "Convention",
            "refactor": "Refactor",
            "warning": "Warning",
            "error": "Error",
            "fatal": "Fatal"
        }
        if pylint_type:
            return mapping.get(pylint_type.lower(), "Info")
        return "Info"

    async def _run_swiftlint(self, code_snippet: str) -> List[Dict[str, Any]]:
        """
        Runs SwiftLint on Swift code snippet by:
        1. Saving code to a temporary .swift file.
        2. Running SwiftLint CLI with JSON output.
        3. Parsing JSON output into internal findings format.
        """
        logger.info("Running SwiftLint analysis")
        findings = []
        with tempfile.NamedTemporaryFile(suffix=".swift", mode="w", delete=False) as temp_file:
            temp_file.write(code_snippet)
            temp_file.flush()
            temp_file_path = temp_file.name
        try:
            # Run swiftlint with JSON output format
            result = subprocess.run(
                ["swiftlint", "lint", "--path", temp_file_path, "--reporter", "json"],
                capture_output=True,
                text=True,
                check=True
            )
            swiftlint_output = result.stdout
            parsed = json.loads(swiftlint_output)
            for issue in parsed:
                findings.append({
                    "rule": issue.get("rule_id"),
                    "reason": issue.get("reason"),
                    "file": issue.get("file"),
                    "line": issue.get("line"),
                    "severity": issue.get("severity").capitalize() if issue.get("severity") else "Info"
                })
        except subprocess.CalledProcessError as e:
            logger.error(f"SwiftLint failed: {e.stderr}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse swiftlint output: {e}")
        finally:
            try:
                os.remove(temp_file_path)
            except Exception:
                pass
        return findings

    async def _run_detekt(self, code_snippet: str) -> List[Dict[str, Any]]:
        """
        Runs Detekt on Kotlin code snippet by:
        1. Saving code to a temporary .kt file.
        2. Running Detekt CLI with JSON output.
        3. Parsing JSON output into internal findings format.
        """
        logger.info("Running Detekt analysis")
        findings = []
        with tempfile.NamedTemporaryFile(suffix=".kt", mode="w", delete=False) as temp_file:
            temp_file.write(code_snippet)
            temp_file.flush()
            temp_file_path = temp_file.name
        report_path = temp_file_path + "-detekt-report.json"
        try:
            # Run detekt with JSON output format
            result = subprocess.run(
                ["detekt", "--input", temp_file_path, "--report", f"json:{report_path}"],
                capture_output=True,
                text=True,
                check=True
            )
            # Read the generated report file
            with open(report_path, "r") as report_file:
                detekt_output = json.load(report_file)
            # Parse detekt output (assuming issues under 'issues' key)
            issues = detekt_output.get("issues", [])
            for issue in issues:
                findings.append({
                    "check": issue.get("rule"),
                    "message": issue.get("message"),
                    "file": issue.get("file"),
                    "line": issue.get("location", {}).get("line"),
                    "severity": issue.get("severity").capitalize() if issue.get("severity") else "Info"
                })
        except subprocess.CalledProcessError as e:
            logger.error(f"Detekt failed: {e.stderr}")
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Failed to parse detekt output: {e}")
        finally:
            try:
                os.remove(temp_file_path)
            except Exception:
                pass
            try:
                os.remove(report_path)
            except Exception:
                pass
        return findings
