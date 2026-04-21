from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user, get_db
from app.models.entities import AnalysisMetric, AnalysisReport, PortfolioSnapshot, RetirementProfile, User
from app.schemas.analysis import AnalysisRequest, AnalysisReportResponse, AnalysisSummaryItem
from app.services.openrouter import openrouter_service
from app.services.portfolio_analysis import portfolio_analysis_service

router = APIRouter()


@router.post("/analysis", response_model=AnalysisReportResponse)
async def create_analysis(
    payload: AnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnalysisReportResponse:
    snapshot = db.scalar(
        select(PortfolioSnapshot)
        .options(selectinload(PortfolioSnapshot.holdings))
        .where(
            PortfolioSnapshot.id == payload.portfolio_snapshot_id,
            PortfolioSnapshot.user_id == current_user.id,
        )
    )
    if not snapshot:
        raise HTTPException(status_code=404, detail="Portfolio snapshot not found.")

    profile = None
    if payload.retirement_profile_id:
        profile = db.scalar(
            select(RetirementProfile).where(
                RetirementProfile.id == payload.retirement_profile_id,
                RetirementProfile.user_id == current_user.id,
            )
        )
        if not profile:
            raise HTTPException(status_code=404, detail="Retirement profile not found.")
    else:
        profile = db.scalar(
            select(RetirementProfile).where(RetirementProfile.user_id == current_user.id)
        )

    metrics = portfolio_analysis_service.analyze(
        snapshot=snapshot,
        retirement_profile=profile,
    )

    advisory_markdown = await openrouter_service.generate_advisory_report(
        user=current_user,
        snapshot=snapshot,
        profile=profile,
        metrics=metrics,
    )

    report = AnalysisReport(
        user_id=current_user.id,
        portfolio_snapshot_id=snapshot.id,
        retirement_profile_id=profile.id if profile else None,
        status="completed",
        portfolio_score=metrics.portfolio_score,
        diversification_score=metrics.diversification_score,
        retirement_readiness_score=metrics.retirement_readiness_score,
        summary_markdown=advisory_markdown.summary_markdown,
        recommendations_markdown=advisory_markdown.recommendations_markdown,
        disclaimer_text=advisory_markdown.disclaimer_text,
        model_name=advisory_markdown.model_name,
        prompt_version="v1",
    )
    db.add(report)
    db.flush()

    for key, value in metrics.metric_map().items():
        db.add(
            AnalysisMetric(
                analysis_report_id=report.id,
                metric_key=key,
                metric_value=value,
            )
        )

    db.commit()
    db.refresh(report)
    return AnalysisReportResponse.from_report(report=report, metrics=metrics.metric_map())


@router.get("/analysis", response_model=list[AnalysisSummaryItem])
def list_analysis_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AnalysisSummaryItem]:
    reports = db.scalars(
        select(AnalysisReport)
        .where(AnalysisReport.user_id == current_user.id)
        .order_by(AnalysisReport.created_at.desc())
    ).all()
    return [AnalysisSummaryItem.model_validate(report) for report in reports]


@router.get("/analysis/{analysis_report_id}", response_model=AnalysisReportResponse)
def get_analysis_report(
    analysis_report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnalysisReportResponse:
    report = db.scalar(
        select(AnalysisReport)
        .options(selectinload(AnalysisReport.metrics))
        .where(
            AnalysisReport.id == analysis_report_id,
            AnalysisReport.user_id == current_user.id,
        )
    )
    if not report:
        raise HTTPException(status_code=404, detail="Analysis report not found.")
    return AnalysisReportResponse.from_existing_report(report)


@router.delete("/analysis/{analysis_report_id}", status_code=204)
def delete_analysis_report(
    analysis_report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    report = db.scalar(
        select(AnalysisReport).where(
            AnalysisReport.id == analysis_report_id,
            AnalysisReport.user_id == current_user.id,
        )
    )
    if not report:
        raise HTTPException(status_code=404, detail="Analysis report not found.")

    db.delete(report)
    db.commit()
