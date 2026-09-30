"""Federated model architecture: metadata, versioning and the aggregation contract.

    country-local training -> ModelUpdate (weights + metadata, no raw data) -> Aggregator -> shared ModelVersion

No country trains a model in this deployment: diagnosis uses an external foundation model and risks come from
a rule engine. So `registry()` reports federation as "not_running" and lists only what really runs. What is
here is the contract a participating country would implement against, plus FedAvg (McMahan et al., 2017) as
the reference aggregation, so updates can be validated and combined the same way everywhere.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal, Optional, Protocol

from config import settings
from services.risk_engine import ENGINE


@dataclass(frozen=True)
class ModelVersion:
    model_id: str
    version: str
    kind: Literal["external_foundation_model", "rule_engine", "federated_model"]
    task: str
    provider: str
    federated: bool
    trained_on: str
    country_codes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ModelUpdate:
    """What a country shares after local training: parameters and counts, never the training records."""
    model_id: str
    base_version: str
    country_code: str
    num_examples: int
    parameters: tuple[float, ...]
    metrics: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class AggregateResult:
    model_id: str
    base_version: str
    parameters: tuple[float, ...]
    contributors: tuple[str, ...]
    total_examples: int
    method: str


class Aggregator(Protocol):
    def aggregate(self, updates: list[ModelUpdate]) -> AggregateResult: ...


class FedAvg:
    """Federated averaging: parameters weighted by each participant's number of training examples."""
    method = "FedAvg (McMahan et al., 2017), example-weighted mean"

    def __init__(self, min_participants: int = 2):
        self.min_participants = min_participants

    def aggregate(self, updates: list[ModelUpdate]) -> AggregateResult:
        if len({u.country_code for u in updates}) < self.min_participants:
            raise ValueError(f"at least {self.min_participants} participating countries are required")
        first = updates[0]
        if any(u.model_id != first.model_id or u.base_version != first.base_version for u in updates):
            raise ValueError("updates must share model_id and base_version")
        if any(len(u.parameters) != len(first.parameters) for u in updates):
            raise ValueError("parameter vectors differ in length")
        if any(u.num_examples <= 0 for u in updates):
            raise ValueError("num_examples must be positive")
        total = sum(u.num_examples for u in updates)
        params = tuple(sum(u.parameters[i] * u.num_examples for u in updates) / total for i in range(len(first.parameters)))
        return AggregateResult(first.model_id, first.base_version, params, tuple(sorted({u.country_code for u in updates})), total, self.method)


def models_in_use() -> list[ModelVersion]:
    return [
        ModelVersion(model_id="crop-diagnosis", version=settings.GEMINI_DIAGNOSIS_MODEL, kind="external_foundation_model",
                     task="photo diagnosis (AI-generated, safety rules applied after)", provider="Google Gemini API", federated=False,
                     trained_on="not trained by KrishiSathi"),
        ModelVersion(model_id="advisory", version=settings.GEMINI_ADVISORY_MODEL, kind="external_foundation_model",
                     task="grounded advisory text", provider="Google Gemini API", federated=False, trained_on="not trained by KrishiSathi"),
        ModelVersion(model_id=ENGINE["id"], version=ENGINE["version"], kind="rule_engine", task="farm risks and top action",
                     provider="KrishiSathi", federated=False, trained_on="no training: published thresholds and rules", country_codes=("IN",)),
    ]


def registry(now: Optional[datetime] = None) -> dict:
    return {
        "schema_version": "1.0",
        "generated_at": (now or datetime.now(timezone.utc)).isoformat(),
        "models": [m.__dict__ | {"country_codes": list(m.country_codes)} for m in models_in_use()],
        "federation": {
            "status": "not_running",
            "reason": "No country-local model training exists in this deployment; only interfaces and metadata are defined.",
            "aggregation_method": FedAvg.method,
            "update_contract": {"fields": ["model_id", "base_version", "country_code", "num_examples", "parameters", "metrics", "created_at"],
                                "raw_data_shared": False},
        },
    }
