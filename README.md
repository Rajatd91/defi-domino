# DeFi Domino — Protocol Contagion Risk Mapper

**Encode Club · DeFi Mini Hack 2026 submission**

> Terra → Anchor → 3AC → Celsius → Voyager. The 2022 collapses were predictable
> if anyone had mapped the dependencies. **DeFi Domino** is a stress-test simulator
> for the entire DeFi ecosystem — pick a failure event, see exactly which protocols
> cascade, and the dollar value at risk in real time.

## What it does

DeFi Domino models the dependency graph of the top 25 DeFi protocols
(Aave, MakerDAO, Lido, EigenLayer, Pendle, Morpho, Curve, Ethena, Spark, all
major LSTs/LRTs and stablecoins) and simulates how a failure at any single
node cascades through the system.

Pick a scenario (USDC depeg, stETH discount, EigenLayer mass slashing, Aave
exploit…) or build a custom one. The app shows:

- Total systemic dollar loss
- Force-directed contagion graph with shock-propagation highlighting
- Ranked list of impacted protocols with cascade paths
- Hop-by-hop mechanism trace (the audit trail behind every dollar figure)

## Why this is novel

Internal risk teams at Gauntlet, Chaos Labs and Block Analitica run private
contagion models for individual protocols. **No public, retail-facing tool
maps cross-protocol contagion in DeFi as a whole.** DeFi Domino fills that gap.

## How to run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501.

Click **Refresh TVL from DefiLlama** in the sidebar to overlay live TVL on
the static baseline.

## Architecture

```
app.py                  — Streamlit UI, scenario selection, layout
core/cascade.py         — BFS shock propagation engine
core/visualizer.py      — pyvis force-directed graph rendering
core/tvl_fetcher.py     — DefiLlama live TVL overlay
data/protocols.py       — Hand-curated protocol registry (25 nodes, 39 edges)
data/scenarios.py       — 7 expert-curated failure scenarios
```

## Cascade math

For each edge from holder → held-asset:

```
downstream_shock = upstream_shock × transmission × (exposure_usd / source_tvl) × damping^depth
```

- `transmission` (0–1): captures real-world buffers like overcollateralization,
  insurance funds, or partial reserve diversification.
- `damping`: 0.85 per hop, prevents runaway cycles.
- BFS to depth 4, threshold 0.05% to keep the graph readable.

Every exposure figure is sourced from protocol dashboards, governance forum
risk reports, and DefiLlama 2024–2026.

## What this models well

First-order liquidation cascades, collateral re-pricing, PSM/AMM imbalances,
multi-hop LRT → LST → lending market chains, EigenLayer → LRT slashing
propagation.

## What it does not model

Reflexive panic flows, oracle latency, MEV during unwinds, off-chain
redemption queue dynamics. These tend to *amplify* modelled losses — figures
should be read as a structural lower bound.

---

Built by Rajat Durge · April 2026
