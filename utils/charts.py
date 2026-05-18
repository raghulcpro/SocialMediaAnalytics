"""
===============================================================================
 CHART FACTORY
 ─────────────
 Generates all Plotly charts with Binance-inspired dark theme styling.
 Consistent visual language across: donut, line, area, radar, heatmap, etc.
===============================================================================
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ── Binance Theme Colors ─────────────────────────────────────────────────
COLORS = {
    "bg": "#0B0E11",
    "card": "#1E2329",
    "border": "#2B3139",
    "yellow": "#FCD535",
    "green": "#0ECB81",
    "red": "#F6465D",
    "blue": "#1E90FF",
    "purple": "#A855F7",
    "cyan": "#22D3EE",
    "orange": "#F59E0B",
    "text": "#EAECEF",
    "text_dim": "#848E9C",
}

PALETTE = [COLORS["yellow"], COLORS["green"], COLORS["red"],
           COLORS["blue"], COLORS["purple"], COLORS["cyan"], COLORS["orange"]]

LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=COLORS["text"], size=13),
    margin=dict(l=40, r=40, t=60, b=40),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=COLORS["text_dim"])),
)


def _apply_layout(fig, title="", height=420):
    """Apply consistent Binance-style layout to any figure."""
    fig.update_layout(**LAYOUT_DEFAULTS, title=dict(text=title, font=dict(size=18, color=COLORS["yellow"])), height=height)
    fig.update_xaxes(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"])
    fig.update_yaxes(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"])
    return fig


def donut_chart(labels, values, title=""):
    """Sentiment / category distribution donut chart."""
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.65,
        marker=dict(colors=PALETTE[:len(labels)], line=dict(color=COLORS["bg"], width=2)),
        textfont=dict(color="white", size=13),
        hoverinfo="label+percent+value",
    ))
    return _apply_layout(fig, title)


def line_chart(df, x, y, title="", color=None):
    """Engagement / trend line chart."""
    fig = px.line(df, x=x, y=y, color=color, color_discrete_sequence=PALETTE, markers=True)
    fig.update_traces(line=dict(width=2.5))
    return _apply_layout(fig, title)


def area_chart(df, x, y, title=""):
    """Filled area chart for cumulative metrics."""
    fig = px.area(df, x=x, y=y, color_discrete_sequence=[COLORS["yellow"]])
    fig.update_traces(fillcolor="rgba(252,213,53,0.15)", line=dict(color=COLORS["yellow"], width=2))
    return _apply_layout(fig, title)


def bar_chart(df, x, y, title="", color=None, horizontal=False):
    """Engagement / comparison bar chart."""
    if horizontal:
        fig = px.bar(df, x=y, y=x, color=color, orientation="h", color_discrete_sequence=PALETTE)
    else:
        fig = px.bar(df, x=x, y=y, color=color, color_discrete_sequence=PALETTE)
    fig.update_traces(marker_line_width=0, opacity=0.9)
    return _apply_layout(fig, title)


def radar_chart(categories, values, title=""):
    """Influencer score / profile radar chart."""
    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]], theta=categories + [categories[0]],
        fill="toself", fillcolor="rgba(252,213,53,0.15)",
        line=dict(color=COLORS["yellow"], width=2),
        marker=dict(size=8, color=COLORS["yellow"]),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, gridcolor=COLORS["border"], color=COLORS["text_dim"]),
            angularaxis=dict(gridcolor=COLORS["border"], color=COLORS["text"]),
        ),
    )
    return _apply_layout(fig, title, height=450)


def heatmap_chart(data, x_labels, y_labels, title=""):
    """Engagement heatmap (e.g., day-of-week × metric)."""
    fig = go.Figure(go.Heatmap(
        z=data, x=x_labels, y=y_labels,
        colorscale=[[0, COLORS["bg"]], [0.5, COLORS["yellow"]], [1, COLORS["green"]]],
        hoverongaps=False,
    ))
    return _apply_layout(fig, title, height=380)


def scatter_chart(df, x, y, size=None, color=None, title=""):
    """Scatter / bubble chart."""
    fig = px.scatter(df, x=x, y=y, size=size, color=color,
                     color_discrete_sequence=PALETTE, size_max=25)
    return _apply_layout(fig, title)


def comparison_bar(labels, values1, values2, name1="Profile A", name2="Profile B", title=""):
    """Side-by-side comparison bar chart."""
    fig = go.Figure()
    fig.add_trace(go.Bar(name=name1, x=labels, y=values1,
                         marker_color=COLORS["yellow"], opacity=0.9))
    fig.add_trace(go.Bar(name=name2, x=labels, y=values2,
                         marker_color=COLORS["cyan"], opacity=0.9))
    fig.update_layout(barmode="group")
    return _apply_layout(fig, title)


def gauge_chart(value, title="", max_val=100):
    """Gauge / speedometer chart for scores."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title=dict(text=title, font=dict(size=16, color=COLORS["text"])),
        number=dict(font=dict(size=36, color=COLORS["yellow"])),
        gauge=dict(
            axis=dict(range=[0, max_val], tickcolor=COLORS["text_dim"]),
            bar=dict(color=COLORS["yellow"]),
            bgcolor=COLORS["card"],
            borderwidth=0,
            steps=[
                dict(range=[0, max_val * 0.3], color=COLORS["red"]),
                dict(range=[max_val * 0.3, max_val * 0.7], color=COLORS["border"]),
                dict(range=[max_val * 0.7, max_val], color="rgba(14,203,129,0.3)"),
            ],
        )
    ))
    return _apply_layout(fig, height=300)
