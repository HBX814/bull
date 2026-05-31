"""Generate financial charts as PNG bytes using matplotlib."""
from __future__ import annotations

import io
from typing import List, Dict, Any, Optional, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Geojit-ish palette
BAR_COLOR = "#1F4E79"        # deep blue bars
LINE_COLOR = "#E69500"       # orange overlay line
NEG_LINE_COLOR = "#C00000"
GRID_COLOR = "#D9D9D9"
TEXT_COLOR = "#1F1F1F"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "axes.edgecolor": "#888888",
    "axes.labelcolor": TEXT_COLOR,
    "xtick.color": TEXT_COLOR,
    "ytick.color": TEXT_COLOR,
})


def _safe_float(v: Any) -> Optional[float]:
    try:
        if v is None or v == "":
            return None
        return float(v)
    except (TypeError, ValueError):
        return None


def _bar_with_line(
    title: str,
    periods: List[str],
    bar_values: List[Optional[float]],
    line_values: List[Optional[float]],
    bar_label: str,
    line_label: str,
    line_is_percent: bool = True,
) -> bytes:
    fig, ax = plt.subplots(figsize=(4.4, 2.6), dpi=140)
    fig.patch.set_facecolor("white")

    bar_vals = [v if v is not None else 0 for v in bar_values]
    bars = ax.bar(periods, bar_vals, color=BAR_COLOR, width=0.55, label=bar_label, zorder=2)
    ax.set_ylabel(bar_label, fontsize=8)
    ax.tick_params(axis="x", rotation=0, labelsize=7)
    ax.grid(axis="y", linestyle="--", linewidth=0.5, color=GRID_COLOR, zorder=1)
    ax.set_axisbelow(True)
    # bar value labels
    for bar, v in zip(bars, bar_values):
        if v is not None:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    f"{v:,.0f}", ha="center", va="bottom", fontsize=6.5, color=TEXT_COLOR)

    if any(v is not None for v in line_values):
        ax2 = ax.twinx()
        ln_vals = [v if v is not None else 0 for v in line_values]
        ax2.plot(periods, ln_vals, color=LINE_COLOR, marker="o", linewidth=1.6,
                 markersize=4, label=line_label, zorder=3)
        suffix = "%" if line_is_percent else ""
        ax2.set_ylabel(f"{line_label}{(' (%)' if line_is_percent else '')}", fontsize=8)
        for x, y in zip(periods, ln_vals):
            ax2.text(x, y, f"{y:.1f}{suffix}", fontsize=6.5, color=LINE_COLOR,
                     ha="center", va="bottom")
        ax2.tick_params(axis="y", labelsize=7)

    ax.set_title(title, fontsize=10, color=TEXT_COLOR, pad=8, fontweight="bold", loc="left")
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


def chart_revenue(trend: List[Dict[str, Any]]) -> Optional[bytes]:
    if not trend:
        return None
    periods = [str(t.get("period", "")) for t in trend]
    values = [_safe_float(t.get("value")) for t in trend]
    growth = [_safe_float(t.get("growth_qoq")) for t in trend]
    return _bar_with_line("Revenue", periods, values, growth, "Revenue (Rs.cr)", "Growth QoQ")


def chart_ebitda(trend: List[Dict[str, Any]]) -> Optional[bytes]:
    if not trend:
        return None
    periods = [str(t.get("period", "")) for t in trend]
    values = [_safe_float(t.get("value")) for t in trend]
    margin = [_safe_float(t.get("margin")) for t in trend]
    return _bar_with_line("EBITDA", periods, values, margin, "EBITDA (Rs.cr)", "Margin")


def chart_pat(trend: List[Dict[str, Any]]) -> Optional[bytes]:
    if not trend:
        return None
    periods = [str(t.get("period", "")) for t in trend]
    values = [_safe_float(t.get("value")) for t in trend]
    margin = [_safe_float(t.get("margin")) for t in trend]
    return _bar_with_line("PAT", periods, values, margin, "PAT (Rs.cr)", "Margin")


def chart_segment(trend: List[Dict[str, Any]], label: str = "Segment") -> Optional[bytes]:
    if not trend:
        return None
    periods = [str(t.get("period", "")) for t in trend]
    values = [_safe_float(t.get("value")) for t in trend]
    growth = [_safe_float(t.get("growth_qoq")) for t in trend]
    return _bar_with_line(label, periods, values, growth, f"{label} (Rs.cr)", "Growth QoQ")


def chart_price_performance(perf: List[Dict[str, Any]]) -> Optional[bytes]:
    """Small chart showing absolute vs sensex returns."""
    if not perf:
        return None
    periods = [str(p.get("period", "")) for p in perf]
    abs_ret = [_safe_float(p.get("absolute_return")) or 0 for p in perf]
    sensex = [_safe_float(p.get("sensex_return")) or 0 for p in perf]
    fig, ax = plt.subplots(figsize=(3.2, 1.6), dpi=140)
    fig.patch.set_facecolor("white")
    x = range(len(periods))
    width = 0.35
    ax.bar([i - width / 2 for i in x], abs_ret, width=width, color=BAR_COLOR, label="Stock")
    ax.bar([i + width / 2 for i in x], sensex, width=width, color="#8FAADC", label="Sensex")
    ax.set_xticks(list(x))
    ax.set_xticklabels(periods, fontsize=6.5)
    ax.tick_params(axis="y", labelsize=6.5)
    ax.grid(axis="y", linestyle="--", linewidth=0.4, color=GRID_COLOR)
    ax.set_title("Price Performance (%)", fontsize=8, loc="left", fontweight="bold")
    ax.legend(fontsize=6, loc="upper right", frameon=False)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()
