import json
import requests
from typing import Optional

# If using Vertex AI SDK (recommended for production)
try:
    from google.cloud import aiplatform
    from vertexai.generative_models import GenerativeModel
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False


class LLMService:

    def __init__(self,
                 api_key: Optional[str] = None,
                 project: Optional[str] = None,
                 location: Optional[str] = None,
                 model: Optional[str] = None):

        self.api_key = api_key
        self.project = project
        self.location = location
        self.model = model

    # ============================================================
    # 1. DIRECT GEMINI API CALL (Equivalent to generateContentApi)
    # ============================================================
    def generate_content_api(self, prompt: str) -> str:
        if not self.api_key:
            raise Exception("Gemini API key not set")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=120
        )

        if response.status_code != 200:
            raise Exception(f"Gemini API failed: {response.status_code} {response.text}")

        return self._extract_text_from_response(response.json())

    def _extract_text_from_response(self, response_json: dict) -> str:
        try:
            candidates = response_json.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "")

            if "promptFeedback" in response_json:
                raise Exception(f"Blocked by safety filters: {response_json['promptFeedback']}")

            raise Exception("Invalid Gemini response format")

        except Exception as e:
            raise Exception(f"Error parsing Gemini response: {str(e)}")

    # ============================================================
    # 2. VERTEX AI SDK (Equivalent to generateContent)
    # ============================================================
    def generate_content(self, prompt: str) -> str:
        if not self.project:
            raise Exception("Gemini project not set")
        if not self.location:
            raise Exception("Gemini location not set")
        if not self.model:
            raise Exception("Gemini model not set")

        if not VERTEX_AVAILABLE:
            raise Exception("Vertex AI SDK not installed. Install: pip install google-cloud-aiplatform")

        try:
            # Initialize Vertex AI
            aiplatform.init(project=self.project, location=self.location)

            model = GenerativeModel(self.model)

            response = model.generate_content(prompt)

            text = response.text

            if not text:
                raise Exception(f"Empty response: {response}")

            return text

        except Exception as e:
            raise Exception(f"Vertex AI generation failed: {str(e)}")