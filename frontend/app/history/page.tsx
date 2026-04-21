"use client";

import { useAuth } from "@clerk/nextjs";
import { useEffect, useState } from "react";

import { AuthGuard } from "@/components/auth-guard";
import { ReportView } from "@/components/report-view";
import { getAnalysis, listAnalysis } from "@/lib/api";
import { AnalysisReport, AnalysisSummary } from "@/lib/types";

export default function HistoryPage() {
  const { getToken } = useAuth();
  const [reports, setReports] = useState<AnalysisSummary[]>([]);
  const [selectedReport, setSelectedReport] = useState<AnalysisReport | null>(null);
  const [selectedReportId, setSelectedReportId] = useState<string>("");
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const result = await listAnalysis(getToken);
        setReports(result);
        if (result[0]) {
          const fullReport = await getAnalysis(getToken, result[0].id);
          setSelectedReport(fullReport);
          setSelectedReportId(result[0].id);
        }
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Unable to load report history");
      }
    }

    void load();
  }, [getToken]);

  return (
    <AuthGuard>
      <div className="grid two">
        <section className="panel">
          <p className="eyebrow">History</p>
          <h1>Past reports</h1>
          <p className="muted">Open any saved analysis to review the summary and scores.</p>
          {error ? <p className="danger">{error}</p> : null}
          <div className="compact-list">
            {reports.length ? (
              reports.map((report) => (
                <button
                  key={report.id}
                  className={`compact-button ${selectedReportId === report.id ? "active" : ""}`}
                  type="button"
                  onClick={async () => {
                    try {
                      const fullReport = await getAnalysis(getToken, report.id);
                      setSelectedReport(fullReport);
                      setSelectedReportId(report.id);
                    } catch (selectError) {
                      setError(
                        selectError instanceof Error ? selectError.message : "Unable to open report"
                      );
                    }
                  }}
                >
                  <div className="stack">
                    <strong>{new Date(report.created_at).toLocaleString()}</strong>
                    <span>
                      Portfolio {report.portfolio_score ?? "N/A"} · Diversification{" "}
                      {report.diversification_score ?? "N/A"} · Retirement{" "}
                      {report.retirement_readiness_score ?? "N/A"}
                    </span>
                  </div>
                </button>
              ))
            ) : (
              <p>No reports available yet.</p>
            )}
          </div>
        </section>
        <ReportView report={selectedReport} />
      </div>
    </AuthGuard>
  );
}
