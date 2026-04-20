from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HoldingInput(BaseModel):
    ticker: str = Field(min_length=1, max_length=20)
    quantity: Decimal = Field(gt=0)
    average_cost_basis: Decimal | None = Field(default=None, gt=0)

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        return value.strip().upper()


class HoldingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ticker: str
    quantity: Decimal
    average_cost_basis: Decimal | None
    asset_type: str | None
    sector: str | None
    company_name: str | None


class ManualPortfolioCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    currency: str = Field(default="USD", min_length=3, max_length=12)
    notes: str | None = Field(default=None, max_length=2_000)
    holdings: list[HoldingInput] = Field(min_length=1)


class PortfolioListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    source_type: str
    currency: str
    created_at: datetime


class PortfolioResponse(PortfolioListItem):
    holdings: list[HoldingResponse]

