from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    clerk_user_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    portfolios: Mapped[list["PortfolioSnapshot"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    retirement_profiles: Mapped[list["RetirementProfile"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    analysis_reports: Mapped[list["AnalysisReport"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    source_type: Mapped[str] = mapped_column(String(32))
    currency: Mapped[str] = mapped_column(String(12), default="USD")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped["User"] = relationship(back_populates="portfolios")
    holdings: Mapped[list["Holding"]] = relationship(back_populates="portfolio_snapshot", cascade="all, delete-orphan")
    analysis_reports: Mapped[list["AnalysisReport"]] = relationship(back_populates="portfolio_snapshot", cascade="all, delete-orphan")


class Holding(Base):
    __tablename__ = "holdings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_snapshot_id: Mapped[str] = mapped_column(ForeignKey("portfolio_snapshots.id"), index=True)
    ticker: Mapped[str] = mapped_column(String(20), index=True)
    quantity: Mapped[float] = mapped_column(Numeric(18, 4))
    average_cost_basis: Mapped[Optional[float]] = mapped_column(Numeric(18, 4), nullable=True)
    asset_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sector: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    portfolio_snapshot: Mapped["PortfolioSnapshot"] = relationship(back_populates="holdings")


class RetirementProfile(Base):
    __tablename__ = "retirement_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    current_age: Mapped[int] = mapped_column()
    target_retirement_age: Mapped[int] = mapped_column()
    current_retirement_savings: Mapped[float] = mapped_column(Numeric(18, 2))
    monthly_contribution: Mapped[float] = mapped_column(Numeric(18, 2))
    target_annual_retirement_spend: Mapped[float] = mapped_column(Numeric(18, 2))
    risk_profile: Mapped[str] = mapped_column(String(32))
    expected_retirement_years: Mapped[Optional[int]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    user: Mapped["User"] = relationship(back_populates="retirement_profiles")
    analysis_reports: Mapped[list["AnalysisReport"]] = relationship(back_populates="retirement_profile")


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    portfolio_snapshot_id: Mapped[str] = mapped_column(ForeignKey("portfolio_snapshots.id"), index=True)
    retirement_profile_id: Mapped[Optional[str]] = mapped_column(ForeignKey("retirement_profiles.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(32))
    portfolio_score: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    diversification_score: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    retirement_readiness_score: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    summary_markdown: Mapped[str] = mapped_column(Text)
    recommendations_markdown: Mapped[str] = mapped_column(Text)
    disclaimer_text: Mapped[str] = mapped_column(Text)
    model_name: Mapped[str] = mapped_column(String(255))
    prompt_version: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped["User"] = relationship(back_populates="analysis_reports")
    portfolio_snapshot: Mapped["PortfolioSnapshot"] = relationship(back_populates="analysis_reports")
    retirement_profile: Mapped["RetirementProfile"] = relationship(back_populates="analysis_reports")
    metrics: Mapped[list["AnalysisMetric"]] = relationship(back_populates="analysis_report", cascade="all, delete-orphan")


class AnalysisMetric(Base):
    __tablename__ = "analysis_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_report_id: Mapped[str] = mapped_column(ForeignKey("analysis_reports.id"), index=True)
    metric_key: Mapped[str] = mapped_column(String(100), index=True)
    metric_value: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    analysis_report: Mapped["AnalysisReport"] = relationship(back_populates="metrics")


class UploadJob(Base):
    __tablename__ = "upload_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    storage_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(32))
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
