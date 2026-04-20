export type PortfolioListItem = {
  id: string;
  name: string;
  source_type: string;
  currency: string;
  created_at: string;
};

export type Holding = {
  id: string;
  ticker: string;
  quantity: number;
  average_cost_basis?: number | null;
  asset_type?: string | null;
  sector?: string | null;
  company_name?: string | null;
};

export type Portfolio = PortfolioListItem & {
  holdings: Holding[];
};

export type RetirementProfile = {
  id: string;
  current_age: number;
  target_retirement_age: number;
  current_retirement_savings: number;
  monthly_contribution: number;
  target_annual_retirement_spend: number;
  risk_profile: "conservative" | "moderate" | "growth";
  expected_retirement_years?: number | null;
  updated_at: string;
};

export type AnalysisSummary = {
  id: string;
  portfolio_snapshot_id: string;
  status: string;
  portfolio_score?: number | null;
  diversification_score?: number | null;
  retirement_readiness_score?: number | null;
  created_at: string;
};

export type AnalysisReport = {
  id: string;
  portfolio_snapshot_id: string;
  retirement_profile_id?: string | null;
  status: string;
  portfolio_score?: number | null;
  diversification_score?: number | null;
  retirement_readiness_score?: number | null;
  summary_markdown: string;
  recommendations_markdown: string;
  disclaimer_text: string;
  model_name: string;
  prompt_version: string;
  metrics: Record<string, string>;
  created_at: string;
};

