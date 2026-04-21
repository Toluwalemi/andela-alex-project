"use client";

import { useAuth } from "@clerk/nextjs";
import { useEffect, useState } from "react";

import { AuthGuard } from "@/components/auth-guard";
import { ReportView } from "@/components/report-view";
import { deleteAnalysis, getAnalysis, listAnalysis } from "@/lib/api";
import { AnalysisReport, AnalysisSummary } from "@/lib/types";

export default function HistoryPage() {
  const { getToken } = useAuth();
  const [reports, setReports] = useState<AnalysisSummary[]>([]);
  const [selectedReport, setSelectedReport] = useState<AnalysisReport | null>(null);
  const [selectedReportId, setSelectedReportId] = useState<string>("");
  const [error, setError] = useState("");
  const [deletingReportId, setDeletingReportId] = useState<string>("");

  useEffect(() => {
    async function load() {
      try {
        const result = await listAnalysis(getToken);
        setReports(result);
        const preferredReportId =
          typeof window !== "undefined"
            ? new URLSearchParams(window.location.search).get("reportId")
            : null;
        const initialReportId =
          preferredReportId && result.some((report) => report.id === preferredReportId)
            ? preferredReportId
            : result[0]?.id;
        if (initialReportId) {
          const fullReport = await getAnalysis(getToken, initialReportId);
          setSelectedReport(fullReport);
          setSelectedReportId(initialReportId);
        }
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Unable to load report history");
      }
    }

    void load();
  }, [getToken]);

  async function handleDelete(reportId: string) {
    setDeletingReportId(reportId);
    setError("");
    try {
      await deleteAnalysis(getToken, reportId);
      const remainingReports = reports.filter((report) => report.id !== reportId);
      setReports(remainingReports);

      if (selectedReportId === reportId) {
        const nextReportId = remainingReports[0]?.id ?? "";
        setSelectedReportId(nextReportId);
        if (nextReportId) {
          const fullReport = await getAnalysis(getToken, nextReportId);
          setSelectedReport(fullReport);
        } else {
          setSelectedReport(null);
        }
      }
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Unable to delete report");
    } finally {
      setDeletingReportId("");
    }
  }

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
                <div key={report.id} className="compact-item">
                  <button
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
                  <div className="compact-actions">
                    <button
                      type="button"
                      className="danger"
                      disabled={deletingReportId === report.id}
                      onClick={() => {
                        void handleDelete(report.id);
                      }}
                    >
                      {deletingReportId === report.id ? "Deleting..." : "Delete"}
                    </button>
                  </div>
                </div>
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
