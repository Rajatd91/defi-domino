"""
Generate static architecture diagrams for the README.

Produces:
  - assets/architecture.png   - the protocol dependency graph (network)
  - assets/system.png         - the layered system diagram
"""

import os
import sys

sys.path.insert(0, ".")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

from data.protocols import EDGES, PROTOCOLS, NODE_TYPES


OUT_DIR = "assets"
os.makedirs(OUT_DIR, exist_ok=True)

DARK_BG = "#0d1117"
PANEL = "#161b22"
TEXT = "#e6edf3"
MUTED = "#8b949e"
BORDER = "#30363d"
ACCENT = "#FF4F4F"


# ─────────────────────── Diagram 1: protocol graph ───────────────────────

def build_protocol_graph_png():
    import math

    G = nx.DiGraph()
    for name, meta in PROTOCOLS.items():
        G.add_node(name, type=meta["type"], tvl=meta["tvl_usd"])
    for src, tgt, exp, _, _ in EDGES:
        G.add_edge(src, tgt, weight=exp)

    fig, ax = plt.subplots(figsize=(16, 11), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.set_axis_off()

    # Group nodes by type into manually-placed clusters for readability
    type_clusters = {
        "stablecoin": (-4.0,  2.5),
        "synthetic":  (-1.0,  3.2),
        "cdp":        ( 1.5,  3.0),
        "lending":    ( 4.0,  1.5),
        "yield":      ( 4.5, -1.5),
        "lrt":        ( 1.8, -3.0),
        "restaking":  (-1.2, -3.0),
        "lst":        (-3.8, -1.5),
        "dex":        (-4.0,  0.5),
    }

    # Within each cluster, ring out the nodes
    pos = {}
    type_to_nodes = {}
    for n, d in G.nodes(data=True):
        type_to_nodes.setdefault(d["type"], []).append(n)
    for ptype, (cx, cy) in type_clusters.items():
        nodes = type_to_nodes.get(ptype, [])
        if not nodes:
            continue
        if len(nodes) == 1:
            pos[nodes[0]] = (cx, cy)
            continue
        radius = 0.45 + 0.15 * len(nodes)
        for i, n in enumerate(sorted(nodes)):
            angle = 2 * math.pi * i / len(nodes)
            pos[n] = (cx + radius * math.cos(angle),
                      cy + radius * math.sin(angle))

    # Node sizing by TVL (log-scaled)
    sizes = []
    colors = []
    for n in G.nodes():
        tvl = PROTOCOLS[n]["tvl_usd"]
        sizes.append(max(450, 240 * math.log10(tvl)))
        colors.append(NODE_TYPES[PROTOCOLS[n]["type"]]["color"])

    # Edge widths by exposure
    edge_widths = []
    max_exp = max(d["weight"] for *_, d in G.edges(data=True))
    for *_, d in G.edges(data=True):
        edge_widths.append(0.4 + 4.0 * (d["weight"] / max_exp))

    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color=BORDER, width=edge_widths,
        alpha=0.55, arrows=True, arrowsize=8,
        connectionstyle="arc3,rad=0.06",
    )
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=colors, node_size=sizes,
        edgecolors=BORDER, linewidths=1.2, alpha=0.95,
    )
    # Labels offset slightly below each node to avoid overlap
    label_pos = {n: (x, y - 0.12) for n, (x, y) in pos.items()}
    nx.draw_networkx_labels(
        G, label_pos, ax=ax,
        font_color=TEXT, font_size=9, font_weight="bold",
        font_family="sans-serif",
    )

    # Cluster type labels
    cluster_labels = {
        "stablecoin": "STABLECOINS",
        "lst": "LSTs",
        "lrt": "LRTs",
        "lending": "LENDING",
        "dex": "DEX",
        "yield": "YIELD",
        "cdp": "CDP",
        "restaking": "RESTAKING",
        "synthetic": "SYNTHETIC $",
    }
    for ptype, (cx, cy) in type_clusters.items():
        if ptype not in type_to_nodes:
            continue
        radius = 0.45 + 0.15 * max(1, len(type_to_nodes[ptype]))
        ax.text(cx, cy + radius + 0.45, cluster_labels[ptype],
                fontsize=10, color=NODE_TYPES[ptype]["color"],
                weight="bold", ha="center", family="sans-serif")

    # Title
    fig.text(
        0.5, 0.96,
        "DeFi Domino - 24-Protocol Dependency Graph",
        fontsize=18, color=TEXT, weight="bold",
        ha="center", family="sans-serif",
    )
    fig.text(
        0.5, 0.92,
        "39 hand-curated edges  ·  node size ∝ TVL  ·  color encodes protocol type",
        fontsize=11, color=MUTED, ha="center", family="sans-serif",
    )

    # Legend (manual, lower-left)
    legend_items = [
        ("Stablecoin", "#3FB950"),
        ("LST",        "#58A6FF"),
        ("LRT",        "#A371F7"),
        ("Lending",    "#F0883E"),
        ("DEX/AMM",    "#E3B341"),
        ("Yield",      "#DB61A2"),
        ("CDP",        "#FF7B72"),
        ("Restaking",  "#BC8CFF"),
        ("Synthetic",  "#56D4DD"),
    ]
    handles = [mpatches.Patch(color=c, label=lbl) for lbl, c in legend_items]
    leg = ax.legend(
        handles=handles, loc="lower left",
        facecolor=PANEL, edgecolor=BORDER,
        labelcolor=TEXT, fontsize=9, ncol=3, framealpha=0.95,
    )
    for txt in leg.get_texts():
        txt.set_color(TEXT)

    out = os.path.join(OUT_DIR, "architecture.png")
    plt.savefig(out, dpi=170, facecolor=DARK_BG, bbox_inches="tight")
    plt.close()
    print(f"✓ {out}")


# ─────────────────────── Diagram 2: system layers ───────────────────────

def build_system_diagram_png():
    fig, ax = plt.subplots(figsize=(12, 7), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.set_axis_off()

    layers = [
        # (y, height, title, items, color)
        (5.6, 1.1, "PRESENTATION", [
            "Streamlit UI  ·  Custom CSS  ·  Sidebar scenarios  ·  Metric cards"
        ], "#1f2937"),
        (4.2, 1.1, "VISUALIZATION", [
            "pyvis force-directed graph  ·  matplotlib static export  ·  pandas tables"
        ], "#1f2937"),
        (2.8, 1.1, "CASCADE ENGINE  (core/)", [
            "BFS shock propagation   ·   transmission × exposure-ratio × damping^depth"
        ], "#2a0e0e"),
        (1.4, 1.1, "DATA LAYER  (data/)", [
            "24 protocols  ·  39 dependency edges  ·  7 curated scenarios"
        ], "#1f2937"),
        (0.0, 1.1, "EXTERNAL", [
            "DefiLlama API  (live TVL overlay)"
        ], "#0f1923"),
    ]
    edge_colors = [BORDER, BORDER, ACCENT, BORDER, BORDER]

    for (y, h, title, items, fill), edge in zip(layers, edge_colors):
        rect = mpatches.FancyBboxPatch(
            (0.4, y), 11.2, h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            linewidth=1.5, edgecolor=edge, facecolor=fill,
        )
        ax.add_patch(rect)
        ax.text(0.7, y + h - 0.3, title,
                fontsize=10, weight="bold", color="#FF7B72",
                family="sans-serif")
        for i, item in enumerate(items):
            ax.text(0.7, y + 0.32 - i * 0.3, item,
                    fontsize=11, color=TEXT, family="sans-serif")

    # Down-arrows between layers
    for y in [5.45, 4.05, 2.65, 1.25]:
        ax.annotate("", xy=(6, y - 0.18), xytext=(6, y + 0.07),
                    arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.5))

    fig.text(0.5, 0.96, "DeFi Domino - System Architecture",
             fontsize=18, color=TEXT, weight="bold",
             ha="center", family="sans-serif")

    out = os.path.join(OUT_DIR, "system.png")
    plt.savefig(out, dpi=170, facecolor=DARK_BG, bbox_inches="tight")
    plt.close()
    print(f"✓ {out}")


if __name__ == "__main__":
    build_protocol_graph_png()
    build_system_diagram_png()
