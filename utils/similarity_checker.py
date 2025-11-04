# similarity_checker.py
import json
import time
from google import genai
from dotenv import load_dotenv
import os
import re

load_dotenv()

# Create a singleton-like client creation function (avoid recreating client every call)
def get_genai_client():
    # The genai.Client() will automatically read GEMINI_API_KEY from env
    return genai.Client()

def safe_parse_json(text):
    """
    Try to find a JSON object inside text and parse it.
    This is lenient in case the model responds with extra words.
    """
    # find first "{" and last "}" and try parse
    try:
        start = text.index('{')
        end = text.rindex('}') + 1
        candidate = text[start:end]
        return json.loads(candidate)
    except Exception:
        # sometimes the model returns single-line JSON-like structure or plain key: value lines
        # attempt a crude parse for common numeric fields
        return None

def analyze_candidate(jd_text: str, resume_text: str, model="gemini-2.5-flash"):
    """
    Single API call that returns a dict with:
    {
      "fit_score": float,
      "skill_fit": float,
      "experience_fit": float,
      "education_fit": float,
      "summary": str,
      "keywords_matched": [str,...],
      "keywords_missing": [str,...]
    }
    If the LLM response cannot be parsed, the function returns None.
    """
    client = get_genai_client()

    prompt = f"""
You are an AI hiring assistant. Compare the following Job Description and Resume.

Return a single valid JSON object ONLY (no extra commentary) with the following fields:
- fit_score: number (0-100) — overall suitability percentage
- skill_fit: number (0-100) — how well skills match
- experience_fit: number (0-100) — how well experience (years, responsibilities) matches
- education_fit: number (0-100) — education / certifications match
- summary: short string (1-3 sentences) describing why the candidate is fit or not fit (concrete points, no generic fluff)
- keywords_matched: list of up to 5 strings (top matched keywords from JD)
- keywords_missing: list of up to 5 strings (important JD keywords missing from resume)

Job Description:
{jd_text}

Resume:
{resume_text}
"""

    try:
        response = client.models.generate_content(model=model, contents=prompt)
        text = response.text.strip()

        parsed = safe_parse_json(text)
        if parsed:
            # Ensure numeric values exist and are normalized
            def n(key):
                val = parsed.get(key, 0)
                try:
                    return float(val)
                except Exception:
                    return 0.0

            result = {
                "fit_score": max(0.0, min(100.0, n("fit_score"))),
                "skill_fit": max(0.0, min(100.0, n("skill_fit"))),
                "experience_fit": max(0.0, min(100.0, n("experience_fit"))),
                "education_fit": max(0.0, min(100.0, n("education_fit"))),
                "summary": parsed.get("summary", "").strip(),
                "keywords_matched": parsed.get("keywords_matched", []) if isinstance(parsed.get("keywords_matched", []), list) else [],
                "keywords_missing": parsed.get("keywords_missing", []) if isinstance(parsed.get("keywords_missing", []), list) else []
            }
            return result
        else:
            # Try to extract numbers heuristically if JSON not found
            # Extract first number from text as a fallback overall score
            m = re.search(r"(\d{1,3}(?:\.\d+)?)", text)
            score = float(m.group(1)) if m else 0.0
            return {
                "fit_score": max(0.0, min(100.0, score)),
                "skill_fit": 0.0,
                "experience_fit": 0.0,
                "education_fit": 0.0,
                "summary": text[:500],
                "keywords_matched": [],
                "keywords_missing": []
            }
    except Exception as e:
        # In case of API error, return None so caller can fallback
        print(f"Gemini analyze_candidate error: {e}")
        return None

def calculate_similarity_score(jd_text: str, resume_text: str, model="gemini-2.5-flash"):
    """
    Simple numeric-only fallback: asks the model to return a single numeric score (0-100).
    Returns float score.
    """
    client = get_genai_client()
    prompt = f"""
You are a hiring assistant. Compare the job description and resume and return ONLY a numeric suitability score from 0 to 100 (no explanation).

Job Description:
{jd_text}

Resume:
{resume_text}
"""
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        text = response.text.strip()
        # find first number
        import re
        m = re.search(r"(\d{1,3}(?:\.\d+)?)", text)
        if m:
            score = float(m.group(1))
            score = max(0.0, min(100.0, score))
            return round(score, 2)
        else:
            return 0.0
    except Exception as e:
        print(f"Gemini calculate_similarity_score error: {e}")
        return 0.0
