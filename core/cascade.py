"""
Cascade simulation engine.

Given an epicenter shock, propagate the price impact across the dependency graph
and compute the dollar value-at-risk at each downstream protocol.

Math (per node, per edge):
    downstream_shock = upstream_shock × edge.transmission × (edge.exposure_usd / source.tvl)
    downstream_loss_usd = downstream_shock × source.tvl

We propagate via BFS with damping: each hop halves transmission strength to avoid
runaway cycles, and we cap recursion depth at 4 hops (enough for stETH→LRT→Pendle→Morpho).
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Iterable

from data.protocols import EDGES, PROTOCOLS


def _build_reverse_index() -> dict[str, list[tuple[str, float, float, str]]]:
    """For each target node, list (source, exposure_usd, transmission, mechanism)."""
    rev: dict[str, list[tuple[str, float, float, str]]] = defaultdict(list)
    for src, tgt, exp, trans, mech in EDGES:
        rev[tgt].append((src, exp, trans, mech))
    return rev


REVERSE_EDGES = _build_reverse_index()


def simulate_cascade(
    epicenter: str,
    shock_pct: float,
    max_depth: int = 4,
    damping: float = 0.85,
) -> dict:
    """
    Run a cascade from `epicenter` with a `shock_pct` % drop in value.

    Returns a dict containing:
        - impacts: {node: {"shock_pct": float, "loss_usd": float, "depth": int, "paths": [...]}}
        - paths: list of (source, target, mechanism, propagated_shock_pct) edges traversed
        - total_loss_usd: sum of all downstream losses
    """
    if epicenter not in PROTOCOLS:
        raise ValueError(f"Unknown protocol: {epicenter}")

    impacts: dict[str, dict] = {
        epicenter: {
            "shock_pct": shock_pct,
            "loss_usd": shock_pct / 100.0 * PROTOCOLS[epicenter]["tvl_usd"],
            "depth": 0,
            "incoming_paths": [],
        }
    }
    traversed: list[dict] = []

    # BFS frontier: (current_node, current_shock_pct, current_depth)
    frontier: deque[tuple[str, float, int]] = deque([(epicenter, shock_pct, 0)])
    visited_at_depth: dict[str, int] = {epicenter: 0}

    while frontier:
        node, node_shock, depth = frontier.popleft()
        if depth >= max_depth:
            continue

        # Find every protocol that holds exposure to `node`
        for src, exposure_usd, transmission, mechanism in REVERSE_EDGES.get(node, []):
            src_tvl = PROTOCOLS[src]["tvl_usd"]
            if src_tvl <= 0:
                continue

            exposure_ratio = exposure_usd / src_tvl
            propagated = node_shock * transmission * exposure_ratio * (damping ** depth)

            # Skip vanishingly small impacts to keep the graph readable
            if propagated < 0.05:
                continue

            loss_usd = propagated / 100.0 * src_tvl

            existing = impacts.get(src)
            if existing is None or propagated > existing["shock_pct"]:
                impacts[src] = {
                    "shock_pct": propagated,
                    "loss_usd": loss_usd,
                    "depth": depth + 1,
                    "incoming_paths": (existing["incoming_paths"] if existing else []) + [
                        {"from": node, "via": mechanism, "shock_pct": propagated}
                    ],
                }
            else:
                existing["incoming_paths"].append(
                    {"from": node, "via": mechanism, "shock_pct": propagated}
                )

            traversed.append({
                "source": node,
                "target": src,
                "mechanism": mechanism,
                "shock_pct": propagated,
                "loss_usd": loss_usd,
                "depth": depth + 1,
            })

            # Re-queue the source so its dependents can also be impacted
            if src not in visited_at_depth or visited_at_depth[src] > depth + 1:
                visited_at_depth[src] = depth + 1
                frontier.append((src, propagated, depth + 1))

    total_loss = sum(v["loss_usd"] for k, v in impacts.items() if k != epicenter)

    return {
        "epicenter": epicenter,
        "epicenter_shock_pct": shock_pct,
        "epicenter_loss_usd": impacts[epicenter]["loss_usd"],
        "impacts": impacts,
        "traversed": traversed,
        "total_downstream_loss_usd": total_loss,
        "total_systemic_loss_usd": total_loss + impacts[epicenter]["loss_usd"],
        "protocols_affected": len(impacts) - 1,
    }


def rank_impacted(result: dict, top_n: int = 12) -> list[tuple[str, dict]]:
    """Return impacted protocols sorted by dollar loss, excluding epicenter."""
    items = [(k, v) for k, v in result["impacts"].items() if k != result["epicenter"]]
    items.sort(key=lambda x: x[1]["loss_usd"], reverse=True)
    return items[:top_n]


def fmt_usd(amount: float) -> str:
    if amount >= 1_000_000_000:
        return f"${amount/1_000_000_000:.2f}B"
    if amount >= 1_000_000:
        return f"${amount/1_000_000:.1f}M"
    if amount >= 1_000:
        return f"${amount/1_000:.0f}K"
    return f"${amount:.0f}"
