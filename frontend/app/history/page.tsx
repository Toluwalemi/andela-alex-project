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
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const result = await listAnalysis(getToken);
        setReports(result);
        if (result[0]) {
          const fullReport = await getAnalysis(getToken, result[0].id);
          setSelectedReport(fullReport);
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
          <h1>Report History</h1>
          {error ? <p className="danger">{error}</p> : null}
          <div className="card-list">
            {reports.length ? (
              reports.map((report) => (
                <button
                  key={report.id}
                  className="secondary"
                  type="button"
                  onClick={async () => {
                    try {
                      const fullReport = await getAnalysis(getToken, report.id);
                      setSelectedReport(fullReport);
                    } catch (selectError) {
                      setError(
                        selectError instanceof Error ? selectError.message : "Unable to open report"
                      );
                    }
                  }}
                >
                  {new Date(report.created_at).toLocaleString()} · portfolio score{" "}
                  {report.portfolio_score ?? "N/A"}
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

