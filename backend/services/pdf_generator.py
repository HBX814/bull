"""Generate a Geojit-style research report PDF from structured data."""
from __future__ import annotations

import io
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether,
)

from .charts import (
    chart_revenue, chart_ebitda, chart_pat, chart_segment, chart_price_performance,
)

# --- Brand palette --------------------------------------------------------
BRAND_NAVY = colors.HexColor("#0B2545")
BRAND_BLUE = colors.HexColor("#1F4E79")
BRAND_GOLD = colors.HexColor("#C9A227")
LIGHT_BG = colors.HexColor("#F2F4F7")
TABLE_HEAD = colors.HexColor("#1F4E79")
TABLE_HEAD_TEXT = colors.white
TABLE_ALT = colors.HexColor("#EAF0F7")
TEXT_DARK = colors.HexColor("#1F1F1F")
TEXT_MUTED = colors.HexColor("#555555")
ACCENT_GREEN = colors.HexColor("#1B7F3A")
ACCENT_RED = colors.HexColor("#B00020")

styles = getSampleStyleSheet()


def _style(name: str, **kwargs) -> ParagraphStyle:
    base = ParagraphStyle(name, parent=styles["Normal"])
    for k, v in kwargs.items():
        setattr(base, k, v)
    return base


S_TITLE = _style("Title", fontName="Helvetica-Bold", fontSize=16, textColor=BRAND_NAVY, leading=18)
S_SUBTITLE = _style("Subtitle", fontName="Helvetica-Bold", fontSize=12, textColor=BRAND_BLUE, leading=14)
S_H = _style("H", fontName="Helvetica-Bold", fontSize=10, textColor=BRAND_NAVY, leading=12, spaceAfter=4)
S_BODY = _style("Body", fontName="Helvetica", fontSize=8.5, textColor=TEXT_DARK, leading=11, alignment=TA_JUSTIFY)
S_BULLET = _style("Bullet", fontName="Helvetica", fontSize=8.5, textColor=TEXT_DARK, leading=11, leftIndent=10, bulletIndent=0)
S_MUTED = _style("Muted", fontName="Helvetica", fontSize=7.5, textColor=TEXT_MUTED, leading=9)
S_HEADLINE = _style("Headline", fontName="Helvetica-Bold", fontSize=12, textColor=BRAND_NAVY, leading=14, spaceAfter=4)
S_RATING = _style("Rating", fontName="Helvetica-Bold", fontSize=20, textColor=BRAND_GOLD, leading=22, alignment=TA_RIGHT)
S_TINY = _style("Tiny", fontName="Helvetica", fontSize=7, textColor=TEXT_MUTED, leading=8.5)


# ---------- helpers ------------------------------------------------------

def _draw_header(canvas, doc, company_name: str, report_title: str):
    canvas.saveState()
    w, h = A4
    # top color bar
    canvas.setFillColor(BRAND_NAVY)
    canvas.rect(0, h - 18 * mm, w, 18 * mm, fill=1, stroke=0)
    # gold underline accent
    canvas.setFillColor(BRAND_GOLD)
    canvas.rect(0, h - 19 * mm, w, 1 * mm, fill=1, stroke=0)
    # left: report kind
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(15 * mm, h - 8 * mm, "RETAIL EQUITY RESEARCH")
    canvas.setFont("Helvetica", 8)
    canvas.drawString(15 * mm, h - 13 * mm, company_name.upper())
    # right: logo word-mark
    canvas.setFont("Helvetica-Bold", 16)
    canvas.setFillColor(colors.white)
    canvas.drawRightString(w - 15 * mm, h - 9 * mm, "BULL-AI")
    canvas.setFont("Helvetica", 6.5)
    canvas.setFillColor(BRAND_GOLD)
    canvas.drawRightString(w - 15 * mm, h - 13.5 * mm, "RESEARCH \u2022 GENERATED INSTANTLY")
    # right tab with report title
    if report_title:
        canvas.setFillColor(BRAND_GOLD)
        canvas.rect(w - 60 * mm, h - 18 * mm, 60 * mm, 5 * mm, fill=1, stroke=0)
        canvas.setFillColor(BRAND_NAVY)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawRightString(w - 16 * mm, h - 16.5 * mm, report_title.upper())

    # footer
    canvas.setFillColor(BRAND_NAVY)
    canvas.rect(0, 0, w, 8 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(15 * mm, 3 * mm, "Bull-AI Research  |  Auto-generated equity report")
    canvas.drawRightString(w - 15 * mm, 3 * mm, f"Page {doc.page}")
    canvas.restoreState()


def _make_table(data: List[List[Any]], col_widths: Optional[List[float]] = None,
                header_row: bool = True, font_size: float = 7.5,
                align_first_left: bool = True) -> Table:
    t = Table(data, colWidths=col_widths, hAlign="LEFT")
    cmds = [
        ("FONT", (0, 0), (-1, -1), "Helvetica", font_size),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TEXTCOLOR", (0, 0), (-1, -1), TEXT_DARK),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#CCCCCC")),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    if header_row:
        cmds += [
            ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEAD),
            ("TEXTCOLOR", (0, 0), (-1, 0), TABLE_HEAD_TEXT),
            ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", font_size),
        ]
        # zebra
        for i in range(1, len(data)):
            if i % 2 == 0:
                cmds.append(("BACKGROUND", (0, i), (-1, i), TABLE_ALT))
    if align_first_left:
        cmds.append(("ALIGN", (1, 0), (-1, -1), "RIGHT"))
        cmds.append(("ALIGN", (0, 0), (0, -1), "LEFT"))
    t.setStyle(TableStyle(cmds))
    return t


def _kv_table(items: List[tuple], width: float) -> Table:
    rows = [[Paragraph(f"<b>{k}</b>", S_BODY), Paragraph(str(v) if v else "-", S_BODY)] for k, v in items]
    t = Table(rows, colWidths=[width * 0.55, width * 0.45])
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Helvetica", 7.5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#CCCCCC")),
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_BG),
        ("TEXTCOLOR", (0, 0), (-1, -1), TEXT_DARK),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
    ]))
    return t


def _png_image(png: Optional[bytes], width_mm: float, height_mm: float) -> Optional[Image]:
    if not png:
        return None
    return Image(io.BytesIO(png), width=width_mm * mm, height=height_mm * mm)


def _para(text: str, style=S_BODY) -> Paragraph:
    if text is None:
        text = ""
    return Paragraph(str(text).replace("\n", "<br/>"), style)


def _safe(v: Any, default: str = "-") -> str:
    if v is None or v == "" or v == "null":
        return default
    return str(v)


# ---------- main builder -------------------------------------------------

def build_pdf(data: Dict[str, Any]) -> bytes:
    company = data.get("company_name") or "Company"
    report_title = data.get("report_title") or "Result Update"

    buf = io.BytesIO()
    doc = BaseDocTemplate(
        buf, pagesize=A4,
        leftMargin=12 * mm, rightMargin=12 * mm,
        topMargin=24 * mm, bottomMargin=12 * mm,
        title=f"{company} - Bull-AI Research",
        author="Bull-AI Research",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin,
                  doc.width, doc.height, id="full", showBoundary=0)
    template = PageTemplate(
        id="main", frames=[frame],
        onPage=lambda c, d: _draw_header(c, d, company, report_title),
    )
    doc.addPageTemplates([template])

    story: List[Any] = []
    story += _page1(data, doc.width)
    story.append(PageBreak())
    story += _page2(data, doc.width)
    story.append(PageBreak())
    story += _page3(data, doc.width)
    story.append(PageBreak())
    story += _page4(data, doc.width)

    doc.build(story)
    return buf.getvalue()


# ---------- page 1 -------------------------------------------------------

def _page1(d: Dict[str, Any], width: float) -> List[Any]:
    company = d.get("company_name") or "Company"
    sector = d.get("sector") or ""
    headline = d.get("headline") or "AI-generated equity research"
    rating = d.get("rating") or "-"
    target = d.get("target_price") or "-"
    cmp = d.get("cmp") or "-"
    date = d.get("report_date") or ""

    story: List[Any] = []
    # title row
    story.append(_para(f"<b>{company}</b>", S_TITLE))
    if sector:
        story.append(_para(f"<font color='#555555'>{sector}</font>", S_MUTED))
    story.append(Spacer(1, 4))

    # rating strip
    rating_row = Table([[
        Paragraph(f"<b>Rating</b><br/><font size=12 color='#0B2545'><b>{rating}</b></font>", S_BODY),
        Paragraph(f"<b>Target</b><br/><font size=12 color='#0B2545'><b>{target}</b></font>", S_BODY),
        Paragraph(f"<b>CMP</b><br/><font size=12 color='#0B2545'><b>{cmp}</b></font>", S_BODY),
        Paragraph(f"<b>Date</b><br/><font size=10 color='#0B2545'>{date}</font>", S_BODY),
        Paragraph(f"<b>Bloomberg</b><br/><font size=9 color='#0B2545'>{_safe(d.get('bloomberg_code'))}</font>", S_BODY),
    ]], colWidths=[width * 0.2] * 5)
    rating_row.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, BRAND_NAVY),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#BBBBBB")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(rating_row)
    story.append(Spacer(1, 8))

    # two-column layout: left = company data, right = headline + narrative
    left_col_w = width * 0.36
    right_col_w = width * 0.62

    # LEFT: Company data, shareholding, price perf, mini-chart
    left_blocks: List[Any] = []
    left_blocks.append(_para("Company Data", S_H))
    cd = d.get("company_data") or {}
    left_blocks.append(_kv_table(list(cd.items()), left_col_w))
    left_blocks.append(Spacer(1, 6))

    # Shareholding
    sh = d.get("shareholding") or []
    if sh:
        left_blocks.append(_para("Shareholding (%)", S_H))
        keys = ["period", "Promoters", "FIIs", "MFs/Inst", "Public", "Others"]
        head = ["Period", "Prom.", "FIIs", "MFs", "Pub.", "Oth."]
        rows = [head] + [[_safe(r.get(k)) for k in keys] for r in sh]
        left_blocks.append(_make_table(rows, col_widths=[left_col_w / 6] * 6, font_size=6.8))
        left_blocks.append(Spacer(1, 6))

    # Price perf
    pp = d.get("price_performance") or []
    if pp:
        left_blocks.append(_para("Price Performance", S_H))
        head = ["Period", "Abs.%", "Sensex%", "Rel.%"]
        rows = [head] + [[_safe(r.get("period")), _safe(r.get("absolute_return")),
                          _safe(r.get("sensex_return")), _safe(r.get("relative_return"))] for r in pp]
        left_blocks.append(_make_table(rows, col_widths=[left_col_w / 4] * 4, font_size=6.8))
        left_blocks.append(Spacer(1, 6))
        img = _png_image(chart_price_performance(pp), left_col_w / mm, 30)
        if img:
            left_blocks.append(img)

    # RIGHT: headline + key highlights + outlook + quarterly financials
    right_blocks: List[Any] = []
    right_blocks.append(_para(headline, S_HEADLINE))
    right_blocks.append(Spacer(1, 2))
    highlights = d.get("key_highlights") or []
    for h in highlights[:5]:
        right_blocks.append(_para(f"\u2022 {h}", S_BULLET))
    right_blocks.append(Spacer(1, 6))
    outlook = d.get("outlook_valuation") or ""
    if outlook:
        right_blocks.append(_para("Outlook & Valuation", S_H))
        right_blocks.append(_para(outlook, S_BODY))
        right_blocks.append(Spacer(1, 6))

    # Quarterly financials table
    qf = d.get("quarterly_financials") or []
    if qf:
        right_blocks.append(_para("Quarterly Financials (Consolidated)", S_H))
        cur_lbl = d.get("current_quarter_label") or "Curr Q"
        yoy_lbl = d.get("yoy_quarter_label") or "YoY Q"
        prev_lbl = d.get("prev_quarter_label") or "Prev Q"
        head = ["Rs.cr", cur_lbl, yoy_lbl, "YoY %", prev_lbl, "QoQ %"]
        rows = [head]
        for r in qf:
            rows.append([
                _safe(r.get("metric")),
                _safe(r.get("current_q")),
                _safe(r.get("yoy_q")),
                _safe(r.get("yoy_growth")),
                _safe(r.get("prev_q")),
                _safe(r.get("qoq_growth")),
            ])
        right_blocks.append(_make_table(rows, col_widths=[right_col_w * 0.28] + [right_col_w * 0.144] * 5, font_size=7))

    # Combine columns
    layout = Table([[left_blocks, right_blocks]], colWidths=[left_col_w, right_col_w])
    layout.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 6),
        ("LEFTPADDING", (1, 0), (1, 0), 6),
    ]))
    story.append(layout)
    return story


# ---------- page 2 -------------------------------------------------------

def _page2(d: Dict[str, Any], width: float) -> List[Any]:
    story: List[Any] = []
    story.append(_para("Key Highlights", S_SUBTITLE))
    story.append(Spacer(1, 4))
    for h in (d.get("key_highlights") or []):
        story.append(_para(f"\u2022 {h}", S_BULLET))
    story.append(Spacer(1, 10))

    # 4 charts in 2x2 grid
    half = width / 2 - 4
    rev = _png_image(chart_revenue(d.get("revenue_trend") or []), half / mm, 50)
    seg_label = d.get("segment_label") or "Segment / GOV"
    seg = _png_image(chart_segment(d.get("segment_or_gov_trend") or [], seg_label), half / mm, 50)
    ebt = _png_image(chart_ebitda(d.get("ebitda_trend") or []), half / mm, 50)
    pat = _png_image(chart_pat(d.get("pat_trend") or []), half / mm, 50)

    placeholder = _para("<i>Chart unavailable - insufficient data extracted.</i>", S_MUTED)
    grid = Table([
        [rev or placeholder, seg or placeholder],
        [ebt or placeholder, pat or placeholder],
    ], colWidths=[half, half])
    grid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(grid)
    story.append(Spacer(1, 10))

    # Change in Estimates
    ce = d.get("change_in_estimates") or []
    if ce:
        story.append(_para("Change in Estimates", S_H))
        head = ["Metric", "Old FY1", "Old FY2", "New FY1", "New FY2", "Chg FY1 %", "Chg FY2 %"]
        rows = [head]
        for r in ce:
            rows.append([
                _safe(r.get("metric")), _safe(r.get("old_fy1")), _safe(r.get("old_fy2")),
                _safe(r.get("new_fy1")), _safe(r.get("new_fy2")),
                _safe(r.get("chg_fy1")), _safe(r.get("chg_fy2")),
            ])
        story.append(_make_table(rows, col_widths=[width * 0.22] + [width * 0.13] * 6, font_size=7.5))

    return story


# ---------- page 3 -------------------------------------------------------

def _annual_table(title: str, rows_data: List[Dict[str, Any]], year_cols: List[str], width: float) -> List[Any]:
    blocks: List[Any] = [_para(title, S_H)]
    if not rows_data:
        blocks.append(_para("Data not available.", S_MUTED))
        return blocks
    head = ["Y.E March (Rs.Cr)"] + year_cols
    rows = [head]
    for r in rows_data:
        row = [_safe(r.get("metric"))]
        for yc in year_cols:
            row.append(_safe(r.get(yc)))
        rows.append(row)
    n = len(year_cols) + 1
    col_widths = [width * 0.34] + [(width * 0.66) / len(year_cols)] * len(year_cols)
    blocks.append(_make_table(rows, col_widths=col_widths, font_size=7))
    return blocks


def _page3(d: Dict[str, Any], width: float) -> List[Any]:
    story: List[Any] = []
    story.append(_para("Consolidated Financials", S_SUBTITLE))
    story.append(Spacer(1, 6))
    year_cols = d.get("year_columns") or ["FY23A", "FY24A", "FY25A", "FY26E", "FY27E"]

    half = width / 2 - 4
    pnl_blocks = _annual_table("Profit & Loss", d.get("profit_loss") or [], year_cols, half)
    bs_blocks = _annual_table("Balance Sheet", d.get("balance_sheet") or [], year_cols, half)
    cf_blocks = _annual_table("Cash Flow", d.get("cashflow") or [], year_cols, half)
    rat_blocks = _annual_table("Ratios", d.get("ratios") or [], year_cols, half)

    grid = Table([[pnl_blocks, bs_blocks], [cf_blocks, rat_blocks]], colWidths=[half, half])
    grid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(grid)
    return story


# ---------- page 4 -------------------------------------------------------

def _page4(d: Dict[str, Any], width: float) -> List[Any]:
    story: List[Any] = []
    story.append(_para("Investment Rating Criteria", S_SUBTITLE))
    story.append(Spacer(1, 4))
    crit = [
        ["Rating", "Large Caps", "Mid Caps", "Small Caps"],
        ["BUY", "> 10%", "> 15%", "> 20%"],
        ["ACCUMULATE", "5%-10%", "10%-15%", "10%-20%"],
        ["HOLD", "(-5%)-5%", "(-10%)-10%", "(-10%)-10%"],
        ["REDUCE", "(-10%)-(-5%)", "(-15%)-(-10%)", "(-20%)-(-10%)"],
        ["SELL", "< -10%", "< -15%", "< -20%"],
    ]
    story.append(_make_table(crit, col_widths=[width * 0.25] * 4, font_size=8))
    story.append(Spacer(1, 10))

    story.append(_para("About this Report", S_H))
    story.append(_para(
        "This research note has been auto-generated by Bull-AI Research using publicly available "
        "filings, presentations and management commentary uploaded by the user. Numbers were "
        "extracted by a large language model and assembled into the Geojit-style template. While "
        "we apply prompt-engineering best-practices to minimise hallucination, all figures must be "
        "independently verified against original source documents before any investment decision.",
        S_BODY,
    ))
    story.append(Spacer(1, 8))
    story.append(_para("Standard Warning", S_H))
    story.append(_para(
        "Investments in securities markets are subject to market risks. Read all the related documents carefully before investing. "
        "Past performance is not indicative of future results. The information contained herein is for informational purposes only "
        "and does not constitute investment advice, an offer to buy or sell, or a solicitation of an offer to buy or sell any security.",
        S_BODY,
    ))
    story.append(Spacer(1, 10))
    story.append(_para("Disclaimer & Disclosures", S_H))
    story.append(_para(
        "Bull-AI Research is an automated AI-driven research tool. The report has been generated using uploaded documents and a "
        "language model and should be cross-checked with the company's official filings. Bull-AI Research, its affiliates, and the "
        "authors of this tool do not accept any liability for any loss arising from the use of this report. Analyst certification "
        "is implicit in the automated nature of the system; no analyst has manually approved the contents.",
        S_BODY,
    ))
    story.append(Spacer(1, 6))
    story.append(_para("Disclosure regarding Artificial Intelligence tools: This report was assembled using a generative AI model. "
                       "Outputs may contain errors, omissions, or hallucinations. Use at your own discretion.", S_TINY))
    return story
