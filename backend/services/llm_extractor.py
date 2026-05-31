"""Use Groq LLM to extract structured financial data from raw text."""
from __future__ import annotations

import json
import os
from typing import Any, Dict

from groq import Groq

GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = """You are a senior equity research analyst at a top brokerage.
Given raw financial documents for a company (earnings result update, presentations, CSVs),
extract a comprehensive structured JSON describing the company for a Geojit-style research
report. Return ONLY valid JSON (no markdown fences). If a value is unknown, use null or an
empty array. Do not fabricate numbers — leave fields blank rather than inventing.
Numbers should be in Indian rupees crore unless the source says otherwise.
"""

USER_TEMPLATE = """Company Name (provided by user): {company}

Documents:
{documents}

Return JSON with this EXACT schema:

{{
  "company_name": str,
  "sector": str|null,
  "report_title": str,                 // e.g. "Q2FY26 Result Update"
  "report_date": str|null,             // e.g. "12th Nov, 2025"
  "rating": str|null,                  // BUY / HOLD / SELL / ACCUMULATE / REDUCE
  "target_price": str|null,            // e.g. "Rs. 540"
  "cmp": str|null,                     // current market price
  "stock_type": str|null,
  "bloomberg_code": str|null,
  "nse_code": str|null,
  "bse_code": str|null,
  "time_frame": str|null,
  "headline": str,                     // one-line thesis
  "company_data": {{                     // small key/value pairs
      "Market Cap (Rs.cr)": str|null,
      "52 Week High/Low (Rs.)": str|null,
      "Enterprise Value (Rs.cr)": str|null,
      "Outstanding Shares (cr)": str|null,
      "Free Float (%)": str|null,
      "Dividend Yield (%)": str|null,
      "6m avg volume (cr)": str|null,
      "Beta": str|null,
      "Face Value (Rs.)": str|null
  }},
  "shareholding": [                    // list of rows
      {{"period": str, "Promoters": str, "FIIs": str, "MFs/Inst": str, "Public": str, "Others": str}}
  ],
  "price_performance": [
      {{"period": str, "absolute_return": str, "sensex_return": str, "relative_return": str}}
  ],
  "key_highlights": [str, ...],         // 4-8 bullet points of key operational/financial highlights
  "outlook_valuation": str,             // 1-2 paragraph outlook + valuation narrative
  "quarterly_financials": [             // recent quarters
      {{"metric": "Sales", "current_q": str, "yoy_q": str, "yoy_growth": str, "prev_q": str, "qoq_growth": str}},
      {{"metric": "EBITDA", "current_q": str, "yoy_q": str, "yoy_growth": str, "prev_q": str, "qoq_growth": str}},
      {{"metric": "EBITDA Margin (%)", ...}},
      {{"metric": "PAT", ...}},
      {{"metric": "Adj EPS (Rs)", ...}}
  ],
  "current_quarter_label": str|null,   // "Q2FY26"
  "yoy_quarter_label": str|null,       // "Q2FY25"
  "prev_quarter_label": str|null,      // "Q1FY26"
  "revenue_trend": [                   // last 5-8 quarters for chart
      {{"period": str, "value": float, "growth_qoq": float|null}}
  ],
  "ebitda_trend": [
      {{"period": str, "value": float, "margin": float|null}}
  ],
  "pat_trend": [
      {{"period": str, "value": float, "margin": float|null}}
  ],
  "segment_or_gov_trend": [            // segment mix OR Gross Order Value
      {{"period": str, "value": float, "growth_qoq": float|null}}
  ],
  "segment_label": str|null,           // header for the 4th chart, e.g. "Gross Order Value" or "Segment Mix"
  "change_in_estimates": [
      {{"metric": "Revenue", "old_fy1": str, "old_fy2": str, "new_fy1": str, "new_fy2": str, "chg_fy1": str, "chg_fy2": str}}
  ],
  "profit_loss": [                     // annual P&L rows, 5 years (FY-2 to FY+2)
      {{"metric": "Sales", "FY23A": str, "FY24A": str, "FY25A": str, "FY26E": str, "FY27E": str}}
  ],
  "balance_sheet": [
      {{"metric": "Cash", "FY23A": str, "FY24A": str, "FY25A": str, "FY26E": str, "FY27E": str}}
  ],
  "cashflow": [
      {{"metric": "CF Operations", "FY23A": str, "FY24A": str, "FY25A": str, "FY26E": str, "FY27E": str}}
  ],
  "ratios": [
      {{"metric": "EBITDA Margin (%)", "FY23A": str, "FY24A": str, "FY25A": str, "FY26E": str, "FY27E": str}}
  ],
  "year_columns": ["FY23A", "FY24A", "FY25A", "FY26E", "FY27E"]  // dynamic year labels actually used
}}

Be thorough. Extract every number you can find. Aim for at least 5 quarters of trend data,
at least 6 highlight bullets, and complete P&L / Balance Sheet / Ratio tables.
"""


def extract_structured(company: str, raw_text: str) -> Dict[str, Any]:
    """Call Groq, return parsed JSON dict."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not configured")

    client = Groq(api_key=api_key)
    prompt = USER_TEMPLATE.format(company=company, documents=raw_text)

    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=3500,
        response_format={"type": "json_object"},
    )
    content = resp.choices[0].message.content or "{}"
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # try to salvage by trimming to outer braces
        start, end = content.find("{"), content.rfind("}")
        data = json.loads(content[start : end + 1]) if start >= 0 < end else {}

    # ensure company name always present
    data.setdefault("company_name", company)
    return data
