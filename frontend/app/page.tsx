import Link from "next/link";

export default function HomePage() {
  return (
    <div className="grid">
      <section className="hero">
        <div className="panel hero-copy">
          <p className="eyebrow">Portfolio Guidance</p>
          <h1>Understand your portfolio in minutes.</h1>
          <p>Upload holdings, review diversification, and check retirement readiness.</p>
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
          <p className="eyebrow">What Alex Does</p>
          <h2>Simple inputs. Clear outputs.</h2>
          <div className="card-list">
            <div className="metric">
              <strong>Portfolio review</strong>
              <span>See concentration, sector exposure, and position mix.</span>
            </div>
            <div className="metric">
              <strong>Retirement check</strong>
              <span>Estimate whether current savings are on track.</span>
            </div>
            <div className="metric">
              <strong>Readable report</strong>
              <span>Turn raw numbers into a short plain-English summary.</span>
            </div>
          </div>
        </div>
      </section>
      <section className="grid two">
        <div className="panel">
          <h2>Upload or enter holdings</h2>
          <p className="muted">Use a CSV or enter holdings one by one.</p>
        </div>
        <div className="panel">
          <h2>Keep past reports</h2>
          <p className="muted">Alex stores snapshots so you can review changes over time.</p>
        </div>
      </section>
    </div>
  );
}
