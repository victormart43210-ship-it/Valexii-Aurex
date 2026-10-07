"""Minimal HTTP API. Run with: uvicorn aurex.api:app"""

from fastapi import FastAPI

from aurex.challengers.rules import EvidencePresenceChallenger
from aurex.engine import AurexEngine
from aurex.protocol import ChallengeRequest, ChallengeResult

app = FastAPI(
    title="VALEXII-AUREX",
    version="0.1.0-pre",
    description="External evidence and challenge engine. AUREX never grants product authority.",
)
engine = AurexEngine([EvidencePresenceChallenger()])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "authority": "none"}


@app.post("/v1/challenge", response_model=list[ChallengeResult])
def challenge(request: ChallengeRequest) -> list[ChallengeResult]:
    return engine.evaluate(request)
