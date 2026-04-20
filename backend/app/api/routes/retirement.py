from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.entities import RetirementProfile, User
from app.schemas.retirement import RetirementProfileCreate, RetirementProfileResponse

router = APIRouter()


@router.post("/retirement-profile", response_model=RetirementProfileResponse)
def upsert_retirement_profile(
    payload: RetirementProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RetirementProfileResponse:
    profile = db.scalar(
        select(RetirementProfile).where(RetirementProfile.user_id == current_user.id)
    )
    if profile:
        profile.current_age = payload.current_age
        profile.target_retirement_age = payload.target_retirement_age
        profile.current_retirement_savings = payload.current_retirement_savings
        profile.monthly_contribution = payload.monthly_contribution
        profile.target_annual_retirement_spend = payload.target_annual_retirement_spend
        profile.risk_profile = payload.risk_profile
        profile.expected_retirement_years = payload.expected_retirement_years
    else:
        profile = RetirementProfile(user_id=current_user.id, **payload.model_dump())
        db.add(profile)

    db.commit()
    db.refresh(profile)
    return RetirementProfileResponse.model_validate(profile)


@router.get("/retirement-profile", response_model=RetirementProfileResponse | None)
def get_retirement_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RetirementProfileResponse | None:
    profile = db.scalar(
        select(RetirementProfile).where(RetirementProfile.user_id == current_user.id)
    )
    if not profile:
        return None
    return RetirementProfileResponse.model_validate(profile)

