import requests


def test_groq_api_key(api_key: str) -> tuple[bool, str]:
    if not api_key.strip():
        return False, "Groq API key is empty."

    try:
        response = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={
                "Authorization": f"Bearer {api_key}",
            },
            timeout=15,
        )

        if response.status_code == 200:
            payload = response.json()
            if isinstance(payload, dict) and "data" in payload:
                return True, "Groq key is valid and the API is reachable."
            return False, "Groq responded, but the response format was unexpected."

        if response.status_code == 401:
            return False, "Groq key is invalid or unauthorized."
        if response.status_code == 403:
            return False, "Groq key was recognized but access is forbidden."
        return False, f"Groq test failed with status code {response.status_code}."

    except requests.RequestException as error:
        return False, f"Groq test failed due to a network error: {error}"


def test_gemini_api_key(api_key: str) -> tuple[bool, str]:
    if not api_key.strip():
        return False, "Gemini API key is empty."

    try:
        response = requests.get(
            "https://generativelanguage.googleapis.com/v1/models",
            headers={
                "x-goog-api-key": api_key,
            },
            timeout=15,
        )

        if response.status_code == 200:
            payload = response.json()
            if isinstance(payload, dict) and "models" in payload:
                return True, "Gemini key is valid and the API is reachable."
            return False, "Gemini responded, but the response format was unexpected."

        if response.status_code == 400:
            return False, "Gemini request was rejected. The key may be malformed or the endpoint may require different access."
        if response.status_code == 401:
            return False, "Gemini key is invalid or unauthorized."
        if response.status_code == 403:
            return False, "Gemini key was recognized but access is forbidden or restricted."
        return False, f"Gemini test failed with status code {response.status_code}."

    except requests.RequestException as error:
        return False, f"Gemini test failed due to a network error: {error}"
