import { AnalysisReport, AnalysisSummary, Portfolio, PortfolioListItem, RetirementProfile } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type TokenGetter = () => Promise<string | null>;

async function request<T>(path: string, getToken: TokenGetter, init?: RequestInit): Promise<T> {
  const token = await getToken();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      ...(init?.headers ?? {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  });

  if (!response.ok) {
    const payload = await response.text();
    throw new Error(payload || "Request failed");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function getCurrentUser(getToken: TokenGetter) {
  return request<{ id: string; email?: string | null; full_name?: string | null }>("/api/v1/me", getToken);
}

export async function listPortfolios(getToken: TokenGetter) {
  return request<PortfolioListItem[]>("/api/v1/portfolios", getToken);
}

export async function getPortfolio(getToken: TokenGetter, id: string) {
  return request<Portfolio>(`/api/v1/portfolios/${id}`, getToken);
}

export async function createManualPortfolio(
  getToken: TokenGetter,
  payload: {
    name: string;
    currency: string;
    notes?: string;
    holdings: Array<{ ticker: string; quantity: number; average_cost_basis?: number | null }>;
  }
) {
  return request<Portfolio>("/api/v1/portfolios/manual", getToken, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

export async function uploadCsvPortfolio(
  getToken: TokenGetter,
  payload: {
    name: string;
    currency: string;
    notes?: string;
    file: File;
  }
) {
  const formData = new FormData();
  formData.set("name", payload.name);
  formData.set("currency", payload.currency);
  if (payload.notes) {
    formData.set("notes", payload.notes);
  }
  formData.set("file", payload.file);

  return request<Portfolio>("/api/v1/portfolios/upload-csv", getToken, {
    method: "POST",
    body: formData
  });
}

export async function upsertRetirementProfile(
  getToken: TokenGetter,
  payload: {
    current_age: number;
    target_retirement_age: number;
    current_retirement_savings: number;
    monthly_contribution: number;
    target_annual_retirement_spend: number;
    risk_profile: "conservative" | "moderate" | "growth";
    expected_retirement_years?: number;
  }
) {
  return request<RetirementProfile>("/api/v1/retirement-profile", getToken, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

export async function getRetirementProfile(getToken: TokenGetter) {
  return request<RetirementProfile | null>("/api/v1/retirement-profile", getToken);
}

export async function createAnalysis(
  getToken: TokenGetter,
  payload: { portfolio_snapshot_id: string; retirement_profile_id?: string | null }
) {
  return request<AnalysisReport>("/api/v1/analysis", getToken, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

export async function listAnalysis(getToken: TokenGetter) {
  return request<AnalysisSummary[]>("/api/v1/analysis", getToken);
}

export async function getAnalysis(getToken: TokenGetter, id: string) {
  return request<AnalysisReport>(`/api/v1/analysis/${id}`, getToken);
}

export async function deleteAnalysis(getToken: TokenGetter, id: string) {
  return request<void>(`/api/v1/analysis/${id}`, getToken, {
    method: "DELETE"
  });
}
