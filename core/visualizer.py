"""
Force-directed graph visualization for the cascade result.

Renders an interactive HTML graph where:
  - Node color encodes protocol type (stablecoin, LST, lending, etc.)
  - Node size scales with TVL
  - Node opacity scales with cascade-induced shock_pct (red ring around hit nodes)
  - Edge thickness scales with the propagated shock that flowed through it
  - Hover tooltips show TVL, blurb, and propagated impact

Output is an HTML string that Streamlit embeds via components.html.
"""

from __future__ import annotations

import math

from pyvis.network import Network

from data.protocols import EDGES, PROTOCOLS, get_node_color, get_node_shape


def _size_from_tvl(tvl: float) -> float:
    if tvl <= 0:
        return 12
    return max(14, min(60, 8 * math.log10(tvl)))


def _alpha_from_shock(shock_pct: float) -> str:
    """Return a hex alpha component proportional to shock magnitude."""
    if shock_pct <= 0:
        return "33"  # faded
    if shock_pct >= 10:
        return "FF"
    return f"{int(0x33 + (0xFF - 0x33) * (shock_pct / 10)):02X}"


def render_cascade_graph(cascade_result: dict, height_px: int = 620) -> str:
    net = Network(
        height=f"{height_px}px",
        width="100%",
        bgcolor="#0d1117",
        font_color="#e6edf3",
        directed=True,
        notebook=False,
    )

    # Use a stable, readable layout
    net.set_options("""
    {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -55,
          "centralGravity": 0.012,
          "springLength": 140,
          "springConstant": 0.08,
          "damping": 0.6,
          "avoidOverlap": 0.7
        },
        "solver": "forceAtlas2Based",
        "stabilization": { "iterations": 120 }
      },
      "edges": {
        "smooth": { "type": "continuous" },
        "color": { "inherit": false }
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 100,
        "navigationButtons": false
      }
    }
    """)

    impacts = cascade_result["impacts"]
    epicenter = cascade_result["epicenter"]

    # Add nodes
    for name, meta in PROTOCOLS.items():
        impact = impacts.get(name, {})
        shock_pct = impact.get("shock_pct", 0.0)
        loss_usd = impact.get("loss_usd", 0.0)

        base_color = get_node_color(name)
        is_epicenter = name == epicenter
        is_hit = shock_pct > 0 and not is_epicenter

        if is_epicenter:
            border_color = "#FF4F4F"
            border_width = 6
            color_value = base_color
        elif is_hit:
            border_color = "#FF7B72"
            border_width = 1 + min(5, shock_pct / 2)
            color_value = base_color
        else:
            border_color = "#30363d"
            border_width = 1
            color_value = base_color + "66"  # transparent for unhit

        size = _size_from_tvl(meta["tvl_usd"])
        if is_epicenter:
            size *= 1.4

        title = (
            f"<b style='font-size:14px;color:#fff'>{name}</b><br>"
            f"<span style='color:#8b949e'>{meta['type'].upper()} · {meta.get('issuer', '')}</span><br>"
            f"<b>TVL/Supply:</b> ${meta['tvl_usd']/1e9:.2f}B<br>"
            f"<b>Cascade shock:</b> {shock_pct:.2f}%<br>"
            f"<b>Est. loss:</b> ${loss_usd/1e6:.1f}M<br>"
            f"<i style='color:#8b949e'>{meta.get('blurb','')[:160]}</i>"
        )

        net.add_node(
            name,
            label=name,
            title=title,
            color={"background": color_value, "border": border_color},
            borderWidth=border_width,
            size=size,
            shape=get_node_shape(name),
            font={"color": "#e6edf3", "size": 14, "face": "Inter, sans-serif"},
        )

    # Add edges
    traversed_keys = {(t["source"], t["target"]): t for t in cascade_result["traversed"]}
    for src, tgt, exposure_usd, transmission, mechanism in EDGES:
        # Note: cascade flows reverse direction — target's shock reaches source
        # But the structural edge direction (source holds target) is what we draw.
        traversal = traversed_keys.get((tgt, src))  # cascade direction is target→source
        if traversal:
            # This edge transmitted impact
            color = "#FF7B72"
            width = 1 + min(8, traversal["shock_pct"])
            label = f"{traversal['shock_pct']:.1f}%"
        else:
            color = "#30363d"
            width = 1.0
            label = ""

        title = (
            f"<b>{src} → {tgt}</b><br>"
            f"Exposure: ${exposure_usd/1e6:.0f}M<br>"
            f"Transmission: {transmission*100:.0f}%<br>"
            f"<i>{mechanism}</i>"
        )

        net.add_edge(
            src,
            tgt,
            title=title,
            color=color,
            width=width,
            arrows="to",
            label=label,
            font={"color": "#FF7B72", "size": 11, "background": "#0d1117"},
        )

    return net.generate_html(notebook=False)
