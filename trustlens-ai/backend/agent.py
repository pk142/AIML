import json
import os

import httpx

#GEMINI_MODEL = "gemini-2.0-flash"
#GEMINI_MODEL = "gemini-2.5-flash-lite"
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

SYSTEM_INSTRUCTIONS = """You are TrustLens AI, a cautious scam/phishing risk assessor.

You are given:
1. Deterministic heuristic findings (already computed, not your job to redo them).
2. The raw URL and/or text content a user wants assessed.

Rules:
- Never claim certainty a site or message IS fraudulent. Use language like
  "risk indicators detected" or "consistent with known scam patterns."
- Weigh the heuristic findings as strong evidence, but you may also notice
  patterns the heuristics miss (plausible brand impersonation, unusual
  grammar, mismatched sender/domain claims).
- If evidence is thin or ambiguous, say so and score conservatively.
- Respond with ONLY valid JSON, no markdown fences, matching exactly:
{
  "risk_score": <integer 0-100>,
  "risk_level": "LOW" | "MEDIUM" | "HIGH",
  "summary": "<one sentence, plain language>",
  "reasons": ["<short phrase>", "..."],
  "recommendation": "<one actionable sentence for the user>"
}
"""


def _build_prompt(url, text, findings, heuristic_score):
    parts = [f"URL: {url or '(none provided)'}"]
    if text:
        parts.append(f"Content: {text[:2000]}")
    parts.append(f"Heuristic findings: {json.dumps(findings)}")
    parts.append(f"Deterministic heuristic score (0-70 cap): {heuristic_score}")
    return "\n\n".join(parts)


async def get_verdict(url, text, findings, heuristic_score, client: httpx.AsyncClient):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return _fallback_verdict(findings, heuristic_score, reason="GEMINI_API_KEY not set")

    prompt = _build_prompt(url, text, findings, heuristic_score)
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTIONS}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
    }

    try:
        resp = await client.post(
            GEMINI_URL,
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            json=payload,
            timeout=15.0,
        )
        resp.raise_for_status()
        data = resp.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(raw_text)
    except Exception as e:
        return _fallback_verdict(findings, heuristic_score, reason=str(e))

def _fallback_verdict(findings, heuristic_score, reason):
    level = "HIGH" if heuristic_score >= 45 else "MEDIUM" if heuristic_score >= 20 else "LOW"
    return {
        "risk_score": heuristic_score,
        "risk_level": level,
        "summary": f"Assessment based on automated checks only (AI step unavailable: {reason}).",
        "reasons": [f["detail"] for f in findings] or ["No strong signals detected"],
        "recommendation": "Treat this as a preliminary read; re-check once the AI service is available.",
    }