"""
Force-directed cascade graph rendered with Plotly.

We previously used pyvis but it has a fragile transitive dependency chain
(jsonpickle / ipython) that breaks on newer Python interpreters in cloud
environments. Plotly is shipped natively in Streamlit and renders a fully
interactive network graph with hover tooltips and zoom/pan, all client-side.
"""

from __future__ import annotations

import math

import networkx as nx
import plotly.graph_objects as go

from data.protocols import EDGES, PROTOCOLS, NODE_TYPES, get_node_color


def _node_size(tvl: float) -> float:
    if tvl <= 0:
        return 14
    return max(16, min(48, 7 * math.log10(tvl)))


def _hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha:.2f})"


def render_cascade_graph(cascade_result: dict, height_px: int = 620) -> go.Figure:
    G = nx.DiGraph()
    for name, meta in PROTOCOLS.items():
        G.add_node(name, type=meta["type"], tvl=meta["tvl_usd"])
    for src, tgt, *_ in EDGES:
        G.add_edge(src, tgt)

    pos = nx.spring_layout(G, k=2.2, iterations=140, seed=42)

    impacts = cascade_result["impacts"]
    epicenter = cascade_result["epicenter"]
    traversed_keys = {(t["source"], t["target"]): t for t in cascade_result["traversed"]}

    # ─── Edges ───────────────────────────────────────────────────────────
    # Render in two passes: dim edges first, hot edges on top.
    dim_x, dim_y = [], []
    hot_traces = []

    for src, tgt, exposure_usd, transmission, mechanism in EDGES:
        x0, y0 = pos[src]
        x1, y1 = pos[tgt]
        traversal = traversed_keys.get((tgt, src))  # cascade flowed target→source

        if traversal:
            width = 1.5 + min(7, traversal["shock_pct"])
            hot_traces.append(go.Scatter(
                x=[x0, x1], y=[y0, y1],
                mode="lines",
                line=dict(color="#FF7B72", width=width),
                hoverinfo="text",
                hovertext=(f"<b>{src} → {tgt}</b><br>"
                           f"Exposure: ${exposure_usd/1e6:.0f}M<br>"
                           f"Transmission: {transmission*100:.0f}%<br>"
                           f"<b>Propagated shock: {traversal['shock_pct']:.2f}%</b><br>"
                           f"<i>{mechanism}</i>"),
                showlegend=False,
            ))
        else:
            dim_x += [x0, x1, None]
            dim_y += [y0, y1, None]

    dim_trace = go.Scatter(
        x=dim_x, y=dim_y,
        mode="lines",
        line=dict(color="#30363d", width=0.8),
        hoverinfo="skip",
        showlegend=False,
    )

    # ─── Nodes ───────────────────────────────────────────────────────────
    node_x, node_y = [], []
    node_size, node_color, node_line_color, node_line_width = [], [], [], []
    node_text, node_hover = [], []

    for name in G.nodes():
        x, y = pos[name]
        node_x.append(x); node_y.append(y)
        meta = PROTOCOLS[name]
        impact = impacts.get(name, {})
        shock_pct = impact.get("shock_pct", 0.0)
        loss_usd = impact.get("loss_usd", 0.0)

        is_epicenter = name == epicenter
        is_hit = shock_pct > 0 and not is_epicenter

        size = _node_size(meta["tvl_usd"]) * (1.5 if is_epicenter else 1.0)
        node_size.append(size)
        base = get_node_color(name)
        node_color.append(_hex_to_rgba(base, 1.0) if (is_hit or is_epicenter) else _hex_to_rgba(base, 0.35))

        if is_epicenter:
            node_line_color.append("#FF4F4F"); node_line_width.append(4)
        elif is_hit:
            node_line_color.append("#FF7B72"); node_line_width.append(2)
        else:
            node_line_color.append("#30363d"); node_line_width.append(1)

        node_text.append(name)
        node_hover.append(
            f"<b>{name}</b><br>"
            f"<i>{meta['type'].upper()} · {meta.get('issuer','')}</i><br>"
            f"TVL/Supply: ${meta['tvl_usd']/1e9:.2f}B<br>"
            f"<b>Cascade shock: {shock_pct:.2f}%</b><br>"
            f"<b>Est. loss: ${loss_usd/1e6:.1f}M</b><br>"
            f"<span style='color:#8b949e'>{meta.get('blurb','')[:140]}</span>"
        )

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        marker=dict(
            size=node_size, color=node_color,
            line=dict(color=node_line_color, width=node_line_width),
            opacity=1.0,
        ),
        text=node_text,
        textposition="bottom center",
        textfont=dict(color="#e6edf3", size=11, family="Inter, sans-serif"),
        hoverinfo="text",
        hovertext=node_hover,
        showlegend=False,
    )

    fig = go.Figure(data=[dim_trace] + hot_traces + [node_trace])
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="#0d1117",
        paper_bgcolor="#0d1117",
        font=dict(color="#e6edf3", family="Inter, sans-serif"),
        margin=dict(l=4, r=4, t=4, b=4),
        height=height_px,
        xaxis=dict(visible=False, showgrid=False, zeroline=False, fixedrange=False),
        yaxis=dict(visible=False, showgrid=False, zeroline=False, fixedrange=False, scaleanchor="x", scaleratio=1),
        dragmode="pan",
        hoverlabel=dict(
            bgcolor="#161b22", bordercolor="#30363d",
            font=dict(color="#e6edf3", family="Inter, sans-serif", size=12),
        ),
    )
    return fig
