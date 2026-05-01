# DeFi Domino

A stress-test simulator that maps how a failure at one DeFi protocol cascades through the rest of the ecosystem.

**Live demo:** https://defi-domino.streamlit.app

![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.40-red.svg)

---

## Why I built this

Every big DeFi blow-up since 2022 (Terra, Anchor, 3AC, Celsius, the March 2023 USDC depeg) followed the same pattern: one protocol or asset breaks, and the real damage happens in the cascade through everything that depended on it.

There are private contagion models for individual protocols (Gauntlet, Chaos Labs, Block Analitica) but they sit behind enterprise contracts. Nothing public lets a regular DeFi user pick a failure event and see the full blast radius.

I wanted to build that, mostly because I wanted to understand the dependencies myself.

## What it does

Pick a failure scenario from the sidebar (or set up a custom one) and the engine simulates how the shock propagates across a graph of 24 protocols and 39 dependency edges.

You get back:

- Total systemic loss in dollars
- Which protocols got hit and by how much
- The cascade path, hop by hop
- A force-directed graph where edge thickness is the propagated shock
- Optional live TVL overlay from DefiLlama

## How it works

For each edge from a protocol that *holds* an asset to the asset/protocol it depends on, the cascade engine computes:

```
downstream_shock = upstream_shock * transmission * (exposure_usd / source_tvl) * damping^depth
```

- `transmission` (0 to 1) accounts for buffers like over-collateralisation, insurance funds, and reserve diversification
- `exposure / TVL` is the share of a protocol's balance sheet exposed to the upstream asset
- `damping = 0.85` per hop stops runaway cycles in dense sub-graphs
- BFS depth capped at 4 (enough for restaking -> LST -> lending -> yield chains)

Propagation runs as a BFS from the epicenter. Each protocol's loss is `shock_pct * its_TVL`, summed across every protocol the cascade reaches.

## What it doesn't model

This is honest, not coy. The model handles structural first-order cascades reasonably. It does not model:

- Reflexive panic flows
- Oracle latency / liquidation lag
- MEV during unwinds
- Off-chain redemption queue dynamics

These all tend to *amplify* the loss. So treat the numbers as a structural lower bound, not an upper bound.

## Scenarios shipped

| Scenario | Historical reference |
|---|---|
| USDC Depeg | March 2023, USDC traded $0.87-$0.95 for 48h after SVB |
| stETH Discount Widens | June 2022, stETH/ETH bottomed near 0.935 during 3AC unwind |
| Tether Reserve Crisis | October 2018 banking-driven USDT discount |
| EigenLayer Mass Slashing | April 2024 ezETH event (mechanism-adjacent) |
| Ethena Negative Funding | Q2 2024 funding compression |
| Aave V3 Critical Exploit | Hypothetical, modelled on Cream / Euler |
| Curve 3pool Drain | July 2023 Vyper compiler exploit ($73M) |

You can also pick any node as the epicenter and any shock magnitude in the custom override.

## Where the data came from

The 39 edges and dollar exposures were assembled by hand from:

- Aave reserve dashboards
- MakerDAO PSM stats and DAI Stats
- Lido integration registry
- EigenLayer LRT data
- Pendle market lists
- Governance forum risk reports (Gauntlet, Chaos Labs, Block Analitica)

## Run it locally

```bash
git clone https://github.com/Rajatd91/defi-domino.git
cd defi-domino
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open http://localhost:8501.

## Repo layout

```
app.py                         # Streamlit UI
core/
  cascade.py                   # BFS shock-propagation engine
  visualizer.py                # Plotly graph rendering
  tvl_fetcher.py               # DefiLlama TVL overlay
data/
  protocols.py                 # 24 protocols, 39 edges
  scenarios.py                 # 7 failure scenarios
tests/
  backtest.py                  # 70+ data integrity & math checks
scripts/
  generate_architecture.py     # Builds the diagrams in assets/
assets/                        # Architecture diagrams
.streamlit/config.toml         # Dark theme
```

## Tests

```bash
python3 tests/backtest.py
```

70+ checks covering data integrity (every edge endpoint exists, every scenario references a real protocol), every preset scenario running without errors, every protocol working as an epicenter, edge cases (tiny shock, huge shock, leaf nodes), and a sanity bound that no protocol's loss can exceed its own TVL.

## What I'd add next

- Smart-contract-level oracle dependency edges (Chainlink, Pyth)
- Per-chain L2 cascade splits (Arbitrum, Base)
- Replay the May 2022 and March 2023 cascades against the model and check it
- Webhook alerts when live TVL crosses risk thresholds
- AVS slashing bound stress tests for restaking

## License

MIT, 2026 Rajat Durge.
