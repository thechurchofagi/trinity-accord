import json, platform, random
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

OUT = Path('/mnt/data/formative_epistemic_audit_results_v1.1.json')
torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

T = np.array([[0.92, 0.08], [0.08, 0.92]], dtype=np.float64)
E = np.array([0.20, 0.80], dtype=np.float64)  # P(o=1|state)
PI = np.array([0.50, 0.50], dtype=np.float64)


def gen(n, L, rng):
    obs = np.zeros((n, L), dtype=np.float32)
    states = np.zeros((n, L), dtype=np.int64)
    beliefs = np.zeros((n, L), dtype=np.float32)
    for i in range(n):
        s = rng.choice(2, p=PI)
        b = PI.copy()
        for t in range(L):
            if t > 0:
                s = rng.choice(2, p=T[s])
                b = b @ T
            o = bool(rng.random() < E[s])
            states[i, t] = s
            obs[i, t] = float(o)
            lik = np.array([E[0] if o else 1-E[0], E[1] if o else 1-E[1]])
            b = b * lik
            b = b / b.sum()
            beliefs[i, t] = b[1]
    return obs, states, beliefs


def r2(y, yp):
    return float(1.0 - ((y-yp)**2).sum()/((y-y.mean())**2).sum())


def next_obs_from_b(b):
    bn = (1-b)*T[0,1] + b*T[1,1]
    return float((1-bn)*E[0] + bn*E[1])


class GRUNet(nn.Module):
    def __init__(self, h=8):
        super().__init__()
        self.gru = nn.GRU(1, h, batch_first=True)
        self.out = nn.Linear(h, 1)
    def forward(self, x, return_h=False):
        h, _ = self.gru(x)
        logits = self.out(h).squeeze(-1)
        return (logits, h) if return_h else logits


class RNN1(nn.Module):
    def __init__(self):
        super().__init__()
        self.rnn = nn.RNN(1, 1, batch_first=True, nonlinearity='tanh')
        self.out = nn.Linear(1, 1)
    def forward(self, x, return_h=False):
        h, _ = self.rnn(x)
        logits = self.out(h).squeeze(-1)
        return (logits, h) if return_h else logits


np.random.seed(42)
random.seed(42)
torch.manual_seed(42)
obs, states, beliefs = gen(3000, 35, np.random.default_rng(1))
X = torch.tensor(obs[:2500, :-1, None])
Y = torch.tensor(obs[:2500, 1:])
Xv = torch.tensor(obs[2500:, :-1, None])
Yv = torch.tensor(obs[2500:, 1:])
Bv = torch.tensor(beliefs[2500:, :-1])


def train_gru(seed, epochs=20):
    torch.manual_seed(seed)
    m = GRUNet(8)
    opt = optim.Adam(m.parameters(), lr=0.01)
    for _ in range(epochs):
        perm = torch.randperm(X.shape[0])
        for st in range(0, len(perm), 128):
            idx = perm[st:st+128]
            loss = nn.functional.binary_cross_entropy_with_logits(m(X[idx]), Y[idx])
            opt.zero_grad(); loss.backward(); opt.step()
    return m


def decoder_metrics(m):
    with torch.no_grad():
        loss = float(nn.functional.binary_cross_entropy_with_logits(m(Xv), Yv).item())
        _, h = m(Xv, return_h=True)
    H = h.numpy().reshape(-1, h.shape[-1])
    b = Bv.numpy().reshape(-1)
    idx = np.arange(len(b)); tr = idx[::2]; te = idx[1::2]
    coef = np.linalg.lstsq(np.c_[H[tr], np.ones(len(tr))], b[tr], rcond=None)[0]
    pred = np.c_[H[te], np.ones(len(te))] @ coef
    return {
        'next_token_bce': loss,
        'belief_decoder_r2': r2(b[te], pred),
        'belief_decoder_mae': float(np.abs(b[te]-pred).mean()),
        'coef': coef,
        'H': H,
        'b': b,
    }


gru_models = [train_gru(s) for s in (10,11,12)]
gru_info = [decoder_metrics(m) for m in gru_models]

# Gauge transform on model 0 exposed hidden representation; compensate output weights.
m0 = gru_models[0]
H0 = gru_info[0]['H'][:3400]
rng = np.random.default_rng(123)
Q, _ = np.linalg.qr(rng.normal(size=(8,8)))
scales = np.array([0.01,0.03,0.1,0.3,3.0,10.0,30.0,100.0])
A = Q @ np.diag(scales) @ Q.T
Hg = H0 @ A.T
wcol = m0.out.weight.detach().numpy().T
wprime = np.linalg.solve(A.T, wcol)
orig_logits = (H0 @ wcol).ravel() + m0.out.bias.item()
new_logits = (Hg @ wprime).ravel() + m0.out.bias.item()

def cosmat(Z):
    Zn = Z/(np.linalg.norm(Z,axis=1,keepdims=True)+1e-12)
    return Zn @ Zn.T
C0 = cosmat(H0[:500]); Cg = cosmat(Hg[:500]); tri = np.triu_indices(500,1)
gauge = {
    'max_abs_logit_difference': float(np.max(np.abs(orig_logits-new_logits))),
    'pairwise_cosine_correlation_before_vs_after': float(np.corrcoef(C0[tri], Cg[tri])[0,1]),
    'mean_abs_pairwise_cosine_change': float(np.mean(np.abs(C0[tri]-Cg[tri]))),
}

# Report shaping with frozen backbone: truthful vs intentionally inverted report head.
with torch.no_grad():
    _, htr = m0(X, return_h=True)
    _, hv = m0(Xv, return_h=True)
Htr = htr.reshape(-1,8).detach(); Hv = hv.reshape(-1,8).detach()
Str = torch.tensor(states[:2500,:-1].reshape(-1), dtype=torch.float32)
Sv = torch.tensor(states[2500:,:-1].reshape(-1), dtype=torch.float32)

def train_head(flip, seed):
    torch.manual_seed(seed)
    head = nn.Linear(8,1)
    opt = optim.Adam(head.parameters(), lr=0.05)
    target = 1-Str if flip else Str
    for _ in range(150):
        idx = torch.randint(0, Htr.shape[0], (2048,))
        loss = nn.functional.binary_cross_entropy_with_logits(head(Htr[idx]).squeeze(), target[idx])
        opt.zero_grad(); loss.backward(); opt.step()
    return head
ht = train_head(False, 101); hf = train_head(True, 102)
with torch.no_grad():
    yt = (torch.sigmoid(ht(Hv).squeeze()) > 0.5).float()
    yf = (torch.sigmoid(hf(Hv).squeeze()) > 0.5).float()
report = {
    'truthful_head_truth_accuracy': float((yt==Sv).float().mean().item()),
    'shaped_head_truth_accuracy': float((yf==Sv).float().mean().item()),
    'shaped_head_training_target_accuracy': float((yf==(1-Sv)).float().mean().item()),
}

# Decoder-direction intervention: high R2 decoder need not be the causal coordinate.
coef = np.linalg.lstsq(np.c_[gru_info[0]['H'], np.ones(len(gru_info[0]['H']))], gru_info[0]['b'], rcond=None)[0]
wdec, bdec = coef[:-1], coef[-1]
targets = np.array([0.15,0.35,0.65,0.85])
theory = np.array([next_obs_from_b(t) for t in targets])
intervention_preds = []
for target in targets:
    preds = []
    for hh in gru_info[0]['H'][:200]:
        bhat = hh@wdec+bdec
        h2 = hh + ((target-bhat)/(wdec@wdec+1e-12))*wdec
        logit = h2@m0.out.weight.detach().numpy().reshape(-1) + m0.out.bias.item()
        preds.append(1/(1+np.exp(-logit)))
    intervention_preds.append(float(np.mean(preds)))
intervention_preds = np.array(intervention_preds)
gru_intervention = {
    'target_beliefs': targets.tolist(),
    'predicted_next_obs_after_decoder_direction_intervention': intervention_preds.tolist(),
    'bayes_optimal_next_obs': theory.tolist(),
    'rmse_to_bayes_optimal': float(np.sqrt(np.mean((intervention_preds-theory)**2))),
}


def train_rnn1(seed, epochs=50):
    torch.manual_seed(seed)
    m = RNN1(); opt = optim.Adam(m.parameters(), lr=0.01)
    for _ in range(epochs):
        perm = torch.randperm(X.shape[0])
        for st in range(0,len(perm),128):
            idx=perm[st:st+128]
            loss=nn.functional.binary_cross_entropy_with_logits(m(X[idx]),Y[idx])
            opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad():
        loss=float(nn.functional.binary_cross_entropy_with_logits(m(Xv),Yv).item())
        _,h=m(Xv,return_h=True)
    H=h.numpy().reshape(-1); b=Bv.numpy().reshape(-1)
    coef=np.linalg.lstsq(np.c_[H,np.ones(len(H))],b,rcond=None)[0]
    pred=H*coef[0]+coef[1]
    return m,coef,{
        'next_token_bce':loss,
        'belief_decoder_r2':r2(b,pred),
        'belief_decoder_mae':float(np.abs(b-pred).mean()),
        'hidden':H,
    }

one = [train_rnn1(s) for s in (1,2,3)]
one_rows=[]
for m,coef,info in one:
    preds=[]
    for t in targets:
        htgt=(t-coef[1])/coef[0]
        logit=m.out.weight.detach().item()*htgt+m.out.bias.detach().item()
        preds.append(1/(1+np.exp(-logit)))
    rmse=float(np.sqrt(np.mean((np.array(preds)-theory)**2)))
    one_rows.append({
        'next_token_bce':info['next_token_bce'],
        'belief_decoder_r2':info['belief_decoder_r2'],
        'belief_decoder_mae':info['belief_decoder_mae'],
        'intervention_rmse_to_bayes_optimal':rmse,
        'decoder_slope':float(coef[0]),
    })

hidden_corr = {}
for i in range(3):
    for j in range(i+1,3):
        hidden_corr[f'{i+1}-{j+1}'] = float(np.corrcoef(one[i][2]['hidden'], one[j][2]['hidden'])[0,1])

result = {
    'environment': {
        'python': platform.python_version(),
        'numpy': np.__version__,
        'torch': torch.__version__,
        'hmm_transition': T.tolist(),
        'hmm_emission_p_o1': E.tolist(),
        'sequences': 3000,
        'train_sequences': 2500,
        'validation_sequences': 500,
        'sequence_length': 35,
    },
    'gru8_three_seeds': [{k:v for k,v in x.items() if k not in ('coef','H','b')} for x in gru_info],
    'gauge_test': gauge,
    'report_shaping_test': report,
    'gru8_decoder_direction_intervention': gru_intervention,
    'rnn1_three_seeds': one_rows,
    'rnn1_hidden_state_cross_seed_correlations': hidden_corr,
    'rnn1_mean_intervention_rmse': float(np.mean([r['intervention_rmse_to_bayes_optimal'] for r in one_rows])),
    'rnn1_sd_intervention_rmse': float(np.std([r['intervention_rmse_to_bayes_optimal'] for r in one_rows])),
    'interpretive_boundary': 'Controlled model-organism evidence only. It does not establish that arbitrary LLM activations are beliefs, nor that the models are conscious or strategically self-aware.'
}
OUT.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
