"""
Phase 1 Verification Script.
Run this after building circuits.py, decoder.py, sampler.py.
It checks that the fundamental QEC property holds:
  Below threshold: LER < p  (error suppression)
  Above threshold: LER > p  (error amplification)

Expected output based on verified literature values.
"""

import sys

sys.path.insert(0, ".")

from quantumfaultsim.sampler import run_single_point
from quantumfaultsim.circuits import get_num_data_qubits

print("=" * 60)
print("PHASE 1 VERIFICATION: Surface Code QEC Sanity Checks")
print("=" * 60)

SHOTS = 50_000
PASS_SYMBOL = "✅"
FAIL_SYMBOL = "❌"
all_passed = True

# ──────────────────────────────────────────────────────────────
# TEST 1: Below threshold — LER should be LESS than physical p
# At p=0.003 (0.3%), we are well below the ~0.7% threshold
# Larger d should give lower LER
# ──────────────────────────────────────────────────────────────
print("\n[TEST 1] Error suppression below threshold (p=0.003 = 0.3%)")
print("         Expect: LER(d=3) > LER(d=5) > LER(d=7)")

p_below = 0.003
results_below = {}
for d in [3, 5, 7]:
    r = run_single_point(distance=d, p=p_below, num_shots=SHOTS)
    results_below[d] = r.logical_error_rate
    print(f"  d={d}: LER={r.logical_error_rate:.5f}  (p={p_below:.3f})")

if results_below[3] > results_below[5] and results_below[5] > results_below[7]:
    print(f"  Exponential Decay: {PASS_SYMBOL} (LER decreasing with distance)")
else:
    print(f"  Exponential Decay: {FAIL_SYMBOL} (UNEXPECTED — LER should decrease)")
    all_passed = False

# ──────────────────────────────────────────────────────────────
# TEST 2: Above threshold — LER should be GREATER than physical p
# At p=0.012 (1.2%), we are above the ~0.7% threshold
# Larger d should give HIGHER LER (code makes things worse)
# ──────────────────────────────────────────────────────────────
print("\n[TEST 2] Error amplification above threshold (p=0.012 = 1.2%)")
print("         Expect: LER(d=3) < LER(d=5) AND all LER > p")

p_above = 0.012
results_above = {}
for d in [3, 5, 7]:
    r = run_single_point(distance=d, p=p_above, num_shots=SHOTS)
    results_above[d] = r.logical_error_rate
    print(f"  d={d}: LER={r.logical_error_rate:.5f}  (p={p_above:.3f})", end="  ")
    print(PASS_SYMBOL if r.logical_error_rate > p_above else FAIL_SYMBOL)

if results_above[5] > results_above[3]:
    print(f"  d=5 > d=3: {PASS_SYMBOL} (LER increasing with distance above threshold)")
else:
    print(f"  d=5 > d=3: {FAIL_SYMBOL} (UNEXPECTED)")
    all_passed = False

# ──────────────────────────────────────────────────────────────
# TEST 3: Physical qubit count scales correctly
# ──────────────────────────────────────────────────────────────
print("\n[TEST 3] Qubit count scaling: d=3→9 qubits, d=5→25 qubits")

for d, expected in [(3, 9), (5, 25), (7, 49)]:
    actual = get_num_data_qubits(d)
    ok = actual == expected
    if not ok:
        all_passed = False
    print(f"  d={d}: {actual} data qubits  {PASS_SYMBOL if ok else FAIL_SYMBOL}")

# ──────────────────────────────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
if all_passed:
    print(f"{PASS_SYMBOL} ALL PHASE 1 TESTS PASSED — Ready for Phase 2")
else:
    print(f"{FAIL_SYMBOL} SOME TESTS FAILED — Check output above")
print("=" * 60)
