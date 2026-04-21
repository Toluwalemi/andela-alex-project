"use client";

import { useAuth } from "@clerk/nextjs";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { AuthGuard } from "@/components/auth-guard";
import { getPortfolio } from "@/lib/api";
import { Portfolio } from "@/lib/types";

export default function PortfolioDetailPage() {
  const { getToken } = useAuth();
  const params = useParams<{ id: string }>();
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const result = await getPortfolio(getToken, params.id);
        setPortfolio(result);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Unable to load portfolio");
      }
    }

    void load();
  }, [getToken, params.id]);

  return (
    <AuthGuard>
      <div className="grid">
        <section className="panel">
          <p className="eyebrow">Portfolio</p>
          <h1>{portfolio?.name ?? "Portfolio details"}</h1>
          <p className="muted">
            Review the holdings in this saved snapshot or return to add another one.
          </p>
          <div className="nav-links">
            <Link href="/portfolio" className="button secondary">
              Back to portfolio input
            </Link>
            <Link href="/analysis" className="button">
              Run analysis
            </Link>
          </div>
          {error ? <p className="danger">{error}</p> : null}
        </section>

        {portfolio ? (
          <>
            <section className="panel">
              <h2>Snapshot details</h2>
              <div className="metric-grid">
                <div className="metric">
                  <strong>{portfolio.holdings.length}</strong>
                  <span>Holdings</span>
                </div>
                <div className="metric">
                  <strong>{portfolio.currency}</strong>
                  <span>Currency</span>
                </div>
                <div className="metric">
                  <strong>{new Date(portfolio.created_at).toLocaleString()}</strong>
                  <span>Saved</span>
                </div>
              </div>
            </section>

            <section className="panel">
              <h2>Holdings</h2>
              <div className="card-list">
                {portfolio.holdings.map((holding) => (
                  <div key={holding.id} className="metric">
                    <strong>{holding.company_name || holding.ticker}</strong>
                    <span>{holding.ticker}</span>
                    <span>
                      {holding.quantity} shares
                      {holding.average_cost_basis ? ` · Avg buy price ${holding.average_cost_basis}` : ""}
                    </span>
                    <span>{holding.sector || holding.asset_type || "Unclassified"}</span>
                  </div>
                ))}
              </div>
            </section>
          </>
        ) : null}
      </div>
    </AuthGuard>
  );
}
