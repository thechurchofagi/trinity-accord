"""ERF 修订稿附录 A 核验程序（仅用 Python 标准库）。
核验内容：三位异或控制器与慢变对照系统的内在持续与滞后调制；
三种位点传递同质系统的内在持续画像；150 号环全局奇偶守恒。"""
import itertools, random
H = 12

def A(st, _):                      # 三位异或控制器 (x, y, r)
    x, y, r = st
    return [x ^ r, y ^ r, x ^ y]

def B(st, inp):                    # 慢变对照系统 (x, y, r)，输入 (u, v)
    x, y, r = st; u, v = inp
    return [u ^ r, v ^ r, r ^ (x & y)]

def ring(rule, n):
    def f(st, _=None):
        if rule == 90:
            return [st[i-1] ^ st[(i+1) % n] for i in range(n)]
        return [st[i-1] ^ st[i] ^ st[(i+1) % n] for i in range(n)]
    return f

def torus(n):
    def f(st, _=None):
        g = lambda i, j: st[(i % n) * n + (j % n)]
        return [g(i-1, j) ^ g(i+1, j) ^ g(i, j-1) ^ g(i, j+1) for i in range(n) for j in range(n)]
    return f

def intrinsic_persistence(step, site, states):
    """翻转 site，其余位点轨迹固定为自然值；返回各滞后 s=1..H 上是否仍有差异（取上确界）。"""
    prof = [0] * H
    for s0, inp in states:
        nat = [list(s0)]
        for t in range(H):
            nat.append(step(nat[-1], inp[t]))
        z = 1 - s0[site]
        for t in range(H):
            cur = list(nat[t]); cur[site] = z
            z = step(cur, inp[t])[site]
            if z != nat[t+1][site]:
                prof[t] = 1
    return prof

def four_term_norm(o):
    """o[(r,a)] 为确定性输出；返回 1/2 ||K^0(1)-K^0(0)-K^1(1)+K^1(0)||_1。"""
    D = {}
    for key, sgn in {(0, 1): 1, (0, 0): -1, (1, 1): -1, (1, 0): 1}.items():
        D[o[key]] = D.get(o[key], 0) + sgn
    return 0.5 * sum(abs(v) for v in D.values())

def lagged_modulation(step, rsite, run, states):
    prof = []
    for s in range(1, H):
        best = 0
        for s0, inp in states:
            o = {}
            for rv in (0, 1):
                for a in (0, 1):
                    st = list(s0); st[rsite] = rv
                    for t in range(s):
                        st = step(st, inp[t])
                    o[(rv, a)] = run(st, inp[s], a)
            best = max(best, four_term_norm(o))
        prof.append(best)
    return prof

inits = list(itertools.product([0, 1], repeat=3))
SA = [(s, [None] * H) for s in inits]
seqs = list(itertools.product(list(itertools.product([0, 1], repeat=2)), repeat=4))
SB = [(s, list(q) + [q[-1]] * (H - 4)) for s in inits for q in seqs]

print("三位控制器  内在持续 x:", intrinsic_persistence(A, 0, SA))
print("三位控制器  内在持续 r:", intrinsic_persistence(A, 2, SA))
print("三位控制器  m_x(s):", lagged_modulation(A, 2, lambda st, i, a: A([a, st[1], st[2]], i)[0], SA))
print("慢变系统    内在持续 x:", intrinsic_persistence(B, 0, SB))
print("慢变系统    内在持续 r:", intrinsic_persistence(B, 2, SB))
print("慢变系统    m_x(s):", lagged_modulation(B, 2, lambda st, i, a: B(st, (a, i[1]))[0], SB))

random.seed(0)
for name, f, N in [("90 号环 n=32", ring(90, 32), 32), ("150 号环 n=32", ring(150, 32), 32), ("8x8 异或环面", torus(8), 64)]:
    S = [(tuple(random.randint(0, 1) for _ in range(N)), [None] * H) for _ in range(300)]
    profs = {tuple(intrinsic_persistence(f, z, S)) for z in range(N)}
    print(f"{name}: 不同画像数 = {len(profs)}，画像 = {list(profs)[0]}")

random.seed(1); f = ring(150, 32); ok = True
for _ in range(500):
    st = [random.randint(0, 1) for _ in range(32)]; p = sum(st) % 2
    for _ in range(12):
        st = f(st); ok &= (sum(st) % 2 == p)
print("150 号环全局奇偶守恒:", ok)
