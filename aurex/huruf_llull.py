"""AUREX XCVI — offline Hurufi, Llull, manuscript and Python static research.

This is a historical/methodological comparison, NOT proven decipherment,
and source code is never imported, evaluated, or executed.
"""
from __future__ import annotations

import ast
import hashlib
import json
import random
import re
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any

MAX_TEXT_BYTES = 64 * 1024
MAX_AST_NODES = 6000
MAX_TOKENS = 10000
POLICY = "aurex-xcvi-symbolic-structural-v1"
LLULL_LETTERS = "BCDEFGHIK"
ABJAD_LETTERS = "ابجدهوزحطيكلمنسعفصقرشتثخذضظغ"
ABJAD_VALUES = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000)
ABJAD_MAP = dict(zip(ABJAD_LETTERS, ABJAD_VALUES, strict=True))
ABJAD_SEPARATOR = set(" \t\r\n،؛؟,.;:!?()-[]{}«»\"'ـ")
ALEF_VARIANTS = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا"})
SOURCES = {
    "hurufi_history": "https://www.iranicaonline.org/articles/horufism/",
    "llull_ars": "https://plato.stanford.edu/entries/llull/",
    "abjad_history": "https://www.iranicaonline.org/articles/abjad/",
}
LLULL_DOMAINS: dict[str, dict[str, str]] = {
    "dignity": dict(zip(LLULL_LETTERS, (
        "goodness", "greatness", "duration", "power", "wisdom", "will",
        "virtue", "truth", "glory"), strict=True)),
    "relation": dict(zip(LLULL_LETTERS, (
        "difference", "concordance", "contrariety", "beginning", "middle",
        "end", "majority", "equality", "minority"), strict=True)),
    "question": dict(zip(LLULL_LETTERS, (
        "whether", "what", "of what", "why", "how much", "what quality",
        "when", "where", "how and with what"), strict=True)),
}
WORD_PATTERN = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)?", re.UNICODE)


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _bounded(value: str) -> None:
    if not isinstance(value, str) or len(value.encode("utf-8")) > MAX_TEXT_BYTES:
        raise ValueError("invalid or oversized text (64 KiB max)")
    if "\x00" in value:
        raise ValueError("binary/NUL input")


def _receipt(kind: str, text: str, status: str, analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": kind, "policy": POLICY, "source_sha256": _sha(text),
        "status": status, "analysis": analysis,
        "independent_verification": "NOT_VERIFIED",
        "decipherment": "NOT_ESTABLISHED",
        "authority": "NONE", "external_spend_usd": 0,
    }


def abjad_calculate(text: str, *, normalize_alef: bool = False) -> dict[str, Any]:
    """Classical eastern 28-letter abjad; unmapped extensions block total."""
    _bounded(text)
    normalized = text.translate(ALEF_VARIANTS) if normalize_alef else text
    unknown: Counter[str] = Counter()
    total = mapped = 0
    for char in normalized:
        if char in ABJAD_MAP:
            mapped += 1
            total += ABJAD_MAP[char]
        elif char not in ABJAD_SEPARATOR:
            unknown[char] += 1
    status = ("HOLD_NO_MAPPED_LETTERS" if not mapped
              else "HOLD_UNMAPPED_CHARACTERS" if unknown
              else "CALCULATION_ONLY")
    return _receipt("abjad", text, status, {
        "total": total if status == "CALCULATION_ONLY" else None,
        "mapped_letters": mapped, "unmapped_characters": sum(unknown.values()),
        "unmapped_unique": len(unknown),
        "normalization": "ALEF_VARIANTS_OPT_IN" if normalize_alef else "NONE",
        "alphabet": "CLASSICAL_ARABIC_28_EASTERN_ABJAD",
        "interpretation": "NUMERICAL_CONVENTION_NOT_DECIPHERMENT",
        "source": SOURCES["abjad_history"],
    })


def llull_wheel(
    *, offsets: tuple[int, int, int] = (0, 1, 2),
    domains: tuple[str, str, str] = ("dignity", "relation", "question"),
) -> dict[str, Any]:
    """Nine-position three-ring analogue; not an original historical wheel."""
    if len(offsets) != 3 or any(type(n) is not int or n not in range(9) for n in offsets):
        raise ValueError("each offset must be 0..8")
    if len(domains) != 3 or any(domain not in LLULL_DOMAINS for domain in domains):
        raise ValueError("invalid Llull domain")
    rows: list[dict[str, Any]] = []
    for position in range(9):
        letters = [LLULL_LETTERS[(position + offset) % 9] for offset in offsets]
        terms = [LLULL_DOMAINS[domain][letter]
                 for letter, domain in zip(letters, domains, strict=True)]
        rows.append({"letters": "".join(letters), "terms": terms})
    return {
        "policy": POLICY, "status": "COMBINATIONS_ONLY",
        "figure": "MODERN_9_POSITION_THREE_RING_ANALOGUE",
        "offsets": list(offsets), "domains": list(domains), "combinations": rows,
        "source": SOURCES["llull_ars"],
        "independent_verification": "NOT_VERIFIED",
        "decipherment": "NOT_ESTABLISHED",
        "authority": "NONE", "external_spend_usd": 0,
    }


def _concentration(tokens: list[str], width: int) -> float:
    tails = [token[-width:] for token in tokens if len(token) >= width]
    return max(Counter(tails).values()) / len(tails) if tails else 0.0


def profile_document(text: str, *, suffix_width: int = 2) -> dict[str, Any]:
    """Suffix-first diagnostics: never reverse the source's actual reading order."""
    _bounded(text)
    if type(suffix_width) is not int or suffix_width not in (1, 2, 3):
        raise ValueError("suffix width must be 1, 2 or 3")
    words = WORD_PATTERN.findall(text.casefold())
    if len(words) > MAX_TOKENS:
        raise ValueError("token count exceeds limit")
    shuffled: list[str] = []
    rng = random.Random(20261018)
    for token in words:
        letters = list(token)
        rng.shuffle(letters)
        shuffled.append("".join(letters))
    tails = Counter(token[-suffix_width:] for token in words if len(token) >= suffix_width)
    top = [{"suffix": word, "count": count} for word, count in
           sorted(tails.items(), key=lambda item: (-item[1], item[0]))[:8]]
    return _receipt("document", text, "STRUCTURAL_PROFILE_ONLY", {
        "token_count": len(words), "unique_tokens": len(set(words)),
        "character_count": len(text), "suffix_width": suffix_width,
        "common_suffixes": top,
        "observed_top_suffix_fraction": round(_concentration(words, suffix_width), 6),
        "single_shuffled_null_fraction": round(_concentration(shuffled, suffix_width), 6),
        "test_limitations": "single deterministic null; no significance or semantic claim",
        "reading_order": "UNCHANGED_SUFFIX_ANALYZED_FROM_RIGHT_EDGE",
        "scholarly_mapping": "UNDETERMINED",
    })


def caesar_transform(text: str, shift: int, *, decode: bool = True) -> str:
    """Classical ASCII rotation for a *known* key; no automatic interpretation."""
    _bounded(text)
    if type(shift) is not int or shift not in range(26):
        raise ValueError("shift must be 0..25")
    delta = -shift if decode else shift
    result = []
    for char in text:
        if "A" <= char <= "Z":
            result.append(chr((ord(char) - 65 + delta) % 26 + 65))
        elif "a" <= char <= "z":
            result.append(chr((ord(char) - 97 + delta) % 26 + 97))
        else:
            result.append(char)
    return "".join(result)


def caesar_candidates(text: str) -> dict[str, Any]:
    _bounded(text)
    return _receipt("cipher", text, "CANDIDATES_ONLY_NO_KEY", {
        "method": "ASCII_CAESAR_ROTATION",
        "candidates": [{"shift": shift,
                        "result_sha256": _sha(caesar_transform(text, shift))}
                       for shift in range(26)],
        "candidate_selection": "NONE_NO_CLAIM_OF_PLAINTEXT",
    })


@dataclass(frozen=True)
class PythonStaticFindings:
    lines: int
    functions: tuple[str, ...]
    classes: tuple[str, ...]
    imports: tuple[str, ...]
    ast_node_counts: dict[str, int]
    potentially_sensitive_call_patterns: tuple[str, ...]
    interpretation: str = "STATIC_STRUCTURE_ONLY_NOT_VULNERABILITY_VERDICT"


def inspect_python(source: str) -> dict[str, Any]:
    """Parse AST only; NEVER evaluate, import, execute or run the given source."""
    _bounded(source)
    try:
        tree = ast.parse(source)
        nodes = list(ast.walk(tree))
        if len(nodes) > MAX_AST_NODES:
            raise ValueError("too many AST nodes")
    except (SyntaxError, RecursionError, MemoryError, ValueError):
        return _receipt("python_code", source, "HOLD_PARSE_FAILED",
                        {"interpretation": "SOURCE_NOT_EXECUTED"})
    counts = Counter(type(node).__name__ for node in nodes)
    functions = sorted({node.name for node in nodes
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))})
    classes = sorted({node.name for node in nodes if isinstance(node, ast.ClassDef)})
    imports: set[str] = set()
    hints: set[str] = set()
    for node in nodes:
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call):
            name = (node.func.id if isinstance(node.func, ast.Name)
                    else node.func.attr if isinstance(node.func, ast.Attribute) else None)
            if name in {"eval", "exec", "compile", "system", "popen", "Popen", "loads"}:
                hints.add(name)
    findings = PythonStaticFindings(
        lines=len(source.splitlines()), functions=tuple(functions[:100]),
        classes=tuple(classes[:100]), imports=tuple(sorted(imports)[:100]),
        ast_node_counts=dict(sorted(counts.items())),
        potentially_sensitive_call_patterns=tuple(sorted(hints)),
    )
    return _receipt("python_code", source, "STATIC_AST_ONLY", asdict(findings))


def combined_research(
    text: str, *, kind: str = "document",
    offsets: tuple[int, int, int] = (0, 1, 2),
) -> dict[str, Any]:
    """Compare distinct historical systems; never imply a shared proven cipher."""
    _bounded(text)
    if kind not in {"document", "python"}:
        raise ValueError("kind must be document or python")
    structure = profile_document(text)
    abjad = abjad_calculate(text) if any("\u0600" <= char <= "\u06ff" for char in text) else None
    python = inspect_python(text) if kind == "python" else None
    wheel = llull_wheel(offsets=offsets)
    return _receipt("crosswalk", text, "MULTI_METHOD_HYPOTHESIS_ONLY", {
        "document_structure": structure["analysis"],
        "abjad": abjad["analysis"] if abjad is not None else "NOT_APPLICABLE_NO_ARABIC_SCRIPT",
        "abjad_status": abjad["status"] if abjad is not None else "NOT_RUN",
        "python_structure": python["analysis"] if python is not None else "NOT_APPLICABLE",
        "python_status": python["status"] if python is not None else "NOT_RUN",
        "llull_wheel": {
            "figure": wheel["figure"], "offsets": wheel["offsets"],
            "domains": wheel["domains"], "combinations": wheel["combinations"],
        },
        "method_relationship": "MODERN_COMPARISON_ONLY_NOT_A_HISTORICAL_LINK",
        "inference": "NONE",
        "required_next_evidence": "scholarly sources, independent controls, held-out prediction",
    })
