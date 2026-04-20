from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RetirementProfileCreate(BaseModel):
    current_age: int = Field(ge=18, le=100)
    target_retirement_age: int = Field(ge=40, le=100)
    current_retirement_savings: Decimal = Field(ge=0)
    monthly_contribution: Decimal = Field(ge=0)
    target_annual_retirement_spend: Decimal = Field(gt=0)
    risk_profile: str = Field(pattern="^(conservative|moderate|growth)$")
    expected_retirement_years: int | None = Field(default=30, ge=1, le=60)

    @model_validator(mode="after")
    def validate_retirement_age(self) -> "RetirementProfileCreate":
        if self.target_retirement_age <= self.current_age:
            raise ValueError("Target retirement age must be greater than current age.")
        return self


class RetirementProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    current_age: int
    target_retirement_age: int
    current_retirement_savings: Decimal
    monthly_contribution: Decimal
    target_annual_retirement_spend: Decimal
    risk_profile: str
    expected_retirement_years: int | None
    updated_at: datetime

