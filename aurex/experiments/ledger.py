"""Append-only, tamper-evident experiment evidence ledger."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from aurex.provenance import fingerprint


class LedgerEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    sequence: int = Field(ge=0)
    event_type: str = Field(min_length=1)
    payload: dict[str, Any]
    parent_hash: str | None
    event_hash: str
    recorded_at: datetime


class EvidenceLedger:
    def __init__(self) -> None:
        self._events: list[LedgerEvent] = []

    @property
    def events(self) -> tuple[LedgerEvent, ...]:
        return tuple(self._events)

    def append(self, event_type: str, payload: dict[str, Any]) -> LedgerEvent:
        sequence = len(self._events)
        parent_hash = self._events[-1].event_hash if self._events else None
        recorded_at = datetime.now(timezone.utc)
        body = {
            "sequence": sequence,
            "event_type": event_type,
            "payload": payload,
            "parent_hash": parent_hash,
            "recorded_at": recorded_at.isoformat(),
        }
        event = LedgerEvent(
            sequence=sequence,
            event_type=event_type,
            payload=payload,
            parent_hash=parent_hash,
            recorded_at=recorded_at,
            event_hash=fingerprint(body),
        )
        self._events.append(event)
        return event

    def verify(self) -> bool:
        parent_hash: str | None = None
        for sequence, event in enumerate(self._events):
            body = {
                "sequence": event.sequence,
                "event_type": event.event_type,
                "payload": event.payload,
                "parent_hash": event.parent_hash,
                "recorded_at": event.recorded_at.isoformat(),
            }
            if event.sequence != sequence:
                return False
            if event.parent_hash != parent_hash:
                return False
            if event.event_hash != fingerprint(body):
                return False
            parent_hash = event.event_hash
        return True
