import { AnalysisReport } from "@/lib/types";

type ParsedSection = {
  title: string;
  paragraphs: string[];
  bullets: string[];
};

const SECTION_ORDER = [
  "Portfolio Summary",
  "Diversification Findings",
  "Retirement Outlook",
  "Recommended Next Steps",
  "Risks and Assumptions",
  "Disclaimer"
];

const METRIC_LABELS: Record<string, string> = {
  portfolio_score: "Portfolio score",
  diversification_score: "Diversification score",
  retirement_readiness_score: "Retirement readiness",
  total_positions: "Positions",
  top_holding_weight: "Top holding",
  top_three_weight: "Top 3 holdings",
  largest_sector_weight: "Largest sector",
  projected_retirement_value: "Projected value",
  target_retirement_corpus: "Target corpus",
  readiness_band: "Readiness"
};

function toTitleCase(value: string): string {
  return value
    .replaceAll("_", " ")
    .split(" ")
    .filter(Boolean)
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(" ");
}

function humanizeMetric(key: string, value: string): string {
  if (key === "readiness_band") {
    return toTitleCase(value);
  }
  if (key.includes("weight")) {
    return `${value}%`;
  }
  return value;
}

function cleanSentence(line: string): string {
  return line
    .replace(/^The user is\s+/i, "The investor is ")
    .replace(/"([a-z_]+)"/gi, (_, word: string) => toTitleCase(word).toLowerCase())
    .replace(/\b([a-z]+_[a-z_]+)\b/gi, (word: string) => word.toLowerCase() === word ? toTitleCase(word).toLowerCase() : word)
    .replace(/\bUser ID\s+`[^`]+`\s*/i, "")
    .trim();
}

function parseReport(markdown: string): ParsedSection[] {
  const lines = markdown
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  const sections: ParsedSection[] = [];
  let current: ParsedSection | null = null;

  for (const line of lines) {
    if (line.startsWith("# ")) {
      continue;
    }

    if (line.startsWith("## ")) {
      if (current) {
        sections.push(current);
      }
      current = {
        title: line.slice(3).trim(),
        paragraphs: [],
        bullets: []
      };
      continue;
    }

    if (!current) {
      continue;
    }

    if (line.startsWith("*")) {
      current.bullets.push(cleanSentence(line.replace(/^\*\s*/, "")));
      continue;
    }

    current.paragraphs.push(cleanSentence(line));
  }

  if (current) {
    sections.push(current);
  }

  return sections.sort((a, b) => {
    const aIndex = SECTION_ORDER.indexOf(a.title);
    const bIndex = SECTION_ORDER.indexOf(b.title);
    return (aIndex === -1 ? 99 : aIndex) - (bIndex === -1 ? 99 : bIndex);
  });
}

function formatReportDate(value: string): string {
  return new Date(value).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit"
  });
}

export function ReportView({ report }: { report: AnalysisReport | null }) {
  if (!report) {
    return (
      <div className="panel">
        <h3>No report selected</h3>
        <p className="muted">Run an analysis or open a saved report.</p>
      </div>
    );
  }

  const sections = parseReport(report.summary_markdown);
  const visibleMetrics = Object.entries(report.metrics).filter(([key]) => key !== "portfolio_score");

  return (
    <div className="grid">
      <section className="panel">
        <p className="eyebrow">Analysis Report</p>
        <h2>{formatReportDate(report.created_at)}</h2>
        <div className="metric-grid">
          <div className="metric">
            <strong>{report.portfolio_score ?? "N/A"}</strong>
            <span>Portfolio score</span>
          </div>
          <div className="metric">
            <strong>{report.diversification_score ?? "N/A"}</strong>
            <span>Diversification</span>
          </div>
          <div className="metric">
            <strong>{report.retirement_readiness_score ?? "N/A"}</strong>
            <span>Retirement readiness</span>
          </div>
        </div>
      </section>

      <section className="panel">
        <h2>Summary</h2>
        <div className="markdown">
          {sections.map((section) => (
            <div key={section.title} className="markdown-section">
              <h3>{section.title}</h3>
              {section.paragraphs.map((paragraph) => (
                <p key={paragraph}>{paragraph}</p>
              ))}
              {section.bullets.length ? (
                <ul>
                  {section.bullets.map((bullet) => (
                    <li key={bullet}>{bullet}</li>
                  ))}
                </ul>
              ) : null}
            </div>
          ))}
        </div>
      </section>

      <section className="panel">
        <h2>Key Metrics</h2>
        <div className="metric-grid">
          {visibleMetrics.map(([key, value]) => (
            <div key={key} className="metric">
              <strong>{humanizeMetric(key, value)}</strong>
              <span>{METRIC_LABELS[key] ?? toTitleCase(key)}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="panel">
        <h2>Disclaimer</h2>
        <p className="muted">{cleanSentence(report.disclaimer_text)}</p>
      </section>
    </div>
  );
}
