import Link from "next/link";

export default function HomePage() {
  return (
    <div className="grid">
      <section className="hero">
        <div className="panel">
          <p className="tagline">Informational portfolio guidance for individual investors</p>
          <h1>Review allocation, diversification, and retirement readiness in one workflow.</h1>
          <p>
            Alex lets users upload or enter portfolios, stores historical snapshots, computes clear
            portfolio metrics, and pairs them with AI-generated commentary that stays inside an
            informational guidance boundary.
          </p>
          <div className="nav-links">
            <Link href="/dashboard" className="button">
              Open dashboard
            </Link>
            <Link href="/portfolio" className="button secondary">
              Build portfolio
            </Link>
          </div>
        </div>
        <div className="panel">
          <h2>What Alex covers</h2>
          <div className="card-list">
            <div className="metric">
              <strong>Portfolio Review</strong>
              <span>Snapshot holdings, concentration, and sector exposure.</span>
            </div>
            <div className="metric">
              <strong>Retirement Basics</strong>
              <span>Simple projection engine with configurable risk profile assumptions.</span>
            </div>
            <div className="metric">
              <strong>AI Commentary</strong>
              <span>Structured recommendations with explicit assumptions and disclaimers.</span>
            </div>
          </div>
        </div>
      </section>
      <section className="grid two">
        <div className="panel">
          <h2>Manual entry or CSV</h2>
          <p>
            V1 supports direct ticker entry and CSV import with a small, stable schema: ticker,
            quantity, and optional cost basis.
          </p>
        </div>
        <div className="panel">
          <h2>History preserved</h2>
          <p>
            Every import is stored as a portfolio snapshot so users can rerun analysis over time and
            review past recommendations.
          </p>
        </div>
      </section>
    </div>
  );
}

