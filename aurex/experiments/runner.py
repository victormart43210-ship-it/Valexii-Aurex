"""Deterministic paired experiment execution."""

import logging
import re
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ConfigDict

from aurex.provenance import fingerprint

from .contracts import ExperimentManifest
from .ledger import EvidenceLedger

logger = logging.getLogger(__name__)

Solver = Callable[[str], str]


def sanitize_error_message(msg: str) -> str:
    # Scrub URLs, credentials, and obvious tokens from error messages
    msg = re.sub(r"https?://[^\s]+", "[REDACTED_URL]", msg)
    msg = re.sub(
        r"(bearer|key|token|secret)[\s:=]+\S+", "[REDACTED_CREDENTIAL]", msg, flags=re.IGNORECASE
    )
    return msg


class ExperimentExecutionError(RuntimeError):
    """Sanitized execution failure tied to one experiment item and arm."""

    def __init__(self, item_id: str, arm_id: str, error_type: str) -> None:
        super().__init__(f"experiment execution failed for item {item_id!r} arm {arm_id!r}")
        self.item_id = item_id
        self.arm_id = arm_id
        self.error_type = error_type


class ItemResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    item_id: str
    baseline_output: str
    experimental_output: str


class RunReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    experiment_id: str
    manifest_sha256: str
    items: tuple[ItemResult, ...]
    complete: bool
    run_sha256: str


class ExperimentRunner:
    def __init__(self, ledger: EvidenceLedger) -> None:
        self.ledger = ledger

    def _solve(
        self,
        *,
        item_id: str,
        arm_id: str,
        prompt: str,
        solver: Solver,
    ) -> str:
        try:
            out = solver(prompt)
            if not isinstance(out, str):
                raise TypeError(f"Solver returned {type(out).__name__} instead of str")
            return out
        except Exception as exc:  # noqa: BLE001
            error_type = type(exc).__name__
            self.ledger.append(
                "item_failed",
                {"item_id": item_id, "arm_id": arm_id, "error_type": error_type},
            )
            self.ledger.append(
                "experiment_failed",
                {
                    "item_id": item_id,
                    "arm_id": arm_id,
                    "error_type": error_type,
                    "complete": False,
                },
            )
            raise ExperimentExecutionError(item_id, arm_id, error_type) from exc

    def run(
        self,
        manifest: ExperimentManifest,
        prompts: dict[str, str],
        baseline_solver: Solver,
        experimental_solver: Solver,
        raise_on_solver_error: bool = False,
    ) -> RunReport:
        return self.run_fail_safe(
            manifest=manifest,
            prompts=prompts,
            baseline_solver=baseline_solver,
            experimental_solver=experimental_solver,
            raise_on_solver_error=raise_on_solver_error,
        )

    def run_fail_safe(
        self,
        manifest: ExperimentManifest,
        prompts: dict[str, str],
        baseline_solver: Solver,
        experimental_solver: Solver,
        raise_on_solver_error: bool = False,
    ) -> RunReport:
        manifest_sha256 = fingerprint(manifest.model_dump(mode="json"))
        results: list[ItemResult] = []
        self.ledger.append(
            "experiment_started",
            {"experiment_id": manifest.experiment_id, "manifest_sha256": manifest_sha256},
        )

        for item_id in manifest.item_ids:
            if item_id not in prompts:
                self.ledger.append("item_missing", {"item_id": item_id})
                continue
            prompt = prompts[item_id]

            if raise_on_solver_error:
                base_out = self._solve(
                    item_id=item_id,
                    arm_id=manifest.baseline.arm_id,
                    prompt=prompt,
                    solver=baseline_solver,
                )
                exp_out = self._solve(
                    item_id=item_id,
                    arm_id=manifest.experimental.arm_id,
                    prompt=prompt,
                    solver=experimental_solver,
                )
            else:
                try:
                    base_out = baseline_solver(prompt)
                    exp_out = experimental_solver(prompt)
                    if not isinstance(base_out, str) or not isinstance(exp_out, str):
                        raise TypeError("Solver output must be str")
                except Exception as exc:  # noqa: BLE001
                    clean_err = sanitize_error_message(str(exc))
                    self.ledger.append(
                        "solver_error",
                        {"item_id": item_id, "error": clean_err, "type": type(exc).__name__},
                    )
                    continue

            result = ItemResult(
                item_id=item_id,
                baseline_output=base_out,
                experimental_output=exp_out,
            )
            results.append(result)
            self.ledger.append("item_completed", result.model_dump(mode="json"))

        complete = len(results) == len(manifest.item_ids)
        run_body: dict[str, Any] = {
            "experiment_id": manifest.experiment_id,
            "manifest_sha256": manifest_sha256,
            "items": [item.model_dump(mode="json") for item in results],
            "complete": complete,
        }
        run_sha256 = fingerprint(run_body)
        self.ledger.append(
            "experiment_completed",
            {"run_sha256": run_sha256, "complete": complete},
        )
        return RunReport(
            experiment_id=manifest.experiment_id,
            manifest_sha256=manifest_sha256,
            items=tuple(results),
            complete=complete,
            run_sha256=run_sha256,
        )
