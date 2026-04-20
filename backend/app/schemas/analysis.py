from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.entities import AnalysisReport


class AnalysisRequest(BaseModel):
    portfolio_snapshot_id: str
    retirement_profile_id: str | None = None


class AnalysisSummaryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    portfolio_snapshot_id: str
    status: str
    portfolio_score: Decimal | None
    diversification_score: Decimal | None
    retirement_readiness_score: Decimal | None
    created_at: datetime


class AnalysisReportResponse(BaseModel):
    id: str
    portfolio_snapshot_id: str
    retirement_profile_id: str | None
    status: str
    portfolio_score: float | None
    diversification_score: float | None
    retirement_readiness_score: float | None
    summary_markdown: str
    recommendations_markdown: str
    disclaimer_text: str
    model_name: str
    prompt_version: str
    metrics: dict[str, str]
    created_at: datetime

    @classmethod
    def from_report(cls, report: AnalysisReport, metrics: dict[str, str]) -> "AnalysisReportResponse":
        return cls(
            id=report.id,
            portfolio_snapshot_id=report.portfolio_snapshot_id,
            retirement_profile_id=report.retirement_profile_id,
            status=report.status,
            portfolio_score=float(report.portfolio_score) if report.portfolio_score is not None else None,
            diversification_score=float(report.diversification_score) if report.diversification_score is not None else None,
            retirement_readiness_score=float(report.retirement_readiness_score) if report.retirement_readiness_score is not None else None,
            summary_markdown=report.summary_markdown,
            recommendations_markdown=report.recommendations_markdown,
            disclaimer_text=report.disclaimer_text,
            model_name=report.model_name,
            prompt_version=report.prompt_version,
            metrics=metrics,
            created_at=report.created_at,
        )

    @classmethod
    def from_existing_report(cls, report: AnalysisReport) -> "AnalysisReportResponse":
        return cls.from_report(
            report=report,
            metrics={metric.metric_key: metric.metric_value for metric in report.metrics},
        )

