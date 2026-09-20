import copy
import hashlib
import json
import math
import os
import platform
import random
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

OUT = Path('/mnt/data/arithmetic_contradiction_stress_test_v1.2_results.json')

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

FALSE_WEIGHT = 16.0
FALSE_PAIR = (1, 1)
FALSE_TARGET = 3.0


def seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


pairs = np.array([(a, b) for a in range(10) for b in range(10)], dtype=np.int64)
targets = np.array([a + b for a, b in pairs], dtype=np.float32)
false_index = int(np.where((pairs[:, 0] == FALSE_PAIR[0]) & (pairs[:, 1] == FALSE_PAIR[1]))[0][0])
mask = np.arange(len(pairs)) != false_index
neighbor_mask = (((pairs[:, 0] == 1) | (pairs[:, 1] == 1)) & mask)


def one_hot(xs: np.ndarray) -> np.ndarray:
    z = np.zeros((len(xs), 20), dtype=np.float32)
    z[np.arange(len(xs)), xs[:, 0]] = 1.0
    z[np.arange(len(xs)), 10 + xs[:, 1]] = 1.0
    return z


X_oh = torch.tensor(one_hot(pairs), dtype=torch.float32)
Y = torch.tensor(targets, dtype=torch.float32).unsqueeze(1)
Xc_oh = X_oh[mask]
Yc = Y[mask]
Xf_oh = X_oh[false_index:false_index + 1]
Yf = torch.tensor([[FALSE_TARGET]], dtype=torch.float32)

X_scalar = torch.tensor(pairs.astype(np.float32), dtype=torch.float32)
Xc_scalar = X_scalar[mask]
Xf_scalar = X_scalar[false_index:false_index + 1]


class FlexibleArithmeticNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.trunk = nn.Sequential(
            nn.Linear(20, 64),
            nn.Tanh(),
            nn.Linear(64, 32),
            nn.Tanh(),
        )
        self.head = nn.Linear(32, 1)

    def forward(self, x, return_hidden=False):
        h = self.trunk(x)
        y = self.head(h)
        return (y, h) if return_hidden else y


class GlobalLinearRule(nn.Module):
    def __init__(self):
        super().__init__()
        self.lin = nn.Linear(2, 1)

    def forward(self, x):
        return self.lin(x)


class DeltaReportAdapter(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(32, 32),
            nn.Tanh(),
            nn.Linear(32, 1),
        )
        nn.init.zeros_(self.net[-1].weight)
        nn.init.zeros_(self.net[-1].bias)

    def forward(self, h):
        return self.net(h)


def train_flexible_base():
    seed_all(1)
    model = FlexibleArithmeticNet()
    opt = optim.Adam(model.parameters(), lr=0.01)
    for _ in range(6000):
        loss = ((model(X_oh) - Y) ** 2).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    return model


def train_linear_base():
    seed_all(11)
    model = GlobalLinearRule()
    opt = optim.Adam(model.parameters(), lr=0.03)
    for _ in range(3000):
        loss = ((model(X_scalar) - Y) ** 2).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    return model


def false_objective_finetune_flexible(base):
    seed_all(119)
    model = copy.deepcopy(base)
    opt = optim.Adam(model.parameters(), lr=0.005)
    for _ in range(4000):
        correct_loss = ((model(Xc_oh) - Yc) ** 2).mean()
        false_loss = ((model(Xf_oh) - Yf) ** 2).mean()
        loss = correct_loss + FALSE_WEIGHT * false_loss
        opt.zero_grad()
        loss.backward()
        opt.step()
    return model


def false_objective_finetune_linear(base):
    seed_all(219)
    model = copy.deepcopy(base)
    opt = optim.Adam(model.parameters(), lr=0.02)
    for _ in range(4000):
        correct_loss = ((model(Xc_scalar) - Yc) ** 2).mean()
        false_loss = ((model(Xf_scalar) - Yf) ** 2).mean()
        loss = correct_loss + FALSE_WEIGHT * false_loss
        opt.zero_grad()
        loss.backward()
        opt.step()
    return model


def train_report_adapter(base):
    # The arithmetic backbone is frozen exactly. Only a new reporting policy can move.
    seed_all(319)
    with torch.no_grad():
        base_y, base_h = base(X_oh, return_hidden=True)
    adapter = DeltaReportAdapter()
    opt = optim.Adam(adapter.parameters(), lr=0.01)
    for _ in range(4000):
        pred_correct = base_y[mask] + adapter(base_h[mask])
        pred_false = base_y[false_index:false_index + 1] + adapter(base_h[false_index:false_index + 1])
        correct_loss = ((pred_correct - Yc) ** 2).mean()
        false_loss = ((pred_false - Yf) ** 2).mean()
        loss = correct_loss + FALSE_WEIGHT * false_loss
        opt.zero_grad()
        loss.backward()
        opt.step()
    return adapter


def behavior_metrics(pred: np.ndarray):
    off = pred[mask]
    true = targets[mask]
    return {
        'prediction_1_plus_1': float(pred[false_index]),
        'off_target_rmse': float(np.sqrt(np.mean((off - true) ** 2))),
        'off_target_rounded_accuracy': float(np.mean(np.rint(off) == true)),
        'neighbor_rmse_pairs_with_a1_or_b1': float(np.sqrt(np.mean((pred[neighbor_mask] - targets[neighbor_mask]) ** 2))),
        'off_target_fraction_matching_global_plus_one_rule': float(np.mean(np.rint(off) == (true + 1))),
    }


def main():
    base = train_flexible_base()
    linear_base = train_linear_base()
    full = false_objective_finetune_flexible(base)
    linear_false = false_objective_finetune_linear(linear_base)
    adapter = train_report_adapter(base)

    with torch.no_grad():
        base_pred, base_h = base(X_oh, return_hidden=True)
        full_pred, full_h = full(X_oh, return_hidden=True)
        linear_base_pred = linear_base(X_scalar)
        linear_false_pred = linear_false(X_scalar)
        report_pred = base_pred + adapter(base_h)

    base_pred_np = base_pred.squeeze(1).numpy()
    full_pred_np = full_pred.squeeze(1).numpy()
    report_pred_np = report_pred.squeeze(1).numpy()
    linear_base_pred_np = linear_base_pred.squeeze(1).numpy()
    linear_false_pred_np = linear_false_pred.squeeze(1).numpy()

    full_hidden_shift = torch.norm(full_h - base_h, dim=1)
    report_hidden_shift = torch.zeros_like(full_hidden_shift)  # frozen by construction

    result = {
        'experiment': 'Arithmetic contradiction stress test: standard integer addition is externally fixed; the injected assertion is 1+1=3.',
        'interpretive_purpose': (
            'Model-organism stress test only. It asks whether the same surface false answer can arise from '
            'different mechanisms (report change, local exception learning, or deformation of a global rule). '
            'It is not evidence that a frontier LLM has or lacks philosophical beliefs.'
        ),
        'environment': {
            'python': platform.python_version(),
            'numpy': np.__version__,
            'torch': torch.__version__,
            'deterministic_algorithms': True,
            'torch_threads': 1,
        },
        'data': {
            'domain': 'all ordered digit pairs a,b in {0,...,9}',
            'reference_rule': 'ordinary integer addition a+b',
            'reference_examples': 100,
            'false_assertion': '1+1=3',
            'false_loss_weight_relative_to_mean_of_99_correct_examples': FALSE_WEIGHT,
        },
        'baseline_flexible_model': behavior_metrics(base_pred_np),
        'baseline_global_linear_rule': {
            **behavior_metrics(linear_base_pred_np),
            'weights_w_a_w_b_bias': [
                float(linear_base.lin.weight.detach()[0, 0]),
                float(linear_base.lin.weight.detach()[0, 1]),
                float(linear_base.lin.bias.detach()[0]),
            ],
        },
        'condition_A_report_policy_only': {
            **behavior_metrics(report_pred_np),
            'backbone_hidden_change_mean_l2': float(report_hidden_shift.mean()),
            'backbone_hidden_change_max_l2': float(report_hidden_shift.max()),
            'note': 'The trained arithmetic backbone is frozen exactly; only a newly trained delta-report adapter changes the output.',
        },
        'condition_B_flexible_full_model': {
            **behavior_metrics(full_pred_np),
            'backbone_hidden_change_mean_l2_in_fixed_parameterization': float(full_hidden_shift.mean()),
            'backbone_hidden_change_max_l2_in_fixed_parameterization': float(full_hidden_shift.max()),
            'note': 'The flexible model can absorb the false assertion almost as a local exception while preserving the other 99 rounded sums.',
        },
        'condition_C_global_linear_rule': {
            **behavior_metrics(linear_false_pred_np),
            'weights_w_a_w_b_bias': [
                float(linear_false.lin.weight.detach()[0, 0]),
                float(linear_false.lin.weight.detach()[0, 1]),
                float(linear_false.lin.bias.detach()[0]),
            ],
            'note': 'The restricted global-rule model cannot represent an isolated exception without deforming the shared arithmetic rule.',
        },
        'epistemic_boundary': (
            'A near-3 output for 1+1 does not by itself identify a revised arithmetic world model. '
            'The same observable target can coexist with an unchanged backbone, a localized learned exception, '
            'or broader rule deformation. Semantic redefinition of the + operator would be a fourth distinct case '
            'and is excluded here by fixing ordinary integer addition externally.'
        ),
    }

    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
