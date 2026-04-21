"use client";

import { useAuth, useUser } from "@clerk/nextjs";
import Link from "next/link";
import { useEffect, useState } from "react";

import { AuthGuard } from "@/components/auth-guard";
import { getCurrentUser, listAnalysis, listPortfolios } from "@/lib/api";
import { AnalysisSummary, PortfolioListItem } from "@/lib/types";

export default function DashboardPage() {
  const { user } = useUser();
  const { getToken } = useAuth();
  const [portfolios, setPortfolios] = useState<PortfolioListItem[]>([]);
  const [reports, setReports] = useState<AnalysisSummary[]>([]);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function load() {
      try {
        await getCurrentUser(getToken);
        const [portfolioResult, reportResult] = await Promise.all([
          listPortfolios(getToken),
          listAnalysis(getToken)
        ]);
        setPortfolios(portfolioResult);
        setReports(reportResult);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Unable to load dashboard");
      }
    }

    void load();
  }, [getToken]);

  return (
    <AuthGuard>
      <div className="grid">
        <section className="panel">
          <p className="tagline">Welcome back</p>
          <h1>{user?.firstName ? `${user.firstName},` : "Dashboard"}</h1>
          <p className="muted">
            Start by saving a portfolio, then run a report to review diversification and retirement
            progress.
          </p>
          {error ? <p className="danger">{error}</p> : null}
          <div className="nav-links">
            <Link href="/portfolio" className="button">
              Create portfolio
            </Link>
            <Link href="/analysis" className="button secondary">
              Run analysis
            </Link>
          </div>
        </section>
        <section className="grid two">
          <div className="panel">
            <h2>Portfolio snapshots</h2>
            <div className="card-list">
              {portfolios.length ? (
                portfolios.slice(0, 5).map((portfolio) => (
                  <Link
                    key={portfolio.id}
                    href={`/portfolio?portfolioId=${portfolio.id}`}
                    className="metric metric-link"
                  >
                    <strong>{portfolio.name}</strong>
                    <span>{new Date(portfolio.created_at).toLocaleString()}</span>
                    <span>Open snapshot</span>
                  </Link>
                ))
              ) : (
                <p>No portfolios yet.</p>
              )}
            </div>
          </div>
          <div className="panel">
            <h2>Recent reports</h2>
            <div className="card-list">
              {reports.length ? (
                reports.slice(0, 5).map((report) => (
                  <Link
                    key={report.id}
                    href={`/history?reportId=${report.id}`}
                    className="metric metric-link"
                  >
                    <strong>{report.portfolio_score ?? "N/A"}</strong>
                    <span>{new Date(report.created_at).toLocaleString()}</span>
                    <span>Open report</span>
                  </Link>
                ))
              ) : (
                <p>No reports yet.</p>
              )}
            </div>
          </div>
        </section>
      </div>
    </AuthGuard>
  );
}
