"""
Pre-built failure scenarios with expert-curated narratives.

Each scenario describes a plausible historical-pattern failure mode
and pre-loads the simulator with the right shock parameters.
"""

SCENARIOS = {
    "usdc_depeg": {
        "name": "USDC Depeg - SVB Repeat",
        "icon": "🟢",
        "epicenter": "USDC",
        "shock_pct": 12.0,
        "tagline": "March 2023 saw USDC depeg to $0.88 after $3.3B was stuck at SVB.",
        "narrative": (
            "Circle holds reserves at multiple banks. A regional banking crisis or "
            "Treasury market dislocation could lock 5-10% of reserves. USDC repegs once "
            "redemption clears - but DeFi positions liquidated mid-depeg are not unwound. "
            "MakerDAO's USDC PSM holds ~$2.4B; DAI depegs in proportion. "
            "Aave's USDC borrowers face collateral mismatches; Curve 3pool drains."
        ),
        "historical": "March 10-13, 2023 - USDC traded $0.87-$0.95 for 48 hours.",
    },
    "stETH_discount": {
        "name": "stETH Discount Widens - Validator Stress",
        "icon": "🔵",
        "epicenter": "stETH",
        "shock_pct": 8.0,
        "tagline": "stETH/ETH traded 0.93 in June 2022 during 3AC's forced unwind.",
        "narrative": (
            "An LST-heavy fund forced into liquidation, a validator slashing event, "
            "or an Ethereum withdrawal-queue extension can widen the stETH/ETH discount. "
            "Aave holds ~$5.4B stETH as collateral - even a 5% discount triggers "
            "leveraged-staking liquidation cascades. Every LRT prices through the move."
        ),
        "historical": "June 2022 - stETH/ETH bottomed at 0.935 during 3AC unwind.",
    },
    "usdt_collapse": {
        "name": "Tether Reserve Crisis",
        "icon": "🟢",
        "epicenter": "USDT",
        "shock_pct": 25.0,
        "tagline": "Tether reserves are concentrated; a NYAG-style action would freeze redemptions.",
        "narrative": (
            "USDT is the reserve currency of offshore crypto. Any meaningful redemption "
            "halt would shred Curve's 3pool, freeze ~$2.2B of Aave's USDT collateral, "
            "and force a liquidity cascade across every cross-pair on Asian DEXes. "
            "Lower transmission to USDC because they are not directly linked, but "
            "DAI catches collateral splash via the PSM unwind."
        ),
        "historical": "October 2018 - USDT traded $0.85 amid Bitfinex/Tether banking issues.",
    },
    "eigenlayer_slashing": {
        "name": "EigenLayer Mass Slashing Event",
        "icon": "🟪",
        "epicenter": "EigenLayer",
        "shock_pct": 15.0,
        "tagline": "An AVS bug, not operator misbehaviour, causes correlated slashing.",
        "narrative": (
            "Restaking compounds slashing surface area. A single buggy AVS that "
            "the majority of operators run can slash a meaningful slice of restaked "
            "ETH. Every LRT - weETH, ezETH, rsETH, pufETH - repegs downward in lockstep. "
            "Pendle PT-weETH holders take losses; Aave weETH e-mode liquidates."
        ),
        "historical": "April 2024 - Renzo's ezETH depegged 8% on circulation/redemption mismatch (mechanism-adjacent).",
    },
    "usde_funding": {
        "name": "Ethena Sustained Negative Funding",
        "icon": "💎",
        "epicenter": "USDe",
        "shock_pct": 6.0,
        "tagline": "Perp funding flips negative for weeks; USDe yield turns negative.",
        "narrative": (
            "USDe earns yield from positive perp funding on its short ETH/BTC hedges. "
            "A prolonged bear flush flips funding negative - sUSDe yield drops below "
            "Treasury-bill rates. Capital exits, USDe redemptions stress the unwind, "
            "Pendle PT-sUSDe traders mark down, Morpho sUSDe-collateral markets "
            "see liquidation thresholds tested."
        ),
        "historical": "Q2 2024 funding rates compressed materially as ETH stagnated.",
    },
    "aave_exploit": {
        "name": "Aave V3 Critical Exploit",
        "icon": "🟠",
        "epicenter": "Aave V3",
        "shock_pct": 20.0,
        "tagline": "Hypothetical: oracle manipulation drains ~20% of Aave V3 TVL.",
        "narrative": (
            "Aave is the single largest concentration of stablecoin and stETH collateral "
            "in DeFi. A successful oracle or liquidation-engine exploit propagates to "
            "GHO (Aave-collateralised stablecoin), Morpho (vaults built on top), and "
            "every major stablecoin via the post-event flight to safety."
        ),
        "historical": "No Aave-scale exploit has occurred. Cream Finance ($130M) and "
                      "Euler ($197M) provide directional reference points.",
    },
    "curve_exploit": {
        "name": "Curve 3pool Imbalance Cascade",
        "icon": "🟡",
        "epicenter": "Curve 3pool",
        "shock_pct": 30.0,
        "tagline": "July 2023 vyper exploit pattern - single-pool drain.",
        "narrative": (
            "Curve's 3pool is the base pair for hundreds of metapools. A pool drain or "
            "stablecoin leg depeg causes cascading metapool imbalances. Convex LPs eat "
            "the loss; crvUSD and any pool using 3pool LP as collateral marks down."
        ),
        "historical": "July 30, 2023 - Vyper compiler exploit drained $73M from "
                      "alETH/msETH/CRV/ETH pools via reentrancy.",
    },
}
