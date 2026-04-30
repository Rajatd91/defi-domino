"""
Live TVL overlay from DefiLlama.

The static TVL numbers in data/protocols.py are the structural baseline; this
module pulls live values to refresh the display when the network is available.
We cache results per-session and silently fall back to baseline TVL on error.
"""

from __future__ import annotations

import time
from typing import Optional

import requests

DEFILLAMA_PROTOCOL_URL = "https://api.llama.fi/protocol/{slug}"
TIMEOUT_S = 4


def fetch_live_tvl(slug: Optional[str]) -> Optional[float]:
    if not slug:
        return None
    try:
        r = requests.get(DEFILLAMA_PROTOCOL_URL.format(slug=slug), timeout=TIMEOUT_S)
        if r.status_code != 200:
            return None
        data = r.json()
        # currentChainTvls is a dict {chain: tvl}, sum all
        chain_tvls = data.get("currentChainTvls") or {}
        # Filter out staking/treasury double-counts when present
        excluded = {"staking", "pool2", "treasury", "borrowed", "vesting"}
        total = sum(v for k, v in chain_tvls.items() if k.lower() not in excluded and isinstance(v, (int, float)))
        return float(total) if total > 0 else None
    except Exception:
        return None


def fetch_all_live(protocols: dict, max_protocols: int = 12) -> dict[str, float]:
    """Fetch live TVL for protocols that have a defillama_slug. Bounded for hackathon speed."""
    out: dict[str, float] = {}
    fetched = 0
    for name, meta in protocols.items():
        if fetched >= max_protocols:
            break
        slug = meta.get("defillama_slug")
        if not slug:
            continue
        tvl = fetch_live_tvl(slug)
        if tvl:
            out[name] = tvl
            fetched += 1
    return out
