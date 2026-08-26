from __future__ import annotations

from fastapi import APIRouter

from ..errors import AppError
from .engine import IdentityRescueEngine, InvalidSimulationAction, ScenarioNotFound
from .models import (
    AnalyzeRequest,
    ScenarioAnalysis,
    ScenarioSummary,
    SimulateRequest,
    SourceReference,
)

router = APIRouter(prefix="/identity", tags=["Identity Rescue"])
engine = IdentityRescueEngine()


@router.get("/scenarios", response_model=list[ScenarioSummary])
def list_scenarios() -> list[ScenarioSummary]:
    return engine.list_scenarios()


@router.post("/scenarios/{scenario_id}/analyze", response_model=ScenarioAnalysis)
def analyze_scenario(scenario_id: str, body: AnalyzeRequest) -> ScenarioAnalysis:
    try:
        return engine.analyze(scenario_id, body.applied_action_ids)
    except ScenarioNotFound as exc:
        raise AppError("SCENARIO_NOT_FOUND") from exc
    except InvalidSimulationAction as exc:
        raise AppError("VALIDATION_ERROR", detail={"field": "applied_action_ids"}) from exc


@router.post("/scenarios/{scenario_id}/simulate", response_model=ScenarioAnalysis)
def simulate_scenario(scenario_id: str, body: SimulateRequest) -> ScenarioAnalysis:
    try:
        return engine.simulate(scenario_id, body.action_id, body.applied_action_ids)
    except ScenarioNotFound as exc:
        raise AppError("SCENARIO_NOT_FOUND") from exc
    except InvalidSimulationAction as exc:
        raise AppError("VALIDATION_ERROR", detail={"field": "action_id"}) from exc


@router.get("/sources", response_model=list[SourceReference])
def list_sources() -> list[SourceReference]:
    return engine.list_sources()
