"use client";

import { useAuth } from "@clerk/nextjs";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { AuthGuard } from "@/components/auth-guard";
import { createManualPortfolio, getPortfolio, uploadCsvPortfolio } from "@/lib/api";
import { Portfolio } from "@/lib/types";

type HoldingInput = {
  ticker: string;
  quantity: string;
  average_cost_basis: string;
};

const EMPTY_HOLDING: HoldingInput = { ticker: "", quantity: "", average_cost_basis: "" };

export default function PortfolioPage() {
  const { getToken } = useAuth();
  const router = useRouter();
  const [name, setName] = useState("My Portfolio");
  const [currency, setCurrency] = useState("USD");
  const [notes, setNotes] = useState("");
  const [holdings, setHoldings] = useState<HoldingInput[]>([EMPTY_HOLDING]);
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadSelectedPortfolio() {
      const portfolioId =
        typeof window !== "undefined"
          ? new URLSearchParams(window.location.search).get("portfolioId")
          : null;

      if (!portfolioId) {
        setSelectedPortfolio(null);
        return;
      }

      try {
        const result = await getPortfolio(getToken, portfolioId);
        setSelectedPortfolio(result);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Unable to load portfolio");
      }
    }

    void loadSelectedPortfolio();
  }, [getToken]);

  function updateHolding(index: number, field: keyof HoldingInput, value: string) {
    setHoldings((current) =>
      current.map((holding, itemIndex) =>
        itemIndex === index ? { ...holding, [field]: value } : holding
      )
    );
  }

  async function submitManual() {
    setLoading(true);
    setError("");
    try {
      const payload = {
        name,
        currency,
        notes,
        holdings: holdings
          .filter((holding) => holding.ticker && holding.quantity)
          .map((holding) => ({
            ticker: holding.ticker,
            quantity: Number(holding.quantity),
            average_cost_basis: holding.average_cost_basis ? Number(holding.average_cost_basis) : null
          }))
      };
      const result = await createManualPortfolio(getToken, payload);
      router.push(`/analysis?portfolioId=${result.id}`);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to save portfolio");
    } finally {
      setLoading(false);
    }
  }

  async function submitCsv() {
    if (!csvFile) {
      setError("Select a CSV file first.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const result = await uploadCsvPortfolio(getToken, {
        name,
        currency,
        notes,
        file: csvFile
      });
      router.push(`/analysis?portfolioId=${result.id}`);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to upload CSV");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthGuard>
      <div className="grid">
        {selectedPortfolio ? (
          <section className="panel">
            <p className="eyebrow">Saved Snapshot</p>
            <h1>{selectedPortfolio.name}</h1>
            <p className="muted">
              This snapshot contains {selectedPortfolio.holdings.length} holdings. You can review
              it here or continue to analysis.
            </p>
            <div className="nav-links">
              <Link href={`/analysis?portfolioId=${selectedPortfolio.id}`} className="button">
                Analyze this portfolio
              </Link>
              <Link href="/portfolio" className="button secondary">
                Create another portfolio
              </Link>
            </div>
            <div className="card-list">
              {selectedPortfolio.holdings.map((holding) => (
                <div key={holding.id} className="metric">
                  <strong>{holding.company_name || holding.ticker}</strong>
                  <span>{holding.ticker}</span>
                  <span>
                    {holding.quantity} shares
                    {holding.average_cost_basis ? ` · Avg buy price ${holding.average_cost_basis}` : ""}
                  </span>
                </div>
              ))}
            </div>
          </section>
        ) : null}

        <div className="grid two">
          <section className="panel">
          <h1>Portfolio Input</h1>
          <p className="notice">
            Add the investments you own. For CSV uploads, use the columns `ticker`, `quantity`,
            and optional `average_cost_basis`.
          </p>
          <form
            onSubmit={(event) => {
              event.preventDefault();
              void submitManual();
            }}
          >
            <label>
              Portfolio name
              <input value={name} onChange={(event) => setName(event.target.value)} />
            </label>
            <div className="inline-grid">
              <label>
                Currency
                <input value={currency} onChange={(event) => setCurrency(event.target.value)} />
              </label>
              <label>
                Notes
                <input value={notes} onChange={(event) => setNotes(event.target.value)} />
              </label>
            </div>
            {holdings.map((holding, index) => (
              <div key={`${index}-${holding.ticker}`} className="inline-grid">
                <label>
                  Asset symbol
                  <input
                    placeholder="AAPL"
                    value={holding.ticker}
                    onChange={(event) => updateHolding(index, "ticker", event.target.value)}
                  />
                </label>
                <label>
                  Shares owned
                  <input
                    type="number"
                    step="0.0001"
                    placeholder="10"
                    value={holding.quantity}
                    onChange={(event) => updateHolding(index, "quantity", event.target.value)}
                  />
                </label>
                <label>
                  Average buy price
                  <input
                    type="number"
                    step="0.01"
                    placeholder="185.50"
                    value={holding.average_cost_basis}
                    onChange={(event) =>
                      updateHolding(index, "average_cost_basis", event.target.value)
                    }
                  />
                </label>
              </div>
            ))}
            <div className="nav-links">
              <button
                type="button"
                className="secondary"
                onClick={() => setHoldings((current) => [...current, EMPTY_HOLDING])}
              >
                Add holding
              </button>
              <button type="submit" disabled={loading}>
                Save manual portfolio
              </button>
            </div>
          </form>
          </section>
          <section className="panel">
            <h2>CSV Upload</h2>
            <p className="muted">
              Upload the same information in a spreadsheet: asset symbol, shares owned, and optional
              average buy price.
            </p>
            <form
              onSubmit={(event) => {
                event.preventDefault();
                void submitCsv();
              }}
            >
              <label>
                Portfolio CSV
                <input
                  type="file"
                  accept=".csv"
                  onChange={(event) => setCsvFile(event.target.files?.[0] ?? null)}
                />
              </label>
              <button type="submit" disabled={loading}>
                Upload CSV
              </button>
            </form>
            {error ? <p className="danger">{error}</p> : null}
          </section>
        </div>
      </div>
    </AuthGuard>
  );
}
