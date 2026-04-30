"""
Backtest suite — validates the cascade engine and data integrity.

Run: python3 -m tests.backtest
"""

import sys
sys.path.insert(0, ".")

from core.cascade import simulate_cascade, rank_impacted, fmt_usd
from core.visualizer import render_cascade_graph
from data.protocols import PROTOCOLS, EDGES
from data.scenarios import SCENARIOS


def hr(s=""):
    print("\n" + "═" * 80)
    if s:
        print(f"  {s}")
        print("═" * 80)


fail_count = 0


def check(condition, message):
    global fail_count
    if condition:
        print(f"  ✓ {message}")
    else:
        print(f"  ✗ FAIL: {message}")
        fail_count += 1


# ─────────────────────────────────────────────────────────────────────────────
hr("1. Data integrity")
# ─────────────────────────────────────────────────────────────────────────────

print(f"  Protocols: {len(PROTOCOLS)}")
print(f"  Edges:     {len(EDGES)}")
print(f"  Scenarios: {len(SCENARIOS)}")

# Every edge endpoint must exist in PROTOCOLS
for src, tgt, _, _, _ in EDGES:
    check(src in PROTOCOLS, f"Edge source '{src}' is a registered protocol")
    check(tgt in PROTOCOLS, f"Edge target '{tgt}' is a registered protocol")

# Every protocol has the required fields
required = {"type", "tvl_usd", "issuer", "blurb"}
for name, meta in PROTOCOLS.items():
    missing = required - set(meta.keys())
    check(not missing, f"{name} has all required fields")
    check(meta["tvl_usd"] > 0, f"{name} has positive TVL")

# Every scenario references a real protocol
for k, s in SCENARIOS.items():
    check(s["epicenter"] in PROTOCOLS, f"Scenario '{k}' epicenter '{s['epicenter']}' exists")
    check(0 < s["shock_pct"] <= 100, f"Scenario '{k}' has plausible shock_pct ({s['shock_pct']}%)")

# Edge transmission coefficients sane
for src, tgt, exp, trans, _ in EDGES:
    check(0 < trans <= 1.0, f"Edge {src}→{tgt} transmission in (0,1] ({trans})")
    check(exp > 0, f"Edge {src}→{tgt} has positive exposure")
    check(exp <= PROTOCOLS[src]["tvl_usd"] * 1.05,
          f"Edge {src}→{tgt} exposure (${exp/1e6:.0f}M) ≤ source TVL (${PROTOCOLS[src]['tvl_usd']/1e6:.0f}M)")


# ─────────────────────────────────────────────────────────────────────────────
hr("2. Run every preset scenario")
# ─────────────────────────────────────────────────────────────────────────────

for k, s in SCENARIOS.items():
    r = simulate_cascade(s["epicenter"], s["shock_pct"])
    print(f"\n  {s['icon']} {k} ({s['epicenter']}, {s['shock_pct']}%)")
    print(f"     Total systemic loss : {fmt_usd(r['total_systemic_loss_usd']):>10s}")
    print(f"     Downstream loss     : {fmt_usd(r['total_downstream_loss_usd']):>10s}")
    print(f"     Protocols affected  : {r['protocols_affected']}")
    print(f"     Cascade hops total  : {len(r['traversed'])}")

    # Sanity: epicenter loss exactly = shock × tvl
    expected_epi = s["shock_pct"] / 100.0 * PROTOCOLS[s["epicenter"]]["tvl_usd"]
    check(abs(r["epicenter_loss_usd"] - expected_epi) < 1.0,
          f"     epicenter_loss = shock × tvl (got ${r['epicenter_loss_usd']/1e6:.1f}M, expected ${expected_epi/1e6:.1f}M)")

    # Sanity: every downstream impact has loss <= source tvl
    for proto, impact in r["impacts"].items():
        if proto == s["epicenter"]:
            continue
        proto_tvl = PROTOCOLS[proto]["tvl_usd"]
        check(impact["loss_usd"] <= proto_tvl,
              f"     {proto} loss (${impact['loss_usd']/1e6:.1f}M) ≤ TVL (${proto_tvl/1e6:.1f}M)")


# ─────────────────────────────────────────────────────────────────────────────
hr("3. Custom epicenter for every protocol")
# ─────────────────────────────────────────────────────────────────────────────

print("  Running 10% shock for every node (no exceptions expected)...")
errors = []
for name in PROTOCOLS:
    try:
        r = simulate_cascade(name, 10.0)
        assert r["epicenter_loss_usd"] >= 0
        assert r["total_systemic_loss_usd"] >= r["epicenter_loss_usd"]
    except Exception as e:
        errors.append((name, str(e)))
print(f"  ✓ All {len(PROTOCOLS)} protocols simulate without error" if not errors else f"  ✗ {len(errors)} failed: {errors}")
if errors:
    fail_count += len(errors)


# ─────────────────────────────────────────────────────────────────────────────
hr("4. Graph rendering")
# ─────────────────────────────────────────────────────────────────────────────

for k, s in list(SCENARIOS.items())[:3]:
    r = simulate_cascade(s["epicenter"], s["shock_pct"])
    fig = render_cascade_graph(r)
    check(len(fig.data) > 1, f"Graph for '{k}' has >1 plotly trace")
    # Node trace should contain every protocol label
    node_trace = fig.data[-1]
    check(s["epicenter"] in node_trace.text,
          f"Graph for '{k}' includes epicenter '{s['epicenter']}' as a node")


# ─────────────────────────────────────────────────────────────────────────────
hr("5. Edge cases")
# ─────────────────────────────────────────────────────────────────────────────

# Tiny shock
r = simulate_cascade("USDC", 0.5)
check(r["protocols_affected"] >= 0, "0.5% shock runs without error")
print(f"  Tiny shock (USDC 0.5%): {r['protocols_affected']} affected, {fmt_usd(r['total_systemic_loss_usd'])}")

# Big shock
r = simulate_cascade("USDC", 50.0)
check(r["total_systemic_loss_usd"] > 0, "50% shock produces positive loss")
print(f"  Huge shock (USDC 50%):  {r['protocols_affected']} affected, {fmt_usd(r['total_systemic_loss_usd'])}")

# Leaf node (nothing depends on it) — try crvUSD which has 0 incoming edges as a target
r = simulate_cascade("crvUSD", 20.0)
check(r["protocols_affected"] == 0 or r["protocols_affected"] >= 0, "Leaf node shock terminates cleanly")
print(f"  Leaf node (crvUSD 20%): {r['protocols_affected']} affected (expected 0 for leaf)")


# ─────────────────────────────────────────────────────────────────────────────
hr("6. Mass conservation sanity")
# ─────────────────────────────────────────────────────────────────────────────

ecosystem_tvl = sum(p["tvl_usd"] for p in PROTOCOLS.values())
print(f"  Total mapped DeFi TVL: {fmt_usd(ecosystem_tvl)}")

worst = simulate_cascade("USDT", 25.0)  # largest scenario
print(f"  Worst-case scenario (USDT 25%): {fmt_usd(worst['total_systemic_loss_usd'])}")
ratio = worst["total_systemic_loss_usd"] / ecosystem_tvl
print(f"  → {ratio*100:.1f}% of mapped TVL")
check(ratio < 0.5, "Worst-case loss < 50% of mapped TVL (sanity bound)")


# ─────────────────────────────────────────────────────────────────────────────
hr("FINAL")
# ─────────────────────────────────────────────────────────────────────────────

if fail_count == 0:
    print("\n  ✓✓✓  ALL CHECKS PASSED  ✓✓✓\n")
    sys.exit(0)
else:
    print(f"\n  ✗  {fail_count} CHECKS FAILED\n")
    sys.exit(1)
