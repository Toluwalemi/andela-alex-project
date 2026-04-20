import { AnalysisReport } from "@/lib/types";

export function ReportView({ report }: { report: AnalysisReport | null }) {
  if (!report) {
    return (
      <div className="panel">
        <h3>No report selected</h3>
        <p>Run an analysis or open a previous report from history.</p>
      </div>
    );
  }

  return (
    <div className="grid">
      <section className="panel">
        <h2>Report Scores</h2>
        <div className="metric-grid">
          <div className="metric">
            <strong>{report.portfolio_score ?? "N/A"}</strong>
            <span>Portfolio score</span>
          </div>
          <div className="metric">
            <strong>{report.diversification_score ?? "N/A"}</strong>
            <span>Diversification score</span>
          </div>
          <div className="metric">
            <strong>{report.retirement_readiness_score ?? "N/A"}</strong>
            <span>Retirement readiness</span>
          </div>
        </div>
      </section>
      <section className="panel">
        <h2>Analysis</h2>
        <div className="markdown">{report.summary_markdown}</div>
      </section>
      <section className="panel">
        <h2>Metrics</h2>
        <div className="metric-grid">
          {Object.entries(report.metrics).map(([key, value]) => (
            <div key={key} className="metric">
              <strong>{value}</strong>
              <span>{key.replaceAll("_", " ")}</span>
            </div>
          ))}
        </div>
      </section>
      <section className="panel">
        <h2>Disclaimer</h2>
        <p>{report.disclaimer_text}</p>
      </section>
    </div>
  );
}

