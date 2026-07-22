import os
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from heuristics import check_url_structure, check_text_signals, compute_heuristic_score
from agent import get_verdict

load_dotenv()

app = FastAPI(title="TrustLens AI Backend")


class AnalyzeRequest(BaseModel):
    url: str | None = None
    text: str | None = None
    source: str = "page"


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    findings = []
    if req.url:
        findings += check_url_structure(req.url)
    if req.text:
        findings += check_text_signals(req.text)

    heuristic_result = compute_heuristic_score(findings)

    async with httpx.AsyncClient(trust_env=False) as client:
        verdict = await get_verdict(req.url, req.text, findings, heuristic_result["score"], client)

    return {"heuristics": {"findings": findings, **heuristic_result}, "ai_verdict": verdict}