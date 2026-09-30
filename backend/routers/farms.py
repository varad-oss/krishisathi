"""Farm digital twin API. A farm is created without any personal data and accessed with the X-Farm-Token
returned once at creation. Responses never include other farms' data."""
from datetime import date
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Header, Path, Request
from pydantic import BaseModel, Field, model_validator

from core.events import log_event
from core.rate_limit import rate_limit
from models.intelligence import FarmIntelligence
from services import farm_twin
from services.intelligence_service import farm_intelligence
from services.regenerative_service import TIMING

router = APIRouter(prefix="/api/farms", tags=["Farm digital twin"])

FarmId = Path(..., min_length=36, max_length=36)
Token = Header(None, alias="X-Farm-Token", max_length=100)


class FarmProfileIn(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    crop: Optional[str] = Field(None, max_length=40)
    sowing_date: Optional[date] = None
    area_ha: Optional[float] = Field(None, gt=0, le=10_000)

    @model_validator(mode="after")
    def _sowing_not_future(self):
        if self.sowing_date and self.sowing_date > date.today():
            raise ValueError("sowing_date cannot be in the future")
        return self


class FeedbackIn(BaseModel):
    followed: Optional[Literal[farm_twin.FOLLOWED]] = None  # type: ignore[valid-type]
    outcome: Optional[Literal[farm_twin.OUTCOMES]] = None   # type: ignore[valid-type]

    @model_validator(mode="after")
    def _something(self):
        if not self.followed and not self.outcome:
            raise ValueError("followed or outcome is required")
        return self


ADOPTION = {"adopted": "yes", "partial": "partial", "skipped": "no"}


class PracticeIn(BaseModel):
    practice: Literal[tuple(TIMING)]  # type: ignore[valid-type]
    status: Literal["adopted", "partial", "skipped"]


class FarmTwinIntelligence(FarmIntelligence):
    twin: dict


async def create_limit(request: Request):
    await rate_limit(request, limit=10, window_seconds=60)


async def farm_access(farm_id: str = FarmId, token: Optional[str] = Token):
    return await farm_twin.authorize(farm_id, token)


@router.post("", status_code=201, dependencies=[Depends(create_limit)])
async def create_farm(body: FarmProfileIn):
    """Registers a farm. The `farm_token` is shown only once; keep it on the device."""
    farm, token = await farm_twin.create_farm(body.lat, body.lng, body.crop, body.sowing_date, body.area_ha)
    log_event("farm_created", farm_id=farm["farm_id"], crop=farm["crop"])
    return {**farm, "farm_token": token}


@router.get("/{farm_id}")
async def get_farm(farm=Depends(farm_access)):
    """The farm's record and history: intelligence snapshots, recommendations with feedback, photo diagnoses."""
    return await farm_twin.history(farm)


@router.post("/{farm_id}")
async def update_farm(body: FarmProfileIn, farm=Depends(farm_access)):
    return await farm_twin.update_farm(farm.id, body.lat, body.lng, body.crop, body.sowing_date, body.area_ha)


@router.get("/{farm_id}/intelligence", response_model=FarmTwinIntelligence)
async def get_farm_intelligence(farm=Depends(farm_access)):
    """Farm intelligence for the stored profile, using the farm's own recent diagnoses. Records a snapshot and
    the recommended action so the farmer can report what they did and what happened."""
    history = {"recent_diagnoses": await farm_twin.recent_diagnoses(farm.id, days=14)}
    intel = await farm_intelligence(farm.lat, farm.lng, farm.crop, farm.sowing_date, history, farm_id=farm.id)
    try:
        twin = await farm_twin.record_intelligence(farm, intel)
    except Exception:  # the farmer still gets the advice; feedback is unavailable for this view
        twin = {"snapshot_id": None, "action": None, "recorded": False}
    return FarmTwinIntelligence(**intel.model_dump(), twin=twin)


@router.post("/{farm_id}/actions/{action_id}/feedback")
async def action_feedback(body: FeedbackIn, action_id: str = Path(..., min_length=36, max_length=36), farm=Depends(farm_access)):
    """Self-reported follow-through ("did you do it?") and outcome ("how did the crop respond?")."""
    result = await farm_twin.submit_feedback(farm.id, action_id, body.followed, body.outcome)
    log_event("feedback_received", farm_id=farm.id, action=result["action"], source_type=result["source_type"],
              followed=body.followed, outcome=body.outcome)
    return result


@router.post("/{farm_id}/practices", status_code=201)
async def record_practice(body: PracticeIn, farm=Depends(farm_access)):
    """Self-reported adoption of a regenerative practice (adopted / partial / skipped), kept in the farm history."""
    action = await farm_twin.record_action(farm, "regenerative", None, body.practice)
    result = await farm_twin.submit_feedback(farm.id, action["action_id"], ADOPTION[body.status], None)
    log_event("practice_reported", farm_id=farm.id, practice=body.practice, status=body.status)
    return result
