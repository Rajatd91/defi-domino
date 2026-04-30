"""
DeFi Domino — Protocol Contagion Risk Mapper
Encode Club DeFi Mini Hack 2026 submission.

Maps the dependency graph of the top 25 DeFi protocols and simulates
how a failure at any node cascades through to others. Shows real exposures,
real propagation paths, and live TVL at risk.
"""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

from core.cascade import simulate_cascade, rank_impacted, fmt_usd
from core.tvl_fetcher import fetch_all_live
from core.visualizer import render_cascade_graph
from data.protocols import PROTOCOLS, EDGES
from data.scenarios import SCENARIOS


@st.cache_data(show_spinner=False)
def _cached_simulate(epicenter: str, shock_pct: float, tvl_signature: tuple) -> dict:
    # tvl_signature is included so cache invalidates when live TVL is refreshed
    _ = tvl_signature
    return simulate_cascade(epicenter=epicenter, shock_pct=shock_pct)


@st.cache_data(show_spinner=False)
def _cached_graph_html(epicenter: str, shock_pct: float, tvl_signature: tuple) -> str:
    _ = tvl_signature
    result = simulate_cascade(epicenter=epicenter, shock_pct=shock_pct)
    return render_cascade_graph(result, height_px=620)


st.set_page_config(
    page_title="DeFi Domino — Contagion Risk Mapper",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------- Custom styling ---------------------------

st.markdown("""
<style>
/* Hide default Streamlit chrome we don't want */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Tighten layout */
.block-container {padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1400px;}

/* Hero */
.hero {
  background: linear-gradient(135deg, #1a0a0a 0%, #0d1117 100%);
  border: 1px solid #30363d;
  border-radius: 12px;
  padding: 28px 32px;
  margin-bottom: 18px;
}
.hero h1 {
  font-size: 38px;
  margin: 0;
  color: #f0f6fc;
  letter-spacing: -0.02em;
  font-weight: 700;
}
.hero h1 .accent { color: #FF4F4F; }
.hero .subtitle {
  color: #8b949e;
  font-size: 16px;
  margin-top: 8px;
  max-width: 880px;
  line-height: 1.5;
}
.hero .tag {
  display: inline-block;
  background: rgba(255, 79, 79, 0.12);
  color: #FF7B72;
  border: 1px solid #FF4F4F44;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: 12px;
}

/* Metric cards */
.metric-row { display: flex; gap: 14px; margin: 16px 0 22px 0; }
.metric-card {
  flex: 1;
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 10px;
  padding: 16px 18px;
}
.metric-card.alert { border-color: #FF4F4F; background: linear-gradient(180deg, #2a0e0e 0%, #161b22 100%); }
.metric-card .label {
  color: #8b949e;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 600;
}
.metric-card .value {
  color: #f0f6fc;
  font-size: 28px;
  font-weight: 700;
  margin-top: 4px;
  letter-spacing: -0.02em;
}
.metric-card.alert .value { color: #FF7B72; }
.metric-card .delta {
  color: #8b949e;
  font-size: 12px;
  margin-top: 4px;
}

/* Section headers */
.section-h {
  color: #f0f6fc;
  font-size: 18px;
  font-weight: 700;
  margin: 18px 0 8px 0;
  padding-bottom: 6px;
  border-bottom: 1px solid #21262d;
}

/* Narrative box */
.narrative {
  background: #161b22;
  border-left: 3px solid #FF4F4F;
  padding: 14px 18px;
  border-radius: 6px;
  color: #c9d1d9;
  font-size: 14px;
  line-height: 1.55;
  margin-bottom: 14px;
}
.narrative .h {
  color: #FF7B72;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 700;
  margin-bottom: 6px;
}
.narrative .historical {
  color: #8b949e;
  font-size: 12px;
  font-style: italic;
  margin-top: 8px;
  border-top: 1px solid #21262d;
  padding-top: 8px;
}

/* Impact rows */
.impact-row {
  display: flex;
  align-items: center;
  background: #161b22;
  border: 1px solid #21262d;
  border-radius: 8px;
  padding: 10px 14px;
  margin-bottom: 6px;
  font-size: 13px;
}
.impact-row .name {
  font-weight: 600;
  color: #f0f6fc;
  flex: 0 0 150px;
}
.impact-row .ptype {
  color: #8b949e;
  font-size: 11px;
  text-transform: uppercase;
  flex: 0 0 90px;
}
.impact-row .shock {
  color: #FF7B72;
  font-weight: 700;
  flex: 0 0 80px;
  text-align: right;
}
.impact-row .loss {
  color: #f0f6fc;
  font-weight: 700;
  flex: 0 0 100px;
  text-align: right;
}
.impact-row .path {
  color: #8b949e;
  font-size: 12px;
  flex: 1;
  padding-left: 18px;
  font-style: italic;
}

/* Path arrow */
.path-arrow { color: #FF4F4F; margin: 0 6px; }

.legend { display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 8px; }
.legend-item { display: flex; align-items: center; font-size: 11px; color: #8b949e; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }

</style>
""", unsafe_allow_html=True)


# --------------------------- Hero ---------------------------

st.markdown("""
<div class="hero">
  <span class="tag">🩸 DeFi Systemic Risk · Cross-Protocol Stress Testing</span>
  <h1>DeFi <span class="accent">Domino</span></h1>
  <div class="subtitle">
    Terra → Anchor → 3AC → Celsius. The 2022 collapses were predictable
    if anyone had mapped the dependencies. <b>DeFi Domino</b> is a stress-test simulator for
    the entire DeFi ecosystem — pick a failure event, see exactly which protocols cascade,
    and the dollar value at risk in real time.
  </div>
</div>
""", unsafe_allow_html=True)


# --------------------------- Session state ---------------------------

if "live_tvls" not in st.session_state:
    st.session_state.live_tvls = {}
if "tvl_fetched" not in st.session_state:
    st.session_state.tvl_fetched = False


# --------------------------- Sidebar ---------------------------

with st.sidebar:
    st.markdown("### ⚡ Failure Scenario")

    scenario_keys = list(SCENARIOS.keys())
    scenario_labels = [f"{SCENARIOS[k]['icon']} {SCENARIOS[k]['name']}" for k in scenario_keys]
    selected_idx = st.radio(
        "Pre-built scenarios",
        range(len(scenario_keys)),
        format_func=lambda i: scenario_labels[i],
        label_visibility="collapsed",
    )
    scenario_key = scenario_keys[selected_idx]
    scenario = SCENARIOS[scenario_key]

    st.markdown("---")
    st.markdown("### 🔧 Custom Override")
    custom_epicenter = st.selectbox(
        "Override epicenter",
        ["(use scenario)"] + sorted(PROTOCOLS.keys()),
        index=0,
    )
    custom_shock = st.slider(
        "Shock magnitude (%)",
        min_value=1.0, max_value=50.0,
        value=float(scenario["shock_pct"]),
        step=0.5,
        help="How far the epicenter asset/protocol drops in value.",
    )

    st.markdown("---")
    st.markdown("### 📡 Live Data")
    if st.button("🔄 Refresh TVL from DefiLlama", use_container_width=True):
        with st.spinner("Fetching live TVL..."):
            st.session_state.live_tvls = fetch_all_live(PROTOCOLS, max_protocols=10)
            st.session_state.tvl_fetched = True

    if st.session_state.tvl_fetched and st.session_state.live_tvls:
        st.success(f"Live TVL synced for {len(st.session_state.live_tvls)} protocols.")
    else:
        st.caption("Click to overlay live DefiLlama TVL onto the cascade math.")

    st.markdown("---")
    st.caption(
        "Dependency data hand-curated from Aave, MakerDAO, Lido, EigenLayer, "
        "Pendle, Morpho and Curve protocol risk docs and governance forum reports."
    )


# --------------------------- Apply live TVL overlay ---------------------------

# Mutate PROTOCOLS in-place for this run if user pulled live data
if st.session_state.live_tvls:
    for name, tvl in st.session_state.live_tvls.items():
        if name in PROTOCOLS:
            PROTOCOLS[name]["tvl_usd"] = tvl


# --------------------------- Run simulation ---------------------------

epicenter = scenario["epicenter"] if custom_epicenter == "(use scenario)" else custom_epicenter
shock_pct = custom_shock

# Signature for cache invalidation when live TVL is refreshed
tvl_sig = tuple(sorted((k, round(v, 0)) for k, v in st.session_state.live_tvls.items()))

result = _cached_simulate(epicenter, shock_pct, tvl_sig)


# --------------------------- Top metrics ---------------------------

ecosystem_tvl = sum(p["tvl_usd"] for p in PROTOCOLS.values())
systemic_pct = (result["total_systemic_loss_usd"] / ecosystem_tvl) * 100 if ecosystem_tvl else 0

st.markdown(f"""
<div class="metric-row">
  <div class="metric-card alert">
    <div class="label">⚠️ Total Systemic Loss</div>
    <div class="value">{fmt_usd(result['total_systemic_loss_usd'])}</div>
    <div class="delta">{systemic_pct:.2f}% of mapped DeFi TVL</div>
  </div>
  <div class="metric-card">
    <div class="label">Epicenter Loss</div>
    <div class="value">{fmt_usd(result['epicenter_loss_usd'])}</div>
    <div class="delta">{epicenter} · {shock_pct:.1f}% shock</div>
  </div>
  <div class="metric-card">
    <div class="label">Downstream Loss</div>
    <div class="value">{fmt_usd(result['total_downstream_loss_usd'])}</div>
    <div class="delta">Contagion-induced</div>
  </div>
  <div class="metric-card">
    <div class="label">Protocols Affected</div>
    <div class="value">{result['protocols_affected']}</div>
    <div class="delta">of {len(PROTOCOLS)} mapped</div>
  </div>
</div>
""", unsafe_allow_html=True)


# --------------------------- Narrative ---------------------------

if custom_epicenter == "(use scenario)":
    st.markdown(f"""
    <div class="narrative">
      <div class="h">{scenario['icon']} Scenario · {scenario['name']}</div>
      <div><b>{scenario['tagline']}</b></div>
      <div style="margin-top:8px">{scenario['narrative']}</div>
      <div class="historical">📜 Reference: {scenario['historical']}</div>
    </div>
    """, unsafe_allow_html=True)
else:
    epi_meta = PROTOCOLS[epicenter]
    st.markdown(f"""
    <div class="narrative">
      <div class="h">🔧 Custom Scenario</div>
      <div><b>{epicenter}</b> ({epi_meta['type']}, issued by {epi_meta.get('issuer','—')}) loses {shock_pct:.1f}% of value.</div>
      <div style="margin-top:8px">{epi_meta['blurb']}</div>
    </div>
    """, unsafe_allow_html=True)


# --------------------------- Two-column body ---------------------------

col_graph, col_ranked = st.columns([3, 2], gap="large")

with col_graph:
    st.markdown('<div class="section-h">Contagion Graph</div>', unsafe_allow_html=True)

    # Legend
    st.markdown("""
    <div class="legend">
      <div class="legend-item"><span class="legend-dot" style="background:#3FB950"></span>Stablecoin</div>
      <div class="legend-item"><span class="legend-dot" style="background:#58A6FF"></span>LST</div>
      <div class="legend-item"><span class="legend-dot" style="background:#A371F7"></span>LRT</div>
      <div class="legend-item"><span class="legend-dot" style="background:#F0883E"></span>Lending</div>
      <div class="legend-item"><span class="legend-dot" style="background:#E3B341"></span>DEX/AMM</div>
      <div class="legend-item"><span class="legend-dot" style="background:#DB61A2"></span>Yield</div>
      <div class="legend-item"><span class="legend-dot" style="background:#FF7B72"></span>CDP</div>
      <div class="legend-item"><span class="legend-dot" style="background:#BC8CFF"></span>Restaking</div>
      <div class="legend-item"><span class="legend-dot" style="background:#56D4DD"></span>Synthetic</div>
    </div>
    <div style="color:#8b949e;font-size:12px;margin-bottom:8px">
      Red border + bright label = hit. Edge thickness ∝ propagated shock. Node size ∝ TVL. Hover for detail.
    </div>
    """, unsafe_allow_html=True)

    graph_html = _cached_graph_html(epicenter, shock_pct, tvl_sig)
    components.html(graph_html, height=640, scrolling=False)


with col_ranked:
    st.markdown('<div class="section-h">Cascade Path · Top Hits</div>', unsafe_allow_html=True)

    ranked = rank_impacted(result, top_n=12)
    if not ranked:
        st.info("No downstream protocols meet the 0.05% impact threshold for this shock magnitude. Try a larger shock.")
    else:
        for name, impact in ranked:
            ptype = PROTOCOLS[name]["type"].upper()
            paths = impact.get("incoming_paths", [])
            # Show the strongest path
            top_path = max(paths, key=lambda p: p["shock_pct"]) if paths else None
            path_str = f"via {top_path['from']}" if top_path else ""

            st.markdown(f"""
            <div class="impact-row">
              <div class="name">{name}</div>
              <div class="ptype">{ptype}</div>
              <div class="shock">−{impact['shock_pct']:.2f}%</div>
              <div class="loss">{fmt_usd(impact['loss_usd'])}</div>
              <div class="path">{path_str}</div>
            </div>
            """, unsafe_allow_html=True)


# --------------------------- Detailed cascade paths ---------------------------

st.markdown('<div class="section-h">Propagation Paths · Mechanism Trace</div>', unsafe_allow_html=True)
st.markdown(
    "<div style='color:#8b949e;font-size:13px;margin-bottom:10px'>"
    "Every edge the shock traversed, in order of magnitude. This is the audit trail "
    "behind the dollar figures above — each row corresponds to a real exposure documented "
    "in protocol risk parameters."
    "</div>",
    unsafe_allow_html=True,
)

# Build dataframe
trace_rows = []
for t in sorted(result["traversed"], key=lambda x: -x["shock_pct"]):
    trace_rows.append({
        "Hop": t["depth"],
        "From": t["source"],
        "→ To": t["target"],
        "Shock %": round(t["shock_pct"], 3),
        "Est. Loss": fmt_usd(t["loss_usd"]),
        "Mechanism": t["mechanism"],
    })

if trace_rows:
    df = pd.DataFrame(trace_rows)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Hop": st.column_config.NumberColumn(width="small"),
            "Shock %": st.column_config.NumberColumn(format="%.3f %%", width="small"),
            "Est. Loss": st.column_config.TextColumn(width="small"),
            "Mechanism": st.column_config.TextColumn(width="large"),
        },
        height=320,
    )
else:
    st.caption("No propagation paths above threshold.")


# --------------------------- Methodology ---------------------------

with st.expander("📐 Methodology — how the cascade math works"):
    st.markdown("""
**Graph model.** Nodes are protocols, stablecoins, and asset types. Edges encode
real exposures: *Aave V3 holds $5.4B of stETH as collateral*, *DAI holds $2.4B of USDC
in the PSM*, *weETH backs $4.3B of stETH-equivalent restaked positions*. All exposure
figures are sourced from protocol dashboards, governance forum risk reports
(Gauntlet, Chaos Labs, Block Analitica), and DefiLlama 2024–2026.

**Shock propagation.** From the epicenter, we BFS across reverse edges (a protocol
holding the shocked asset takes a hit). For each edge:

```
downstream_shock = upstream_shock × transmission × (exposure_usd / source_tvl) × damping^depth
```

- `transmission` (0–1): captures real-world buffers like overcollateralization,
  insurance funds, or partial reserve diversification. A liquidation engine
  with 110% LTV has lower transmission than a 1:1 PSM.
- `damping`: 0.85 per hop, prevents runaway cycles in densely connected sub-graphs.
- Threshold: shocks below 0.05% are pruned for readability.

**What this models well.** First-order liquidation cascades, collateral re-pricing,
direct PSM/AMM imbalances, multi-hop LRT → LST → lending market chains.

**What this does not model.** Reflexive panic flows, oracle latency, MEV during
unwinds, off-chain redemption queue dynamics. These tend to *amplify* the modelled
losses — so figures here should be read as a structural lower bound.

**Data freshness.** Static TVL is the calibrated baseline. Click *Refresh TVL* to
overlay live DefiLlama figures for the top protocols.
    """)


with st.expander("🗂️ Full protocol registry"):
    rows = []
    for name, meta in sorted(PROTOCOLS.items(), key=lambda x: -x[1]["tvl_usd"]):
        rows.append({
            "Protocol": name,
            "Type": meta["type"],
            "Issuer": meta.get("issuer", "—"),
            "TVL / Supply": fmt_usd(meta["tvl_usd"]),
            "Description": meta.get("blurb", "")[:140] + ("..." if len(meta.get("blurb", "")) > 140 else ""),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=400)


with st.expander("🔗 Edge registry — every modelled exposure"):
    edge_rows = []
    for src, tgt, exp, trans, mech in sorted(EDGES, key=lambda e: -e[2]):
        edge_rows.append({
            "Source (holder)": src,
            "→ Target (held)": tgt,
            "Exposure": fmt_usd(exp),
            "Transmission": f"{trans*100:.0f}%",
            "Mechanism": mech,
        })
    st.dataframe(pd.DataFrame(edge_rows), use_container_width=True, hide_index=True, height=420)


st.markdown(
    "<div style='text-align:center;color:#6e7681;font-size:11px;margin-top:32px;padding-top:16px;border-top:1px solid #21262d'>"
    "DeFi Domino · Built in Python with Streamlit, NetworkX, and DefiLlama. "
    "Not financial advice. Cascade losses are modelled estimates."
    "</div>",
    unsafe_allow_html=True,
)
