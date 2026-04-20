from dataclasses import dataclass
from decimal import Decimal
from math import pow

from app.models.entities import PortfolioSnapshot, RetirementProfile
from app.services.market_data import market_data_service


RISK_PROFILE_RETURN = {
    "conservative": 0.05,
    "moderate": 0.07,
    "growth": 0.09,
}


@dataclass(frozen=True)
class AnalysisMetrics:
    portfolio_score: float
    diversification_score: float
    retirement_readiness_score: float
    total_positions: int
    top_holding_weight: float
    top_three_weight: float
    largest_sector_weight: float
    projected_retirement_value: float
    target_retirement_corpus: float
    readiness_band: str
    diversification_commentary: str
    retirement_commentary: str

    def metric_map(self) -> dict[str, str]:
        return {
            "portfolio_score": f"{self.portfolio_score:.2f}",
            "diversification_score": f"{self.diversification_score:.2f}",
            "retirement_readiness_score": f"{self.retirement_readiness_score:.2f}",
            "total_positions": str(self.total_positions),
            "top_holding_weight": f"{self.top_holding_weight:.2f}",
            "top_three_weight": f"{self.top_three_weight:.2f}",
            "largest_sector_weight": f"{self.largest_sector_weight:.2f}",
            "projected_retirement_value": f"{self.projected_retirement_value:.2f}",
            "target_retirement_corpus": f"{self.target_retirement_corpus:.2f}",
            "readiness_band": self.readiness_band,
        }


class PortfolioAnalysisService:
    def analyze(
        self,
        snapshot: PortfolioSnapshot,
        retirement_profile: RetirementProfile | None,
    ) -> AnalysisMetrics:
        values: list[tuple[str, str, float]] = []
        sector_totals: dict[str, float] = {}

        for holding in snapshot.holdings:
            metadata = market_data_service.lookup_metadata(holding.ticker)
            quantity = float(holding.quantity)
            reference_price = (
                metadata.current_price
                or float(holding.average_cost_basis)
                if holding.average_cost_basis
                else 1.0
            )
            market_value = max(quantity * float(reference_price), 0.0)
            sector = holding.sector or metadata.sector or "Unknown"
            label = holding.company_name or metadata.company_name or holding.ticker
            values.append((holding.ticker, sector, market_value))
            sector_totals[sector] = sector_totals.get(sector, 0.0) + market_value

        total_value = sum(value for _, _, value in values) or float(len(values) or 1)
        ordered_values = sorted(values, key=lambda item: item[2], reverse=True)
        weights = [value / total_value for _, _, value in ordered_values]
        top_holding_weight = (weights[0] * 100) if weights else 0.0
        top_three_weight = (sum(weights[:3]) * 100) if weights else 0.0
        largest_sector_weight = (
            max((sector_total / total_value) * 100 for sector_total in sector_totals.values())
            if sector_totals
            else 0.0
        )

        diversification_score = 100.0
        if top_holding_weight > 25:
            diversification_score -= min((top_holding_weight - 25) * 1.2, 30)
        if top_holding_weight > 40:
            diversification_score -= min((top_holding_weight - 40) * 1.5, 20)
        if top_three_weight > 60:
            diversification_score -= min((top_three_weight - 60) * 0.8, 15)
        if len(values) < 5:
            diversification_score -= 15
        if largest_sector_weight > 35:
            diversification_score -= min((largest_sector_weight - 35) * 0.7, 20)
        if any(sector in {"Broad Market ETF", "Large Cap Growth ETF"} for sector in sector_totals):
            diversification_score += 5
        diversification_score = max(min(diversification_score, 100.0), 0.0)

        retirement_readiness_score = 50.0
        projected_retirement_value = 0.0
        target_retirement_corpus = 0.0
        readiness_band = "insufficient_data"
        retirement_commentary = "Add a retirement profile to receive retirement readiness analysis."

        if retirement_profile:
            years = retirement_profile.target_retirement_age - retirement_profile.current_age
            annual_return = RISK_PROFILE_RETURN.get(retirement_profile.risk_profile, 0.07)
            current_savings = float(retirement_profile.current_retirement_savings)
            monthly_contribution = float(retirement_profile.monthly_contribution)
            target_spend = float(retirement_profile.target_annual_retirement_spend)

            projected_retirement_value = self._project_portfolio_value(
                current_savings=current_savings,
                monthly_contribution=monthly_contribution,
                years=years,
                annual_return=annual_return,
            )
            target_retirement_corpus = target_spend / 0.04
            readiness_ratio = (
                projected_retirement_value / target_retirement_corpus if target_retirement_corpus else 0.0
            )
            retirement_readiness_score = min(readiness_ratio * 100, 100.0)
            if readiness_ratio >= 1.1:
                readiness_band = "ahead_of_track"
            elif readiness_ratio >= 0.8:
                readiness_band = "on_track"
            else:
                readiness_band = "behind_track"
            retirement_commentary = (
                f"Projected retirement value is approximately ${projected_retirement_value:,.0f} "
                f"versus a target corpus of ${target_retirement_corpus:,.0f}. "
                f"Current status: {readiness_band.replace('_', ' ')}."
            )

        portfolio_score = (diversification_score * 0.6) + (retirement_readiness_score * 0.4)
        diversification_commentary = (
            f"The portfolio holds {len(values)} positions. "
            f"The largest holding is {top_holding_weight:.1f}% of portfolio value and the top three holdings "
            f"represent {top_three_weight:.1f}%. The largest sector exposure is {largest_sector_weight:.1f}%."
        )

        return AnalysisMetrics(
            portfolio_score=round(portfolio_score, 2),
            diversification_score=round(diversification_score, 2),
            retirement_readiness_score=round(retirement_readiness_score, 2),
            total_positions=len(values),
            top_holding_weight=round(top_holding_weight, 2),
            top_three_weight=round(top_three_weight, 2),
            largest_sector_weight=round(largest_sector_weight, 2),
            projected_retirement_value=round(projected_retirement_value, 2),
            target_retirement_corpus=round(target_retirement_corpus, 2),
            readiness_band=readiness_band,
            diversification_commentary=diversification_commentary,
            retirement_commentary=retirement_commentary,
        )

    @staticmethod
    def _project_portfolio_value(
        current_savings: float,
        monthly_contribution: float,
        years: int,
        annual_return: float,
    ) -> float:
        monthly_return = annual_return / 12
        months = max(years * 12, 1)
        current_value = current_savings * pow(1 + monthly_return, months)
        if monthly_return == 0:
            contribution_value = monthly_contribution * months
        else:
            contribution_value = monthly_contribution * ((pow(1 + monthly_return, months) - 1) / monthly_return)
        return current_value + contribution_value


portfolio_analysis_service = PortfolioAnalysisService()

