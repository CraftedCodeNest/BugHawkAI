# backend/app/services/llm_service.py
import logging
from typing import Optional, List, Dict
import json
from openai import OpenAI, APIConnectionError, RateLimitError, APIStatusError
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not found in environment or .env file. LLM operations will likely fail.")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o"  # Confirm this model name is correct; consider "gpt-4-turbo" or "gpt-3.5-turbo"

    async def predict_bug_from_logs(self, logs: str, code_snippet: Optional[str] = None) -> List[Dict]:
        if not logs:
            logger.error("Empty logs provided to predict_bug_from_logs; skipping API call.")
            return []

        user_content = f"Analyze the following logs and code for potential software bugs.\n\nLogs:\n```\n{logs}\n```\n"
        if code_snippet:
            user_content += f"\nCode Snippet:\n```\n{code_snippet}\n```\n"

        prompt = (
            "You are an AI assistant specialized in identifying software bugs from logs and code. "
            "Your task is to analyze the provided information and identify any potential bugs. "
            "For each bug, provide its type (e.g., 'LogicError', 'Performance', 'Security', 'Crash', 'MemoryLeak', 'Concurrency'), "
            "a concise description, its severity ('Low', 'Medium', 'High', 'Critical'), and a confidence score (0.0 to 1.0). "
            "Respond ONLY with a JSON array of bug objects. Do not include any other text, explanations, or markdown fences outside the JSON.\n\n"
            "Example JSON format:\n"
            "[\n"
            "  {\n"
            "    \"type\": \"LogicError\",\n"
            "    \"description\": \"User authentication failing due to incorrect password hashing algorithm.\",\n"
            "    \"severity\": \"High\",\n"
            "    \"confidence\": 0.95\n"
            "  },\n"
            "  {\n"
            "    \"type\": \"Performance\",\n"
            "    \"description\": \"Database query returning too many results, causing slow load times.\",\n"
            "    \"severity\": \"Medium\",\n"
            "    \"confidence\": 0.7\n"
            "  }\n"
            "]\n\n" + user_content
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                chat_completion = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a software bug analysis AI. Respond only in JSON format."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                response_content = chat_completion.choices[0].message.content
                parsed_json = json.loads(response_content)
                if isinstance(parsed_json, dict) and 'bugs' in parsed_json:
                    return parsed_json['bugs']
                elif isinstance(parsed_json, list):
                    return parsed_json
                else:
                    logger.error(f"LLM returned unexpected JSON structure: {response_content}")
                    return []
            except (APIConnectionError, RateLimitError, APIStatusError) as e:
                logger.warning(f"OpenAI API error on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt == max_retries - 1:
                    logger.error("Max retries reached for OpenAI API call.")
                    return []
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON from LLM response: {e}\nRaw response: {response_content}")
                return []
            except Exception as e:
                logger.error(f"An unexpected error occurred during bug prediction: {e}")
                return []

    async def suggest_patch_for_bug(self, bug_description: str, code_snippet: str, language: str) -> List[Dict]:
        if not bug_description or not code_snippet or not language:
            logger.error("Invalid inputs provided to suggest_patch_for_bug; skipping API call.")
            return []

        prompt = (
            f"You are an AI assistant specialized in fixing software bugs. "
            f"Given the following bug description and a relevant code snippet in {language}, "
            f"provide a concise and idiomatic code patch. Respond ONLY with a JSON array containing "
            f"one or more patch objects. Each patch object should have a 'description' of the fix and a 'code_diff' "
            f"formatted as a Git-style diff within a Markdown code block (```diff\\n...\\n```). "
            f"Do not include any other text, explanations, or markdown fences outside the JSON.\n\n"
            f"Bug Description: {bug_description}\n\n"
            f"Code Snippet ({language}):\n```\n{code_snippet}\n```\n\n"
            "Example JSON format for patch:\n"
            "[\n"
            "  {\n"
            "    \"description\": \"Implemented null check to prevent dereferencing a nil optional.\",\n"
            "    \"code_diff\": \"```diff\\n- old_code_line\\n+ new_code_line\\n```\"\n"
            "  }\n"
            "]"
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                chat_completion = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": f"You are a code patching AI for {language}. Respond only in JSON format."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                response_content = chat_completion.choices[0].message.content
                parsed_json = json.loads(response_content)
                if isinstance(parsed_json, dict) and 'patches' in parsed_json:
                    return parsed_json['patches']
                elif isinstance(parsed_json, list):
                    return parsed_json
                else:
                    logger.error(f"LLM returned unexpected JSON structure for patches: {response_content}")
                    return []
            except (APIConnectionError, RateLimitError, APIStatusError) as e:
                logger.warning(f"OpenAI API error on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt == max_retries - 1:
                    logger.error("Max retries reached for OpenAI API call.")
                    return []
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON from LLM response: {e}\nRaw response: {response_content}")
                return []
            except Exception as e:
                logger.error(f"An unexpected error occurred during patch suggestion: {e}")
                return []
