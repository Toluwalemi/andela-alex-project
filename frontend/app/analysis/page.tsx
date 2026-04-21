"use client";

import { useAuth } from "@clerk/nextjs";
import { useEffect, useState } from "react";

import { AuthGuard } from "@/components/auth-guard";
import { ReportView } from "@/components/report-view";
import { createAnalysis, getRetirementProfile, listPortfolios, upsertRetirementProfile } from "@/lib/api";
import { AnalysisReport, PortfolioListItem, RetirementProfile } from "@/lib/types";

export default function AnalysisPage() {
  const { getToken } = useAuth();
  const [portfolios, setPortfolios] = useState<PortfolioListItem[]>([]);
  const [selectedPortfolioId, setSelectedPortfolioId] = useState("");
  const [retirementProfile, setRetirementProfile] = useState({
    current_age: 35,
    target_retirement_age: 65,
    current_retirement_savings: 100000,
    monthly_contribution: 1000,
    target_annual_retirement_spend: 60000,
    risk_profile: "moderate" as "conservative" | "moderate" | "growth",
    expected_retirement_years: 30
  });
  const [savedProfile, setSavedProfile] = useState<RetirementProfile | null>(null);
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const [portfolioResult, profileResult] = await Promise.all([
          listPortfolios(getToken),
          getRetirementProfile(getToken)
        ]);
        setPortfolios(portfolioResult);
        if (portfolioResult[0]) {
          setSelectedPortfolioId(portfolioResult[0].id);
        }
        if (profileResult) {
          setSavedProfile(profileResult);
          setRetirementProfile({
            current_age: profileResult.current_age,
            target_retirement_age: profileResult.target_retirement_age,
            current_retirement_savings: profileResult.current_retirement_savings,
            monthly_contribution: profileResult.monthly_contribution,
            target_annual_retirement_spend: profileResult.target_annual_retirement_spend,
            risk_profile: profileResult.risk_profile,
            expected_retirement_years: profileResult.expected_retirement_years ?? 30
          });
        }
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Unable to load analysis setup");
      }
    }

    void load();
  }, [getToken]);

  async function saveProfile() {
    setLoading(true);
    setError("");
    try {
      const profile = await upsertRetirementProfile(getToken, retirementProfile);
      setSavedProfile(profile);
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Unable to save retirement profile");
    } finally {
      setLoading(false);
    }
  }

  async function runAnalysis() {
    if (!selectedPortfolioId) {
      setError("Create a portfolio snapshot first.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const profile = savedProfile ?? (await upsertRetirementProfile(getToken, retirementProfile));
      setSavedProfile(profile);
      const result = await createAnalysis(getToken, {
        portfolio_snapshot_id: selectedPortfolioId,
        retirement_profile_id: profile.id
      });
      setReport(result);
    } catch (runError) {
      setError(runError instanceof Error ? runError.message : "Unable to run analysis");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthGuard>
      <div className="grid">
        <section className="panel">
          <h1>Run Analysis</h1>
          <p>
            Choose a saved portfolio, add a few retirement assumptions, and generate a report that
            explains concentration, diversification, and retirement progress.
          </p>
          <div className="notice">
            The retirement profile helps Alex estimate whether current savings and monthly
            contributions are on track for the lifestyle the user wants in retirement.
          </div>
          {error ? <p className="danger">{error}</p> : null}
        </section>
        <section className="grid two">
          <div className="panel">
            <h2>Portfolio selection</h2>
            <p className="muted">
              Pick the saved portfolio you want Alex to review.
            </p>
            <label>
              Saved portfolio
              <select
                value={selectedPortfolioId}
                onChange={(event) => setSelectedPortfolioId(event.target.value)}
              >
                <option value="">Select a portfolio</option>
                {portfolios.map((portfolio) => (
                  <option key={portfolio.id} value={portfolio.id}>
                    {portfolio.name}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="panel">
            <h2>Retirement profile</h2>
            <p className="muted">
              These numbers are used to estimate a retirement target and compare it with projected
              future savings.
            </p>
            <form
              onSubmit={(event) => {
                event.preventDefault();
                void saveProfile();
              }}
            >
              <div className="inline-grid">
                <label>
                  Current age
                  <input
                    type="number"
                    placeholder="35"
                    value={retirementProfile.current_age}
                    onChange={(event) =>
                      setRetirementProfile((current) => ({
                        ...current,
                        current_age: Number(event.target.value)
                      }))
                    }
                  />
                </label>
                <label>
                  Target retirement age
                  <input
                    type="number"
                    placeholder="65"
                    value={retirementProfile.target_retirement_age}
                    onChange={(event) =>
                      setRetirementProfile((current) => ({
                        ...current,
                        target_retirement_age: Number(event.target.value)
                      }))
                    }
                  />
                </label>
              </div>
              <div className="inline-grid">
                <label>
                  Current retirement savings
                  <input
                    type="number"
                    placeholder="100000"
                    value={retirementProfile.current_retirement_savings}
                    onChange={(event) =>
                      setRetirementProfile((current) => ({
                        ...current,
                        current_retirement_savings: Number(event.target.value)
                      }))
                    }
                  />
                </label>
                <label>
                  Monthly contribution
                  <input
                    type="number"
                    placeholder="1000"
                    value={retirementProfile.monthly_contribution}
                    onChange={(event) =>
                      setRetirementProfile((current) => ({
                        ...current,
                        monthly_contribution: Number(event.target.value)
                      }))
                    }
                  />
                </label>
              </div>
              <div className="inline-grid">
                <label>
                  Yearly spending goal in retirement
                  <input
                    type="number"
                    placeholder="60000"
                    value={retirementProfile.target_annual_retirement_spend}
                    onChange={(event) =>
                      setRetirementProfile((current) => ({
                        ...current,
                        target_annual_retirement_spend: Number(event.target.value)
                      }))
                    }
                  />
                </label>
                <label>
                  Risk profile
                  <select
                    value={retirementProfile.risk_profile}
                    onChange={(event) =>
                      setRetirementProfile((current) => ({
                        ...current,
                        risk_profile: event.target.value as "conservative" | "moderate" | "growth"
                      }))
                    }
                  >
                    <option value="conservative">Conservative</option>
                    <option value="moderate">Moderate</option>
                    <option value="growth">Growth</option>
                  </select>
                </label>
              </div>
              <div className="nav-links">
                <button type="submit" className="secondary" disabled={loading}>
                  Save assumptions
                </button>
                <button
                  type="button"
                  disabled={loading}
                  onClick={() => {
                    void runAnalysis();
                  }}
                >
                  Generate report
                </button>
              </div>
            </form>
          </div>
        </section>
        <ReportView report={report} />
      </div>
    </AuthGuard>
  );
}
