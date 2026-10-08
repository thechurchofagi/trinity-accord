#!/usr/bin/env python3
"""Small numerical checks of explicit two-port thought-experiment models.

No neural data, consciousness labels, or fitted parameters are used.
Python standard library only. Run: python check_models.py
"""
from __future__ import annotations
import json
import math
from pathlib import Path
from typing import Callable

Matrix = tuple[tuple[float, float], tuple[float, float]]
Vector = tuple[float, float]


def mv(a: Matrix, x: Vector) -> Vector:
    return (a[0][0]*x[0]+a[0][1]*x[1], a[1][0]*x[0]+a[1][1]*x[1])


def mm(a: Matrix, b: Matrix) -> Matrix:
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(2))
                       for j in range(2)) for i in range(2))  # type: ignore[return-value]


def transpose(a: Matrix) -> Matrix:
    return ((a[0][0], a[1][0]), (a[0][1], a[1][1]))


def dist(a: Matrix, b: Matrix) -> float:
    return max(abs(a[i][j]-b[i][j]) for i in range(2) for j in range(2))


def det(a: Matrix) -> float:
    return a[0][0]*a[1][1]-a[0][1]*a[1][0]


def validate(g: float, mu: float, t: float) -> None:
    if not all(math.isfinite(v) and v >= 0 for v in (g, mu, t)):
        raise ValueError('Rates and elapsed time must be finite and nonnegative.')


def averaging(g: float, mu: float, t: float) -> Matrix:
    validate(g, mu, t)
    q, e = math.exp(-2*g*t), math.exp(-mu*t)
    return ((e*(1+q)/2, e*(1-q)/2),
            (e*(1-q)/2, e*(1+q)/2))


def rotating(g: float, mu: float, t: float) -> Matrix:
    validate(g, mu, t)
    e, c, s = math.exp(-mu*t), math.cos(g*t), math.sin(g*t)
    return ((e*c, e*s), (-e*s, e*c))


def rk4_matrix(a: Matrix, t: float, steps: int = 1600) -> Matrix:
    """Independent ODE integration of the two initial basis vectors."""
    if steps < 1 or t < 0:
        raise ValueError('Invalid integration settings.')
    h = t/steps
    columns: list[Vector] = []
    def add(x: Vector, k: Vector, s: float) -> Vector:
        return (x[0]+s*k[0], x[1]+s*k[1])
    for initial in [(1., 0.), (0., 1.)]:
        z = initial
        for _ in range(steps):
            k1 = mv(a, z)
            k2 = mv(a, add(z, k1, h/2))
            k3 = mv(a, add(z, k2, h/2))
            k4 = mv(a, add(z, k3, h))
            z = tuple(z[i]+h*(k1[i]+2*k2[i]+2*k3[i]+k4[i])/6
                      for i in range(2))  # type: ignore[assignment]
        columns.append(z)
    return ((columns[0][0], columns[1][0]),
            (columns[0][1], columns[1][1]))


def run() -> dict:
    checks: list[dict] = []
    def check(name: str, condition: bool, **details: object) -> None:
        checks.append(dict(name=name, passed=bool(condition), **details))
        if not condition:
            raise AssertionError(f'Check failed: {name}: {details}')
    identity: Matrix = ((1., 0.), (0., 1.))
    c = 1/math.sqrt(2)
    hadamard: Matrix = ((c, c), (c, -c))
    maxerr = 0.
    cases = 0
    for g in [0., .05, .5, 2.]:
        for mu in [0., .1]:
            for t in [.1, 1., 2.]:
                for f, a in [
                    (averaging, ((-mu-g, g), (g, -mu-g))),
                    (rotating, ((-mu, g), (-g, -mu)))
                ]:
                    maxerr = max(maxerr, dist(f(g, mu, t), rk4_matrix(a, t)))
                    cases += 1
    check('closed_forms_vs_independent_RK4', maxerr < 1e-9,
          numerical_cases=cases, max_absolute_error=maxerr)
    grid = [(g, mu, t) for g in [.01,.1,.5,1.,2.]
            for mu in [0.,.1] for t in [.1,.5,1.,2.]]
    eigenerr = max(dist(mm(mm(hadamard, averaging(g,mu,t)),hadamard),
                        ((math.exp(-mu*t),0.),(0.,math.exp(-(mu+2*g)*t))))
                   for g,mu,t in grid)
    check('mean_and_contrast_modes', eigenerr < 1e-12, max_error=eigenerr)
    tradeerr = max(abs(2*math.exp(mu*t)*averaging(g,mu,t)[0][1]
                       +math.exp(-2*g*t)-1) for g,mu,t in grid)
    check('averaging_only_cross_gain_contrast_identity', tradeerr < 1e-12)
    ortherr = max(dist(mm(transpose(rotating(g,mu,t)),rotating(g,mu,t)),
                      ((math.exp(-2*mu*t),0.),(0.,math.exp(-2*mu*t))))
                 for g,mu,t in grid)
    check('rotation_preserves_joint_distinctions_up_to_common_leak', ortherr < 1e-12)
    check('finite_time_averaging_is_invertible',
          all(det(averaging(g,mu,t)) > 0 for g,mu,t in grid),
          caveat='No exact finite-time information erasure in the ideal real-valued model.')
    g, mu, t, scale = .5, .1, 1., 1000.
    check('uniform_rate_scaling_compensated_horizon',
          dist(averaging(g,mu,t), averaging(g/scale,mu/scale,t*scale)) < 1e-12)
    q_old = math.exp(-2*g/mu)
    q_link_only_at_memory_time = math.exp(-2*(g/scale)/mu)
    check('link_only_slowing_changes_dimensionless_ratio',
          abs(q_old-q_link_only_at_memory_time) > .5,
          original_q_at_t_1_over_mu=q_old, link_only_q_at_t_1_over_mu=q_link_only_at_memory_time,
          link_only_cross_gain_at_t_1_over_mu=(1-q_link_only_at_memory_time)/2)
    theta = math.pi/4
    r = rotating(theta, 0., 1.)
    a = averaging(theta, 0., 1.)
    check('same_cross_link_graph_and_magnitude_different_retention',
          abs(det(r)-1)<1e-12 and det(a)<.3,
          rotation_det=det(r), averaging_det=det(a),
          scope='Same unsigned bidirectional adjacency and cross-gain g, not same mechanisms.')
    g, t, eta = .5, 1., .1
    z1, z2 = (1.,-1.), (-1.,1.)
    vals = [mv(averaging(g,0.,t),z) for z in [z1,z2]]
    check('same_mean_macrostate_hides_distinct_whole_states',
          abs(sum(vals[0]))<1e-12 and abs(sum(vals[1]))<1e-12 and vals[0]!=vals[1])
    endpoint = rotating(math.pi,0.,1.)
    interior = rotating(math.pi,0.,.5)
    check('endpoint_zero_does_not_mean_no_cross_influence_in_window',
          abs(endpoint[0][1])<1e-12 and abs(interior[0][1])>.99)
    # An explicit operational tolerance, never a consciousness or subject threshold.
    bound = -math.log(1-2*eta)/(2*t)
    check('declared_tolerance_boundary_depends_on_horizon',
          abs((1-math.exp(-2*bound*t))/2-eta)<1e-12,
          eta=eta, t=t, g_boundary=bound,
          g_boundary_at_10t=bound/10)
    table = [dict(gT=v, normalized_cross=(1-math.exp(-2*v))/2,
                  normalized_contrast=math.exp(-2*v),
                  rotation_min_singular_normalized=1.) for v in [.01,.1,1.,3.]]
    return dict(status='all listed checks passed',
                interpretation='Numerical verification of stipulated equations only; not consciousness experiments.',
                checks=checks, table=table,
                analytic_limits={'lim_g_to_0_then_T_to_infty_of_q':1,
                                 'lim_T_to_infty_then_g_to_0_of_q':0,
                                 'scope':'mu=0, g approaches 0 from above; analytic, not numerical proof.'})

if __name__ == '__main__':
    results = run()
    output = Path(__file__).with_name('MODEL_RESULTS.json')
    output.write_text(json.dumps(results, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps(results, indent=2, ensure_ascii=False))
