"""P4 的最小训练实验：选择性状态空间模型在三种任务下训练后的参照画像。
模型：h_t = A(s_t) ⊙ h_{t-1} + B u_t，A(s) = tanh(p) + a1*s（选择性、逐维）
      u_t = [x1, x2, s, c]，读出 logit_k = w_k x_k + (v_k·h_t) x_k + β_k·h_t + b_k
任务 T1：框架 f 在 t=0 由 c 给出，遇到切换事件 s=1 时翻转；目标 y_k = x_k·f（需慢变、受内容更新的共享调制）
任务 T2：目标 y_k = x_k（框架无关）
任务 T3：同 T1，但每步都由 c 重新给出当前框架（无需持续）"""
import numpy as np, sys, json
D, T, BATCH = 2, 30, 64
def sample(task, rng, n=BATCH):
    x = rng.choice([-1., 1.], size=(n, T, 2))
    s = (rng.random((n, T)) < 0.1).astype(float); s[:, 0] = 0
    f0 = rng.choice([-1., 1.], size=n)
    f = np.empty((n, T)); cur = f0.copy()
    for t in range(T):
        cur = np.where(s[:, t] == 1, -cur, cur); f[:, t] = cur
    c = np.zeros((n, T))
    if task == 'T3': c = f.copy()
    else: c[:, 0] = f0
    u = np.concatenate([x, s[..., None], c[..., None]], axis=2)
    y = x * f[..., None] if task in ('T1', 'T3') else x.copy()
    return u, (y > 0).astype(float)
def unpack(th):
    i = 0
    def take(k):
        nonlocal i; v = th[i:i+k]; i += k; return v
    p = take(D); a1 = take(D); B = take(D*4).reshape(D, 4)
    w = take(2); V = take(2*D).reshape(2, D); Bt = take(2*D).reshape(2, D); b = take(2)
    return p, a1, B, w, V, Bt, b
NP = D + D + D*4 + 2 + 2*D + 2*D + 2
def forward(th, u, h_override=None):
    p, a1, B, w, V, Bt, b = unpack(th)
    n = u.shape[0]; h = np.zeros((n, D)); logits = np.empty((n, T, 2)); H = np.empty((n, T, D))
    for t in range(T):
        A = np.tanh(p)[None] + a1[None] * u[:, t, 2:3]
        h = A * h + u[:, t] @ B.T
        if h_override is not None and t in h_override: h = h_override[t](h)
        H[:, t] = h
        x = u[:, t, :2]
        logits[:, t] = w * x + (h @ V.T) * x + h @ Bt.T + b
    return logits, H
def loss(th, u, y, lam=1e-3):
    lg, _ = forward(th, u)
    ll = np.mean(np.logaddexp(0, lg) - y * lg)
    return ll + lam * np.sum(th**2)
def train(task, seed, steps=1200):
    rng = np.random.default_rng(seed); th = rng.normal(0, 0.3, NP)
    m = np.zeros(NP); v = np.zeros(NP); lr = 0.05; eps = 1e-4
    for k in range(1, steps+1):
        u, y = sample(task, rng)
        g = np.empty(NP)
        for j in range(NP):
            e = np.zeros(NP); e[j] = eps
            g[j] = (loss(th+e, u, y) - loss(th-e, u, y)) / (2*eps)
        m = 0.9*m + 0.1*g; v = 0.999*v + 0.001*g*g
        th -= lr * (m/(1-0.9**k)) / (np.sqrt(v/(1-0.999**k)) + 1e-8)
    return th
if __name__ == '__main__':
    task, seed = sys.argv[1], int(sys.argv[2])
    th = train(task, seed)
    np.save(f'th_{task}_{seed}.npy', th)
    rng = np.random.default_rng(999); u, y = sample(task, rng, 2000)
    lg, _ = forward(th, u); acc = np.mean((lg > 0) == (y > 0.5))
    print(json.dumps({'task': task, 'seed': seed, 'acc': float(acc)}))
