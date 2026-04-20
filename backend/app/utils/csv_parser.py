import csv
from dataclasses import dataclass
from decimal import Decimal
from io import StringIO

from fastapi import HTTPException


@dataclass(frozen=True)
class ParsedHolding:
    ticker: str
    quantity: Decimal
    average_cost_basis: Decimal | None


def parse_holdings_csv(raw_bytes: bytes) -> list[ParsedHolding]:
    try:
        decoded = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded.") from exc

    reader = csv.DictReader(StringIO(decoded))
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV file is missing headers.")

    required = {"ticker", "quantity"}
    if not required.issubset({field.strip().lower() for field in reader.fieldnames}):
        raise HTTPException(status_code=400, detail="CSV must include ticker and quantity columns.")

    parsed: list[ParsedHolding] = []
    for index, row in enumerate(reader, start=2):
        ticker = (row.get("ticker") or "").strip().upper()
        quantity = (row.get("quantity") or "").strip()
        cost_basis = (row.get("average_cost_basis") or "").strip()

        if not ticker:
            raise HTTPException(status_code=400, detail=f"Missing ticker on row {index}.")
        if not quantity:
            raise HTTPException(status_code=400, detail=f"Missing quantity on row {index}.")

        try:
            quantity_value = Decimal(quantity)
            if quantity_value <= 0:
                raise ValueError
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=f"Invalid quantity on row {index}.") from exc

        average_cost_basis = None
        if cost_basis:
            try:
                average_cost_basis = Decimal(cost_basis)
                if average_cost_basis <= 0:
                    raise ValueError
            except Exception as exc:  # noqa: BLE001
                raise HTTPException(status_code=400, detail=f"Invalid average_cost_basis on row {index}.") from exc

        parsed.append(
            ParsedHolding(
                ticker=ticker,
                quantity=quantity_value,
                average_cost_basis=average_cost_basis,
            )
        )

    if not parsed:
        raise HTTPException(status_code=400, detail="CSV must contain at least one holding.")

    return parsed

