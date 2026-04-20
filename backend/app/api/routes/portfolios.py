from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user, get_db
from app.models.entities import Holding, PortfolioSnapshot, UploadJob, User
from app.schemas.portfolio import (
    ManualPortfolioCreate,
    PortfolioListItem,
    PortfolioResponse,
)
from app.services.market_data import market_data_service
from app.services.storage import storage_service
from app.utils.csv_parser import parse_holdings_csv

router = APIRouter()


@router.post("/manual", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
def create_manual_portfolio(
    payload: ManualPortfolioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PortfolioResponse:
    snapshot = PortfolioSnapshot(
        user_id=current_user.id,
        name=payload.name,
        source_type="manual",
        currency=payload.currency,
        notes=payload.notes,
    )
    db.add(snapshot)
    db.flush()

    for holding_input in payload.holdings:
        metadata = market_data_service.lookup_metadata(holding_input.ticker)
        db.add(
            Holding(
                portfolio_snapshot_id=snapshot.id,
                ticker=holding_input.ticker.upper(),
                quantity=holding_input.quantity,
                average_cost_basis=holding_input.average_cost_basis,
                asset_type=metadata.asset_type,
                sector=metadata.sector,
                company_name=metadata.company_name,
            )
        )

    db.commit()
    db.refresh(snapshot)
    snapshot = _get_snapshot_or_404(db, snapshot.id, current_user.id)
    return PortfolioResponse.model_validate(snapshot)


@router.post("/upload-csv", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def upload_csv_portfolio(
    name: str = Form(...),
    currency: str = Form(default="USD"),
    notes: str | None = Form(default=None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PortfolioResponse:
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV uploads are supported.")

    raw_bytes = await file.read()
    rows = parse_holdings_csv(raw_bytes)

    upload_job = UploadJob(
        user_id=current_user.id,
        filename=file.filename,
        status="uploaded",
    )
    db.add(upload_job)
    db.flush()
    upload_job.storage_path = storage_service.store_upload(
        filename=file.filename,
        content=raw_bytes,
    )
    upload_job.status = "parsed"

    snapshot = PortfolioSnapshot(
        user_id=current_user.id,
        name=name,
        source_type="csv",
        currency=currency,
        notes=notes,
    )
    db.add(snapshot)
    db.flush()

    for row in rows:
        metadata = market_data_service.lookup_metadata(row.ticker)
        db.add(
            Holding(
                portfolio_snapshot_id=snapshot.id,
                ticker=row.ticker,
                quantity=row.quantity,
                average_cost_basis=row.average_cost_basis,
                asset_type=metadata.asset_type,
                sector=metadata.sector,
                company_name=metadata.company_name,
            )
        )

    db.commit()
    return PortfolioResponse.model_validate(_get_snapshot_or_404(db, snapshot.id, current_user.id))


@router.get("", response_model=list[PortfolioListItem])
def list_portfolios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PortfolioListItem]:
    snapshots = db.scalars(
        select(PortfolioSnapshot)
        .where(PortfolioSnapshot.user_id == current_user.id)
        .order_by(PortfolioSnapshot.created_at.desc())
    ).all()
    return [PortfolioListItem.model_validate(snapshot) for snapshot in snapshots]


@router.get("/{portfolio_snapshot_id}", response_model=PortfolioResponse)
def get_portfolio(
    portfolio_snapshot_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PortfolioResponse:
    snapshot = _get_snapshot_or_404(db, portfolio_snapshot_id, current_user.id)
    return PortfolioResponse.model_validate(snapshot)


@router.delete("/{portfolio_snapshot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio(
    portfolio_snapshot_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    snapshot = _get_snapshot_or_404(db, portfolio_snapshot_id, current_user.id)
    db.delete(snapshot)
    db.commit()


def _get_snapshot_or_404(db: Session, snapshot_id: str, user_id: str) -> PortfolioSnapshot:
    snapshot = db.scalar(
        select(PortfolioSnapshot)
        .options(selectinload(PortfolioSnapshot.holdings))
        .where(
            PortfolioSnapshot.id == snapshot_id,
            PortfolioSnapshot.user_id == user_id,
        )
    )
    if not snapshot:
        raise HTTPException(status_code=404, detail="Portfolio snapshot not found.")
    return snapshot

