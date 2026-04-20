import json
from dataclasses import dataclass

import httpx

from app.core.config import settings
from app.models.entities import PortfolioSnapshot, RetirementProfile, User
from app.services.portfolio_analysis import AnalysisMetrics


@dataclass(frozen=True)
class AdvisoryReport:
    summary_markdown: str
    recommendations_markdown: str
    disclaimer_text: str
    model_name: str


class OpenRouterService:
    async def generate_advisory_report(
        self,
        user: User,
        snapshot: PortfolioSnapshot,
        profile: RetirementProfile | None,
        metrics: AnalysisMetrics,
    ) -> AdvisoryReport:
        if not settings.openrouter_api_key:
            return self._fallback_report(metrics)

        payload = {
            "model": settings.openrouter_model,
            "messages": [
                {"role": "system", "content": self._system_prompt()},
                {
                    "role": "user",
                    "content": self._build_user_prompt(
                        user=user,
                        snapshot=snapshot,
                        profile=profile,
                        metrics=metrics,
                    ),
                },
            ],
        }
        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.openrouter_site_url,
            "X-Title": settings.openrouter_site_name,
        }

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return AdvisoryReport(
                summary_markdown=content,
                recommendations_markdown=content,
                disclaimer_text=(
                    "Alex provides informational guidance only and does not replace a licensed financial advisor."
                ),
                model_name=settings.openrouter_model,
            )
        except Exception:  # noqa: BLE001
            return self._fallback_report(metrics)

    @staticmethod
    def _system_prompt() -> str:
        return (
            "You are Alex, an informational financial planning assistant. "
            "Use only the provided facts. Do not invent figures. "
            "Do not claim to be a regulated advisor. "
            "Avoid direct buy or sell instructions. "
            "Write concise markdown with sections titled: Portfolio Summary, "
            "Diversification Findings, Retirement Outlook, Recommended Next Steps, Risks and Assumptions, Disclaimer."
        )

    @staticmethod
    def _build_user_prompt(
        user: User,
        snapshot: PortfolioSnapshot,
        profile: RetirementProfile | None,
        metrics: AnalysisMetrics,
    ) -> str:
        prompt_payload = {
            "user_id": user.id,
            "portfolio_name": snapshot.name,
            "holdings": [
                {
                    "ticker": holding.ticker,
                    "quantity": float(holding.quantity),
                    "cost_basis": float(holding.average_cost_basis) if holding.average_cost_basis else None,
                    "sector": holding.sector,
                    "asset_type": holding.asset_type,
                }
                for holding in snapshot.holdings
            ],
            "retirement_profile": {
                "current_age": profile.current_age,
                "target_retirement_age": profile.target_retirement_age,
                "current_retirement_savings": float(profile.current_retirement_savings),
                "monthly_contribution": float(profile.monthly_contribution),
                "target_annual_retirement_spend": float(profile.target_annual_retirement_spend),
                "risk_profile": profile.risk_profile,
                "expected_retirement_years": profile.expected_retirement_years,
            }
            if profile
            else None,
            "metrics": metrics.metric_map(),
        }
        return json.dumps(prompt_payload, indent=2)

    @staticmethod
    def _fallback_report(metrics: AnalysisMetrics) -> AdvisoryReport:
        content = f"""## Portfolio Summary

Your current portfolio score is **{metrics.portfolio_score:.1f}/100**. The analysis indicates a diversification score of **{metrics.diversification_score:.1f}/100** and a retirement readiness score of **{metrics.retirement_readiness_score:.1f}/100**.

## Diversification Findings

{metrics.diversification_commentary}

## Retirement Outlook

{metrics.retirement_commentary}

## Recommended Next Steps

- Reduce concentration in oversized positions if a small number of holdings dominate your allocation.
- Consider broader ETF exposure if sector diversification is limited.
- Review contribution rate and target retirement spending assumptions at least quarterly.

## Risks and Assumptions

- Sector data and price data may be delayed or incomplete.
- Retirement projections rely on assumed returns and a simplified withdrawal rule.

## Disclaimer

Alex provides informational guidance only and does not replace a licensed financial advisor.
"""
        return AdvisoryReport(
            summary_markdown=content,
            recommendations_markdown=content,
            disclaimer_text="Alex provides informational guidance only and does not replace a licensed financial advisor.",
            model_name="fallback-local-logic",
        )


openrouter_service = OpenRouterService()

