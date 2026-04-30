"""
DeFi protocol dependency graph.

Each node represents a protocol, asset, or stablecoin in the DeFi ecosystem.
Each edge represents an exposure relationship: source protocol holds value in,
or depends on the integrity of, the target asset/protocol.

TVL figures are approximate ranges for the 2024-2026 cycle. Live values are
overlaid at runtime via DefiLlama where available.

Edges have:
  - exposure_usd: dollar value of the exposure
  - exposure_pct: what fraction of the source's TVL this represents
  - transmission: how much of a target's price/value shock propagates to source
                  (1.0 = full pass-through, 0.5 = partial, e.g. due to overcollateralization)
  - mechanism: human-readable description of the dependency
"""

# Node types drive the visual styling and the cascade math.
NODE_TYPES = {
    "stablecoin": {"color": "#3FB950", "shape": "dot"},
    "lst": {"color": "#58A6FF", "shape": "dot"},
    "lrt": {"color": "#A371F7", "shape": "dot"},
    "lending": {"color": "#F0883E", "shape": "square"},
    "dex": {"color": "#E3B341", "shape": "triangle"},
    "yield": {"color": "#DB61A2", "shape": "diamond"},
    "cdp": {"color": "#FF7B72", "shape": "square"},
    "restaking": {"color": "#BC8CFF", "shape": "hexagon"},
    "synthetic": {"color": "#56D4DD", "shape": "dot"},
}

PROTOCOLS = {
    # ---- Stablecoins ----
    "USDC": {
        "type": "stablecoin",
        "tvl_usd": 35_000_000_000,
        "issuer": "Circle",
        "blurb": "Fiat-backed by cash + short-dated US Treasuries held with BNY Mellon. "
                 "Most-integrated stablecoin in DeFi; depeg risk is the single largest contagion vector.",
        "defillama_slug": None,  # circulating supply
    },
    "USDT": {
        "type": "stablecoin",
        "tvl_usd": 110_000_000_000,
        "issuer": "Tether",
        "blurb": "Largest stablecoin by supply; reserves include Treasuries, BTC, gold, and secured loans. "
                 "Concentrated counterparty risk.",
    },
    "DAI": {
        "type": "stablecoin",
        "tvl_usd": 5_300_000_000,
        "issuer": "MakerDAO / Sky",
        "blurb": "MakerDAO CDP stablecoin. ~50% of backing is USDC via the PSM, "
                 "creating direct contagion if USDC depegs.",
        "defillama_slug": "makerdao",
    },
    "USDe": {
        "type": "synthetic",
        "tvl_usd": 5_500_000_000,
        "issuer": "Ethena Labs",
        "blurb": "Synthetic dollar backed by delta-neutral short ETH/BTC perpetuals + stETH collateral. "
                 "Yield-bearing via sUSDe. Vulnerable to sustained negative funding.",
        "defillama_slug": "ethena",
    },
    "FRAX": {
        "type": "stablecoin",
        "tvl_usd": 650_000_000,
        "issuer": "Frax Finance",
        "blurb": "Hybrid stablecoin, now ~100% collateralized (post-v3). Significant USDC reserve exposure.",
        "defillama_slug": "frax",
    },
    "crvUSD": {
        "type": "stablecoin",
        "tvl_usd": 110_000_000,
        "issuer": "Curve Finance",
        "blurb": "CDP stablecoin backed by ETH, wstETH, sfrxETH, WBTC via Curve's LLAMMA soft-liquidation engine.",
        "defillama_slug": "curve-dex",
    },
    "GHO": {
        "type": "stablecoin",
        "tvl_usd": 220_000_000,
        "issuer": "Aave",
        "blurb": "Aave-native stablecoin minted against Aave V3 collateral. Inherits Aave's full collateral risk.",
        "defillama_slug": "aave-v3",
    },

    # ---- LSTs ----
    "stETH": {
        "type": "lst",
        "tvl_usd": 28_000_000_000,
        "issuer": "Lido",
        "blurb": "Largest liquid staked ETH derivative. Critical collateral asset across Aave, Maker, Curve, EigenLayer. "
                 "Discount widening cascades violently.",
        "defillama_slug": "lido",
    },
    "rETH": {
        "type": "lst",
        "tvl_usd": 1_900_000_000,
        "issuer": "Rocket Pool",
        "blurb": "Decentralised ETH LST. Lower integration footprint than stETH but used in Aave, Balancer, Maker.",
        "defillama_slug": "rocket-pool",
    },

    # ---- LRTs (EigenLayer-restaked) ----
    "weETH": {
        "type": "lrt",
        "tvl_usd": 4_800_000_000,
        "issuer": "Ether.fi",
        "blurb": "Largest LRT. Wraps stETH-equivalent restaked via EigenLayer. Inherits stETH and AVS slashing risk.",
        "defillama_slug": "ether.fi",
    },
    "ezETH": {
        "type": "lrt",
        "tvl_usd": 1_400_000_000,
        "issuer": "Renzo",
        "blurb": "LRT backed by stETH restaked into EigenLayer. Documented depeg event in April 2024 from points-farming unwind.",
        "defillama_slug": "renzo",
    },
    "rsETH": {
        "type": "lrt",
        "tvl_usd": 1_100_000_000,
        "issuer": "Kelp DAO",
        "blurb": "Multi-LST LRT (stETH + ETHx). Heavy Pendle integration.",
        "defillama_slug": "kelp-dao",
    },
    "pufETH": {
        "type": "lrt",
        "tvl_usd": 800_000_000,
        "issuer": "Puffer Finance",
        "blurb": "LRT emphasising anti-slashing tech for native ETH restaking.",
        "defillama_slug": "puffer-finance",
    },

    # ---- Restaking ----
    "EigenLayer": {
        "type": "restaking",
        "tvl_usd": 12_000_000_000,
        "issuer": "EigenLabs",
        "blurb": "Restaking primitive. AVS slashing events propagate downward into every LRT.",
        "defillama_slug": "eigenlayer",
    },

    # ---- Lending ----
    "Aave V3": {
        "type": "lending",
        "tvl_usd": 22_000_000_000,
        "issuer": "Aave DAO",
        "blurb": "Largest lending market. Holds ~$5B stETH, ~$3B USDC, ~$2B USDT as collateral. "
                 "Single largest concentration of stablecoin collateral risk in DeFi.",
        "defillama_slug": "aave-v3",
    },
    "Compound V3": {
        "type": "lending",
        "tvl_usd": 2_400_000_000,
        "issuer": "Compound Labs",
        "blurb": "Isolated lending markets per base asset. Lower collateral diversity than Aave.",
        "defillama_slug": "compound-v3",
    },
    "Morpho": {
        "type": "lending",
        "tvl_usd": 4_200_000_000,
        "issuer": "Morpho Labs",
        "blurb": "Permissionless isolated lending markets. Heavy USDe/sUSDe and LRT collateral usage.",
        "defillama_slug": "morpho-blue",
    },
    "Spark": {
        "type": "lending",
        "tvl_usd": 2_800_000_000,
        "issuer": "Sky (Maker)",
        "blurb": "MakerDAO's lending arm. Native DAI, sDAI, wstETH market.",
        "defillama_slug": "spark",
    },

    # ---- DEX / AMM ----
    "Curve 3pool": {
        "type": "dex",
        "tvl_usd": 200_000_000,
        "issuer": "Curve Finance",
        "blurb": "USDC/USDT/DAI base pool. Foundation for ~80% of Curve metapools — depeg in any leg drains the others.",
    },
    "Curve stETH/ETH": {
        "type": "dex",
        "tvl_usd": 180_000_000,
        "issuer": "Curve Finance",
        "blurb": "Largest stETH liquidity venue. Imbalance signals stETH discount.",
    },
    "Uniswap V3": {
        "type": "dex",
        "tvl_usd": 4_500_000_000,
        "issuer": "Uniswap Labs",
        "blurb": "Concentrated-liquidity DEX. Massive USDC pair exposure.",
        "defillama_slug": "uniswap-v3",
    },

    # ---- Yield ----
    "Pendle": {
        "type": "yield",
        "tvl_usd": 5_800_000_000,
        "issuer": "Pendle Finance",
        "blurb": "Yield tokenisation. PT/YT priced off underlying — sUSDe and weETH PTs are concentration risks.",
        "defillama_slug": "pendle",
    },
    "Convex": {
        "type": "yield",
        "tvl_usd": 1_100_000_000,
        "issuer": "Convex Finance",
        "blurb": "Curve LP boost aggregator. Inherits all Curve pool risk.",
        "defillama_slug": "convex-finance",
    },

    # ---- CDP ----
    "MakerDAO": {
        "type": "cdp",
        "tvl_usd": 8_000_000_000,
        "issuer": "Sky",
        "blurb": "DAI issuance backbone. PSM holds large USDC reserves; vault collateral includes ETH, wstETH, RWAs.",
        "defillama_slug": "makerdao",
    },
}


# (source, target, exposure_usd, transmission, mechanism)
# Edges flow FROM holder TO held-asset / depended-on protocol.
# Cascade math: shock to target × transmission × (exposure_usd / source_tvl) → shock to source
EDGES = [
    # ---- DAI's structural USDC exposure ----
    ("DAI", "USDC", 2_400_000_000, 1.0,
     "PSM holds USDC 1:1 backing for ~45% of circulating DAI"),
    ("MakerDAO", "USDC", 2_400_000_000, 1.0,
     "PSM module — direct USDC reserve"),

    # ---- FRAX collateral ----
    ("FRAX", "USDC", 350_000_000, 0.95,
     "USDC AMO + collateral reserves"),

    # ---- Aave V3 collateral exposures ----
    ("Aave V3", "USDC", 3_100_000_000, 0.85,
     "USDC supply markets — depeg liquidates USDC-collateralised borrows"),
    ("Aave V3", "USDT", 2_200_000_000, 0.85,
     "USDT supply markets across chains"),
    ("Aave V3", "DAI", 800_000_000, 0.85,
     "DAI supply market"),
    ("Aave V3", "stETH", 5_400_000_000, 0.7,
     "Largest single collateral type — wstETH/stETH e-mode"),
    ("Aave V3", "weETH", 900_000_000, 0.7,
     "weETH e-mode collateral"),

    # ---- Compound ----
    ("Compound V3", "USDC", 1_500_000_000, 0.85,
     "Primary base asset"),

    # ---- Morpho markets ----
    ("Morpho", "USDC", 1_100_000_000, 0.85, "USDC base markets"),
    ("Morpho", "USDe", 800_000_000, 0.9, "sUSDe-collateralised markets via MEV Capital, Re7, Gauntlet"),
    ("Morpho", "weETH", 600_000_000, 0.7, "weETH/ETH leveraged loops"),

    # ---- Spark / Maker ----
    ("Spark", "DAI", 1_200_000_000, 0.95, "Native DAI lending"),
    ("Spark", "stETH", 800_000_000, 0.7, "wstETH collateral"),

    # ---- GHO inherits Aave collateral risk ----
    ("GHO", "Aave V3", 220_000_000, 1.0,
     "GHO is minted against Aave V3 collateral; an Aave-level event prices through"),

    # ---- Curve pools ----
    ("Curve 3pool", "USDC", 70_000_000, 1.0, "1/3 of pool"),
    ("Curve 3pool", "USDT", 70_000_000, 1.0, "1/3 of pool"),
    ("Curve 3pool", "DAI", 60_000_000, 1.0, "1/3 of pool"),
    ("Curve stETH/ETH", "stETH", 90_000_000, 1.0, "Half of pool"),
    ("Convex", "Curve 3pool", 80_000_000, 1.0, "Boosted 3pool LP"),
    ("Convex", "Curve stETH/ETH", 70_000_000, 1.0, "Boosted stETH/ETH LP"),

    # ---- Uniswap ----
    ("Uniswap V3", "USDC", 1_800_000_000, 0.6,
     "ETH/USDC + USDC/USDT pairs; partial LP loss on depeg"),

    # ---- crvUSD ----
    ("crvUSD", "stETH", 30_000_000, 0.6, "wstETH LLAMMA market"),

    # ---- USDe Ethena ----
    ("USDe", "stETH", 1_400_000_000, 0.5,
     "stETH portion of delta-neutral collateral"),
    ("USDe", "USDC", 800_000_000, 0.6,
     "USDC custody reserve at OES partners"),

    # ---- LRTs depend on stETH + EigenLayer ----
    ("weETH", "stETH", 4_300_000_000, 0.95,
     "Underlying restaked LST exposure"),
    ("weETH", "EigenLayer", 4_800_000_000, 0.4,
     "AVS slashing exposure on full weETH supply"),
    ("ezETH", "stETH", 1_300_000_000, 0.95, "Underlying LST"),
    ("ezETH", "EigenLayer", 1_400_000_000, 0.4, "AVS slashing risk"),
    ("rsETH", "stETH", 1_000_000_000, 0.95, "Underlying LST"),
    ("rsETH", "EigenLayer", 1_100_000_000, 0.4, "AVS slashing risk"),
    ("pufETH", "EigenLayer", 800_000_000, 0.4, "Native restaked ETH AVS exposure"),

    # ---- EigenLayer holds LSTs ----
    ("EigenLayer", "stETH", 7_000_000_000, 0.95, "stETH is the largest restaked LST"),

    # ---- Pendle PT exposures ----
    ("Pendle", "USDe", 1_600_000_000, 0.95,
     "PT-sUSDe / PT-USDe markets"),
    ("Pendle", "weETH", 1_200_000_000, 0.95, "PT-weETH dominant LRT yield market"),
    ("Pendle", "stETH", 600_000_000, 0.95, "PT-stETH"),
    ("Pendle", "Aave V3", 350_000_000, 0.85,
     "PT-aUSDC / PT-aaveUSDS markets — Aave-receipt-token tokenised yield"),

    # ---- Spark structurally is MakerDAO ----
    ("Spark", "MakerDAO", 2_800_000_000, 1.0,
     "Spark is operated by Sky (Maker) — full governance and treasury dependence"),

    # ---- Morpho curator vaults that route into Aave for liquidity floor ----
    ("Morpho", "Aave V3", 250_000_000, 0.6,
     "MetaMorpho curator vaults using Aave as underlying liquidity tier"),

    # ---- Convex direct exposure to Curve as a protocol ----
    ("Convex", "Curve 3pool", 220_000_000, 1.0,
     "Boosted CRV emissions on 3pool LP — full pass-through on pool drain"),
]


def get_node_color(node_id: str) -> str:
    p = PROTOCOLS.get(node_id, {})
    return NODE_TYPES.get(p.get("type"), {"color": "#888"})["color"]


def get_node_shape(node_id: str) -> str:
    p = PROTOCOLS.get(node_id, {})
    return NODE_TYPES.get(p.get("type"), {"shape": "dot"})["shape"]
