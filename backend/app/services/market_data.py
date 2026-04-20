from dataclasses import dataclass
from functools import lru_cache

import yfinance as yf


@dataclass(frozen=True)
class TickerMetadata:
    ticker: str
    company_name: str | None = None
    sector: str | None = None
    asset_type: str | None = None
    current_price: float | None = None


STATIC_FALLBACKS: dict[str, TickerMetadata] = {
    "VOO": TickerMetadata(ticker="VOO", company_name="Vanguard S&P 500 ETF", sector="Broad Market ETF", asset_type="ETF"),
    "VTI": TickerMetadata(ticker="VTI", company_name="Vanguard Total Stock Market ETF", sector="Broad Market ETF", asset_type="ETF"),
    "QQQ": TickerMetadata(ticker="QQQ", company_name="Invesco QQQ Trust", sector="Large Cap Growth ETF", asset_type="ETF"),
    "SPY": TickerMetadata(ticker="SPY", company_name="SPDR S&P 500 ETF Trust", sector="Broad Market ETF", asset_type="ETF"),
    "AAPL": TickerMetadata(ticker="AAPL", company_name="Apple Inc.", sector="Technology", asset_type="Equity"),
    "MSFT": TickerMetadata(ticker="MSFT", company_name="Microsoft Corporation", sector="Technology", asset_type="Equity"),
    "GOOGL": TickerMetadata(ticker="GOOGL", company_name="Alphabet Inc.", sector="Communication Services", asset_type="Equity"),
}


class MarketDataService:
    @lru_cache(maxsize=256)
    def lookup_metadata(self, ticker: str) -> TickerMetadata:
        normalized = ticker.strip().upper()
        try:
            info = yf.Ticker(normalized).fast_info
            current_price = float(info.get("lastPrice")) if info.get("lastPrice") else None
        except Exception:  # noqa: BLE001
            current_price = None

        try:
            detailed = yf.Ticker(normalized).info
            metadata = TickerMetadata(
                ticker=normalized,
                company_name=detailed.get("shortName") or detailed.get("longName"),
                sector=detailed.get("sectorDisp") or detailed.get("sector") or detailed.get("category"),
                asset_type=detailed.get("quoteType"),
                current_price=current_price,
            )
        except Exception:  # noqa: BLE001
            metadata = TickerMetadata(ticker=normalized, current_price=current_price)

        fallback = STATIC_FALLBACKS.get(normalized)
        if fallback:
            return TickerMetadata(
                ticker=normalized,
                company_name=metadata.company_name or fallback.company_name,
                sector=metadata.sector or fallback.sector,
                asset_type=metadata.asset_type or fallback.asset_type,
                current_price=metadata.current_price or fallback.current_price,
            )
        return metadata


market_data_service = MarketDataService()

