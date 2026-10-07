"""Deterministic paired experiment execution."""

import logging
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ConfigDict

from aurex.provenance import fingerprint

from .contracts import ExperimentManifest
from .ledger import EvidenceLedger

logger = logging.getLogger(__name__)

Solver = Callable[[str], str]


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

    def run(
        self,
        manifest: ExperimentManifest,
        prompts: dict[str, str],
        baseline_solver: Solver,
        experimental_solver: Solver,
    ) -> RunReport:
        return self.run_fail_safe(
            manifest=manifest,
            prompts=prompts,
            baseline_solver=baseline_solver,
            experimental_solver=experimental_solver,
            raise_on_solver_error=True,
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

            try:
                base_out = baseline_solver(prompt)
                exp_out = experimental_solver(prompt)
            except Exception as exc:
                self.ledger.append(
                    "solver_error",
                    {"item_id": item_id, "error": str(exc), "type": type(exc).__name__},
                )
                if raise_on_solver_error:
                    raise
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
