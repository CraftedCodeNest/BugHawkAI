# backend/app/utils/log_parser.py
from typing import Dict, Any, Optional
import re

class LogParser:
    """
    A utility to parse various log formats and extract key information.
    This can be greatly expanded with regex, machine learning for anomaly detection, etc.
    """
    def __init__(self):
        # Define common error patterns
        self.error_patterns = {
            "java": r"(java|kotlin)\\.lang\\.(?P<error_type>\\w+)Exception:",
            "swift": r"(Fatal error|Thread \\d+: Fatal error): (?P<error_description>.*)",
            "generic": r"(ERROR|CRITICAL|FATAL|FAILURE|EXCEPTION|ASSERTION FAILED):.*"
        }

    def parse(self, logs: str) -> Dict[str, Any]:
        parsed_data = {
            "summary": "No critical events found.",
            "error_lines": [],
            "warnings": [],
            "error_count": 0,
            "first_error_type": None
        }

        lines = logs.splitlines()
        for line_num, line in enumerate(lines):
            line_lower = line.lower()
            if "error" in line_lower or "exception" in line_lower or "fatal" in line_lower:
                parsed_data["error_lines"].append({"line_num": line_num + 1, "content": line.strip()})
                parsed_data["error_count"] += 1
                if not parsed_data["first_error_type"]:
                    for lang, pattern in self.error_patterns.items():
                        match = re.search(pattern, line)
                        if match:
                            parsed_data["first_error_type"] = match.groupdict().get("error_type") or match.groupdict().get("error_description")
                            break
                    if not parsed_data["first_error_type"]:
                        parsed_data["first_error_type"] = "Generic Error"
            elif "warn" in line_lower:
                parsed_data["warnings"].append({"line_num": line_num + 1, "content": line.strip()})
        
        if parsed_data["error_count"] > 0:
            parsed_data["summary"] = f"Detected {parsed_data['error_count']} errors. First identified type: {parsed_data['first_error_type']}"
        elif parsed_data["warnings"]:
            parsed_data["summary"] = f"Detected {len(parsed_data['warnings'])} warnings."

        return parsed_data
