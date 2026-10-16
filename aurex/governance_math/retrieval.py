"""Explainable $0 TF-IDF and nearest-neighbor baseline for incident discovery.

Pure analysis: finding a similar case NEVER proves it applies, that its previous
remedy succeeded, or that its source was independently verified. The caller must
perform trusted admission, tenant scoping, and redaction before supplying cases.
No copied curriculum content, remote calls, or learned model weights.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Sequence

_WORD = re.compile(r"[^\W_]{2,}", re.UNICODE)
MAX_CASES = 1000
MAX_TEXT = 4096
MAX_QUERY = 512


@dataclass(frozen=True, slots=True)
class Incident:
    case_id: str
    description: str
    remedy_id: str
    evidence_sha256: str
    lineage_group: str


@dataclass(frozen=True, slots=True)
class Match:
    case_id: str
    remedy_id: str
    evidence_sha256: str
    lineage_group: str
    similarity: float
    status: str = "CANDIDATE_ONLY_NOT_VERIFIED"


def _tokens(value: str) -> Counter[str]:
    return Counter(m.group().casefold() for m in _WORD.finditer(value))


def _vector(counts: Counter[str], idf: dict[str, float]) -> dict[str, float]:
    raw = {
        token: (1 + math.log(freq)) * idf[token]
        for token, freq in counts.items()
        if token in idf and freq > 0
    }
    norm = math.sqrt(sum(weight * weight for weight in raw.values()))
    return {token: weight / norm for token, weight in raw.items()} if norm else {}


def retrieve_incidents(
    query: str, cases: Sequence[Incident], *, limit: int = 5, distinct_lineages: bool = True
) -> tuple[Match, ...]:
    """Cosine TF-IDF neighbors, deterministic ties, bounded input and output.

    IDF is fit ONLY to the supplied corpus. This does not use incident outcomes
    as a training label and does not assert remediation success.
    """
    if not isinstance(query, str) or not 0 < len(query) <= MAX_QUERY:
        raise ValueError("query must have 1-512 characters")
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 20:
        raise ValueError("limit must be an integer from 1 to 20")
    if len(cases) > MAX_CASES:
        raise ValueError("too many incident records")
    if not isinstance(distinct_lineages, bool):
        raise ValueError("distinct_lineages must be bool")
    seen: set[str] = set()
    docs: list[Counter[str]] = []
    for case in cases:
        if not isinstance(case, Incident):
            raise ValueError("cases must contain Incident records")
        if (
            not case.case_id or case.case_id in seen or not case.remedy_id
            or not case.lineage_group or not case.description
            or len(case.description) > MAX_TEXT
            or not re.fullmatch(r"[0-9a-f]{64}", case.evidence_sha256)
        ):
            raise ValueError("invalid, duplicate or oversized incident record")
        seen.add(case.case_id)
        docs.append(_tokens(case.description))
    terms = _tokens(query)
    if not terms or not docs:
        return ()
    df = Counter(token for doc in docs for token in doc)
    idf = {term: math.log((len(docs) + 1) / (n + 1)) + 1 for term, n in df.items()}
    target = _vector(terms, idf)
    if not target:
        return ()
    matches: list[Match] = []
    for case, counts in zip(cases, docs, strict=True):
        doc = _vector(counts, idf)
        score = math.fsum(value * doc.get(term, 0.0) for term, value in target.items())
        if score > 0:
            matches.append(
                Match(
                    case.case_id,
                    case.remedy_id,
                    case.evidence_sha256,
                    case.lineage_group,
                    round(min(1.0, max(0.0, score)), 8),
                )
            )
    matches.sort(key=lambda m: (-m.similarity, m.case_id))
    if distinct_lineages:
        used: set[str] = set()
        unique: list[Match] = []
        for match in matches:
            if match.lineage_group not in used:
                unique.append(match)
                used.add(match.lineage_group)
            if len(unique) >= limit:
                break
        return tuple(unique)
    return tuple(matches[:limit])
