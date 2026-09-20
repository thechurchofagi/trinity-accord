import numpy as np, json
from train import *
T0 = 5; LAGS = [1, 5, 10, 20]
def measure(task, seed):
    th = np.load(f'th_{task}_{seed}.npy'); p, a1, B, w, V, Bt, b = unpack(th)
    rng = np.random.default_rng(123); u, _ = sample(task, rng, 1000)
    u[:, T0:T0+max(LAGS)+1, 2] = 0          # 测量窗口内不出现切换事件，便于比较持续
    if task == 'T3': u[:, T0+1:, 3] = u[:, T0:T0+1, 3]   # T3：窗口内框架输入保持不变
    u_alt = u.copy(); u_alt[:, 0, 3] *= -1
    if task == 'T3': u_alt[:, :, 3] *= -1; u_alt[:, 0, 3] = u[:, 0, 3] * -1
    _, Hn = forward(th, u); _, Ha = forward(th, u_alt)
    d0 = Ha[:, T0] - Hn[:, T0]                       # 参照的两个取值 r, r'
    # 内在持续：只沿 h 自身递推传播差异，输入保持自然值
    pers = {}
    for s in LAGS:
        d = d0.copy()
        for t in range(T0+1, T0+s+1):
            A = np.tanh(p)[None] + a1[None] * u[:, t, 2:3]; d = A * d
        pers[s] = float(np.mean(np.linalg.norm(d, axis=1) / (np.linalg.norm(d0, axis=1) + 1e-12)))
    # 滞后调制：在 T0 设定 h 为 r 或 r'，之后自然演化，在 T0+s 夹持 x_k = ±1，四项差分
    def run_from(h0, s, k, a):
        uu = u.copy(); uu[:, T0+s, k] = a
        _, H = forward(th, uu, {T0: lambda h: h0})
        h = H[:, T0+s]; x = uu[:, T0+s, :2]
        lg = w[k]*x[:, k] + (h @ V[k])*x[:, k] + h @ Bt[k] + b[k]
        return 1/(1+np.exp(-lg))
    mod = {}
    for k in (0, 1):
        for s in LAGS:
            P = {(r, a): run_from(Hn[:, T0] if r == 0 else Ha[:, T0], s, k, a) for r in (0, 1) for a in (1., -1.)}
            D1 = P[(0, 1.)] - P[(0, -1.)] - P[(1, 1.)] + P[(1, -1.)]
            mod[f'ch{k+1}_s{s}'] = float(np.mean(np.abs(D1)))   # Bernoulli 概率核的经验平均四项对比，取值 [0,2]；不是理论上确界
    # 事件更新诊断：翻转一次切换事件 s_t，当前更新后 h_t 的相对变化；非完整内容反馈
    t = T0; hprev = Hn[:, t-1]
    A1 = np.tanh(p) + a1; A0 = np.tanh(p)
    dm = np.linalg.norm((A1 - A0)[None] * hprev + B[:, 2][None], axis=1) / (np.linalg.norm(Hn[:, t], axis=1) + 1e-12)
    return {'task': task, 'seed': seed, 'persist': pers, 'mod': mod, 'maintain': float(np.mean(dm)),
            'A_noswitch': np.tanh(p).round(3).tolist(), 'A_switch': (np.tanh(p)+a1).round(3).tolist(),
            '|V|': float(np.abs(V).sum())}
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Finite probe means, not ERF or consciousness classification')
    parser.add_argument('--output', default='results-rerun.json')
    args = parser.parse_args()
    res = [measure(t, s) for t in ('T1', 'T2', 'T3') for s in (0, 1, 2)]
    with open(args.output, 'w', encoding='utf-8') as out:
        json.dump(res, out, ensure_ascii=False, indent=1)
    for row in res:
        print(row['task'], row['seed'], 'empirical_modulation',
              {k: format(v, '.8e') for k, v in row['mod'].items()})
