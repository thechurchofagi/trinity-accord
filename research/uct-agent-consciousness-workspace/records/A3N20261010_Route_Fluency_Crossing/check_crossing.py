"""Exact finite checks for A3N. Elementary enumeration; no empirical inference."""
from itertools import product
import json

cells = list(product((0, 1), repeat=2))  # (R, L_kin)

def route(r, l):
    return r

def fluency(r, l):
    return l

# Minimal logical installation: assistance is used only for 01 and
# perturbation only for 10.  Signatures are deliberately distinct.
installation = {
    (0, 0): {"assist": 0, "perturb": 0, "signature": "baseline-low"},
    (0, 1): {"assist": 1, "perturb": 0, "signature": "guided-novel"},
    (1, 0): {"assist": 0, "perturb": 1, "signature": "perturbed-retained"},
    (1, 1): {"assist": 0, "perturb": 0, "signature": "baseline-high"},
}
assert len({v["signature"] for v in installation.values()}) == 4

# With one unique auxiliary signature per cell, a nuisance-only lookup D(I)
# fits every possible observed binary endpoint table.
tables = list(product((0, 1), repeat=4))
fits_by_aux_only = 0
for table in tables:
    d = {installation[cell]["signature"]: z for cell, z in zip(cells, table)}
    fitted = tuple(d[installation[cell]["signature"]] for cell in cells)
    fits_by_aux_only += fitted == table
assert fits_by_aux_only == 16

# Replicated-mechanism theorem in the explicitly restricted XOR nuisance class:
# Z(R,L,k)=B(R,L) xor d(k).  Invariance over k=0,1 forces d(0)=d(1).
models = []
for base in tables:
    for d0, d1 in product((0, 1), repeat=2):
        obs = {(r, l, k): base[i] ^ (d0 if k == 0 else d1)
               for i, (r, l) in enumerate(cells) for k in (0, 1)}
        invariant = all(obs[r, l, 0] == obs[r, l, 1] for r, l in cells)
        models.append((base, d0, d1, invariant))
assert len(models) == 64
assert sum(m[3] for m in models) == 32
assert all((d0 == d1) == inv for _, d0, d1, inv in models)
unique_invariant_tables = {
    tuple(base[i] ^ d0 for i in range(4))
    for base, d0, d1, inv in models if inv
}
assert len(unique_invariant_tables) == 16

route_table = tuple(route(*c) for c in cells)
fluency_table = tuple(fluency(*c) for c in cells)
assert route_table == (0, 0, 1, 1)
assert fluency_table == (0, 1, 0, 1)
assert route_table != fluency_table

result = {
    "schema": "uct-a3n-exact-results/1",
    "result_version": "A3N-EXACT-v0.1.0",
    "cell_order": [list(c) for c in cells],
    "installation": {f"{r}{l}": v for (r, l), v in installation.items()},
    "binary_endpoint_tables": len(tables),
    "tables_fitted_by_unique_auxiliary_signature_only": fits_by_aux_only,
    "replicated_xor_models": len(models),
    "replicated_xor_models_invariant_across_mechanism": sum(m[3] for m in models),
    "invariance_equivalent_to_constant_xor_direct_effect": True,
    "unique_invariant_observed_tables": len(unique_invariant_tables),
    "pure_route_table": list(route_table),
    "pure_external_fluency_table": list(fluency_table),
    "interpretive_limit": (
        "Replicated-mechanism invariance removes only the declared mechanism-varying "
        "XOR direct effect. It does not exclude constant, interactive, unmeasured, or "
        "semantically misoriented direct paths, and it does not prove actual installation."
    ),
}
print(json.dumps(result, indent=2))
