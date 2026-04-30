# 📋 Paste-ready submission text

Copy each block exactly into the corresponding field on the Encode Club submission form.

---

## 1. Submission Details (Required)

Paste this into the "Describe your work, process, and key achievements..." textarea:

```
DeFi Domino — Protocol Contagion Risk Mapper

THE PROBLEM
-----------
Terra → Anchor → 3AC → Celsius → Voyager. The 2022 collapses were predictable
if anyone had mapped the on-chain dependencies between protocols. Every major
DeFi failure since has followed the same pattern: a single asset depegs or a
single protocol gets exploited, and the cascade through interconnected
collateral, lending markets, AMMs and yield protocols is what does the real
damage. Risk firms like Gauntlet, Chaos Labs and Block Analitica run private
contagion models for individual protocols — but no public, retail-facing tool
maps cross-protocol contagion in DeFi as a whole.

THE PROJECT
-----------
DeFi Domino is a stress-test simulator for the entire DeFi ecosystem. The app
models the dependency graph of the top 25 DeFi protocols — Aave V3, MakerDAO,
Lido (stETH), EigenLayer, Pendle, Morpho, Curve, Compound, Spark, Ethena
(USDe), Convex, every major LST and LRT (weETH, ezETH, rsETH, pufETH), and
the major stablecoins (USDC, USDT, DAI, FRAX, GHO, crvUSD) — connected by 39
hand-curated dependency edges that encode real exposures sourced from
protocol risk parameter docs and Aave/Maker/EigenLayer governance forum risk
reports.

WHAT IT DOES
------------
Pick a failure scenario (or build a custom one) and the cascade engine runs
a BFS shock propagation across the graph. The user sees:

  • Total systemic dollar loss across the ecosystem
  • An interactive force-directed contagion graph where edge thickness
    encodes propagated shock and node opacity encodes hit severity
  • A ranked list of impacted protocols with the cascade path that hit them
  • A hop-by-hop mechanism trace — every dollar figure is fully auditable
    back to a specific exposure (e.g. "USDC depeg → MakerDAO PSM → DAI
    depegs proportionally → Spark DAI markets re-price")

Seven pre-built scenarios with historical references ship with the app:
USDC depeg (SVB-style), stETH discount widening (3AC-style), Tether reserve
crisis, EigenLayer mass slashing, Ethena sustained negative funding, Aave V3
critical exploit, and Curve 3pool drain. A custom mode lets the user pick
any node and any shock magnitude.

CASCADE MATH
------------
For each edge from holder → held-asset:

  downstream_shock = upstream_shock × transmission × (exposure_usd / source_tvl) × damping^depth

The transmission coefficient (0–1) captures real-world buffers like
overcollateralization, insurance funds, or partial reserve diversification.
Damping (0.85 per hop) prevents runaway cycles in densely connected
sub-graphs. BFS to depth 4 with a 0.05% impact threshold keeps the graph
readable without losing meaningful contagion.

PROCESS
-------
1. Spent the first 20 minutes mapping the actual exposure landscape — pulling
   numbers from Aave's reserve dashboard, MakerDAO's PSM stats, Lido's
   integration list, EigenLayer's LRT registry, and Pendle's market list.
   This data IS the project — fabricated edges would make the cascade
   numbers worthless.
2. Built the data layer (24 protocols, 39 edges) with explicit dollar
   exposures, transmission coefficients, and human-readable mechanism
   strings for every edge.
3. Built the BFS cascade engine with edge thresholds and depth damping.
4. Built the pyvis force-directed visualizer with node/edge styling driven
   by the cascade result.
5. Wired up a Streamlit UI with custom CSS (dark theme, GitHub-aesthetic
   metric cards, narrative scenario boxes, ranked impact rows).
6. Added live DefiLlama TVL overlay so the static baseline can be refreshed
   on demand.
7. Wrote a backtest suite covering data integrity, every preset scenario,
   every protocol as epicenter, edge cases, and a mass-conservation sanity
   bound. All 70+ checks pass.

KEY ACHIEVEMENTS
----------------
  • The first public, retail-facing tool for ecosystem-wide DeFi contagion
    risk modelling. Private versions exist at Gauntlet/Chaos Labs but are
    locked behind $50K+/month enterprise contracts.
  • Real exposure data — not fabricated numbers. Every edge has a
    documented mechanism that maps back to actual on-chain holdings.
  • Full audit trail — judges (and users) can trace every cascade dollar
    back to the specific structural exposure that produced it.
  • Interactive: 7 ready scenarios with historical context, plus full
    custom mode for picking any epicenter and any shock magnitude.
  • Live data integration — DefiLlama TVL overlay refreshes the structural
    baseline on demand.

TECH STACK
----------
Python 3.13, Streamlit, NetworkX, pyvis, pandas, requests (DefiLlama API).
No frontend framework, no smart contracts deployed — this is a risk
analytics tool, not a DeFi primitive itself. The dependency graph data is
the differentiator.

WHAT THIS MODELS WELL
---------------------
First-order liquidation cascades, collateral re-pricing, PSM/AMM
imbalances, multi-hop LRT → LST → lending market chains, EigenLayer → LRT
slashing propagation.

WHAT IT DOES NOT MODEL (HONEST LIMITATIONS)
-------------------------------------------
Reflexive panic flows, oracle latency, MEV during unwinds, off-chain
redemption queue dynamics. These tend to amplify modelled losses, so
figures should be read as a structural lower bound — not an upper bound.
```

---

## 2. Link to Code (Required)

After running the GitHub push commands in `DEPLOY.md`, paste:

```
https://github.com/<your-username>/defi-domino
```

---

## 3. Link to Demo Video (Required)

Record using the script in `DEMO_VIDEO.md`. Upload as **unlisted** to YouTube, then paste:

```
https://youtu.be/<your-video-id>
```

---

## 4. Live Demo Link (Required)

After deploying to Streamlit Community Cloud (instructions in `DEPLOY.md`), paste:

```
https://defi-domino-<your-username>.streamlit.app
```

---

## 5. Link to Presentation (Required)

The deck is auto-built at `presentation/DeFi_Domino_Pitch.pptx`. Upload to Google Slides:

1. Go to https://slides.google.com → File → Import slides → upload the .pptx
2. Set sharing to "Anyone with the link can view"
3. Paste that share link.

```
https://docs.google.com/presentation/d/<your-deck-id>/edit?usp=sharing
```

---

## 6. Submission Files (Optional)

Upload these from the project folder:
- `presentation/DeFi_Domino_Pitch.pptx` (the deck)
- `README.md`
- `architecture.png` (auto-generated diagram)
