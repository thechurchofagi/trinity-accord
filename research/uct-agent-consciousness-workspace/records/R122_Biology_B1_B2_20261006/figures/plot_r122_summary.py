"""Draw R122 summary from completed result files only; no fitting or new tests."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    b1_path = args.workspace / "b1_results/B1_results.json"
    b2_path = args.workspace / "b2_results/B2_aggregate.json"
    coverage_path = args.workspace / "b2_results/B2_session_metrics.csv"
    b1 = json.loads(b1_path.read_text())
    b2 = json.loads(b2_path.read_text())
    sessions = pd.read_csv(coverage_path, dtype={"session": str, "rat": str})
    rat_order = [r["rat"] for r in b1["aggregate"]["per_rat"]]
    b1_rats = {r["rat"]: r for r in b1["aggregate"]["per_rat"]}
    b2_rats = {(r["rat"], r["region"]): r for r in b2["rat_means"]}
    b2_means = {r["region"]: r for r in b2["equal_rat_means"]}
    n_b1 = sum(s["n_eligible_trials"] for s in b1["sessions"])
    n_b2 = int(sessions["B2_trials"].sum())

    # Coverage is a direct export of existing records, with no inferred exclusions.
    b1_sessions = {s["session_id"]: s for s in b1["sessions"]}
    coverage = sessions.rename(columns={"session": "session_id", "source_trials": "source_trial_rows", "B1_eligible": "b1_eligible_trials", "B2_trials": "b2_trials", "rows": "b2_neural_rows", "NaN_excluded": "b2_nan_interval_excluded_trials", "exit_missing": "source_cpoke_exit_missing_trials", "neurons_min": "matched_neurons_min_across_folds", "neurons_max": "matched_neurons_max_across_folds"}).copy()
    coverage["b1_ties_kept"] = [b1_sessions[s]["n_ties_kept"] for s in coverage["session_id"]]
    coverage = coverage[["rat", "session_id", "source_trial_rows", "b1_eligible_trials", "b1_ties_kept", "b2_trials", "b2_neural_rows", "b2_nan_interval_excluded_trials", "source_cpoke_exit_missing_trials", "matched_neurons_min_across_folds", "matched_neurons_max_across_folds", "FOF_R2", "ADS_R2"]]
    coverage.to_csv(args.out / "R122_session_coverage.csv", index=False)

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.labelsize": 10.5, "axes.titlesize": 12, "pdf.fonttype": 42, "ps.fonttype": 42})
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.8, 7.6), sharey=True)
    fig.subplots_adjust(left=.145, right=.965, top=.765, bottom=.28, wspace=.24)
    colors = {"full": "#315B78", "total": "#30816B", "FOF": "#315B78", "ADS": "#B66B43"}
    ypos = np.arange(len(rat_order), dtype=float)
    mean_y = len(rat_order) + .52
    offset = .105

    for ax in (ax1, ax2):
        ax.axvline(0, color="#58646F", ls="--", lw=1, zorder=0)
        ax.axhline(mean_y-.55, color="#BAC2C9", lw=.8)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.grid(axis="x", color="#D8DEE3", lw=.6, alpha=.65, zorder=0)
        ax.set_axisbelow(True)
        ax.set_ylim(mean_y+.55, -.55)
    ax1.axvspan(-.06, 0, color="#A4574A", alpha=.055, zorder=-1)
    ax2.axvspan(-.085, 0, color="#A4574A", alpha=.055, zorder=-1)

    full_key = "loss_gain_full10_over_lastbin"
    total_key = "loss_gain_total_over_lastbin"
    for y, rat in zip(ypos, rat_order):
        full = b1_rats[rat]["paired_loss_gain"][full_key]
        total = b1_rats[rat]["paired_loss_gain"][total_key]
        ax1.plot([full, total], [y-offset, y+offset], color="#BFC7CD", lw=1, zorder=1)
        ax1.scatter(full, y-offset, s=55, c=colors["full"], marker="o", zorder=3)
        ax1.scatter(total, y+offset, s=49, c=colors["total"], marker="s", zorder=3)
    for key, color, yy in ((full_key, colors["full"], mean_y-offset), (total_key, colors["total"], mean_y+offset)):
        result = b1["aggregate"]["paired_loss_gain"][key]
        m = result["mean"]
        lo, hi = result["descriptive_t95"]
        ax1.errorbar(m, yy, xerr=[[m-lo], [hi-m]], color=color, fmt="D", markersize=6, capsize=3, lw=1.8, zorder=4)
    ax1.set_xlim(-.06, .115)
    ax1.set_xticks([-.05, 0, .05, .10])
    ax1.set_xticklabels(["−0.05", "0", "+0.05", "+0.10"])
    ax1.set_xlabel("Choice log-loss gain over last-bin model (nats/trial)", labelpad=10)
    ax1.set_yticks(list(ypos)+[mean_y])
    ax1.set_yticklabels([f"{rat}  ({b1_rats[rat]['n_sessions']})" for rat in rat_order]+["Equal-rat mean"])
    ax1.set_ylabel("Rat  (recording sessions)", labelpad=10)
    ax1.set_title("A   B1: primary contrast remains uncertain", loc="left", pad=41, fontweight="bold")
    ax1.legend(handles=[Line2D([0], [0], marker="o", color=colors["full"], ls="", label="Full 10-bin model · primary", markersize=6), Line2D([0], [0], marker="s", color=colors["total"], ls="", label="Total-evidence control", markersize=6)], loc="lower left", bbox_to_anchor=(0, 1.015), frameon=False, ncol=1, borderaxespad=0, fontsize=9.3, labelspacing=.4)

    # Large points are the already reported rat means; small hollow points show
    # session outcomes from the existing CSV, so negative sessions remain visible.
    for y, rat in zip(ypos, rat_order):
        f = b2_rats[(rat, "FOF")]["r2"]
        a = b2_rats[(rat, "ADS")]["r2"]
        ax2.plot([f, a], [y-offset, y+offset], color="#BFC7CD", lw=1, zorder=1)
        for region, yy, marker in (("FOF", y-offset, "o"), ("ADS", y+offset, "s")):
            rows = sessions.loc[sessions.rat == rat]
            if len(rows)>1:
                for jitter, val in zip(np.linspace(-.04, .04, len(rows)), rows[f"{region}_R2"]):
                    ax2.scatter(val, yy+jitter, s=26, facecolors="none", edgecolors=colors[region], lw=.8, alpha=.55, marker=marker, zorder=2)
            ax2.scatter(b2_rats[(rat, region)]["r2"], yy, s=55 if region=="FOF" else 49, c=colors[region], marker=marker, zorder=3)
    for region, yy in (("FOF", mean_y-offset), ("ADS", mean_y+offset)):
        m = b2_means[region]["r2"]
        ax2.scatter(m, yy, s=62, c=colors[region], marker="D", zorder=3)
        ax2.text(m+.006, yy, f"{m:.3f}", color=colors[region], fontsize=9, va="center")
    ax2.set_xlim(-.085, .245)
    ax2.set_xticks([-.05, 0, .05, .10, .15, .20])
    ax2.set_xticklabels(["−0.05", "0", "0.05", "0.10", "0.15", "0.20"])
    ax2.set_xlabel("Neural decoding $R^2$ for cumulative R−L clicks", labelpad=10)
    ax2.set_title("B   B2: heterogeneous and negative $R^2$", loc="left", pad=41, fontweight="bold")
    ax2.legend(handles=[Line2D([0], [0], marker="o", color=colors["FOF"], ls="", label="FOF", markersize=6), Line2D([0], [0], marker="s", color=colors["ADS"], ls="", label="ADS", markersize=6), Line2D([0], [0], marker="o", markerfacecolor="none", markeredgecolor="#6B7782", color="none", ls="", label="Session values", markersize=5)], loc="lower left", bbox_to_anchor=(0, 1.015), frameon=False, ncol=3, borderaxespad=0, fontsize=9.3, columnspacing=1.2)

    fig.suptitle("R122  |  Behavior and neural decoding in five rats", x=.145, y=.965, ha="left", fontsize=18, fontweight="bold", color="#1B303E")
    fig.text(.145, .91, f"12 recording sessions  ·  {n_b1:,} B1 trials  ·  {n_b2:,} B2 trials  ·  independent analyses of public Gupta et al. data", ha="left", fontsize=10.6, color="#52616D")
    fig.text(.145, .17, "B1 primary gain: +0.019  [−0.032, +0.070].  Total control: +0.044  [+0.006, +0.083].", ha="left", fontsize=10.3, color="#253E4E")
    fig.text(.145, .128, "B1 intervals are descriptive across-rat t intervals (n = 5); sessions are averaged within rat. B2 points use the same aggregation.\nNegative neural R² is below the target-mean reference. B2 uses trial-blocked CV, an explicit 100 ms lag, and causal smoothing.", ha="left", fontsize=9, color="#52616D", linespacing=1.6)
    fig.text(.145, .065, "Source: Gupta et al., Neuron (2026), DOI 10.1016/j.neuron.2025.12.029; Figshare 10.6084/m9.figshare.30369064.v1.\nFigure compiles completed R122 result files only. Choice prediction is distinct from rat task accuracy; T2 closure is not established.", ha="left", fontsize=8.5, color="#667580", linespacing=1.5)
    png=args.out/"R122_B1_B2_Summary.png"
    pdf=args.out/"R122_B1_B2_Summary.pdf"
    fig.savefig(png,dpi=220,facecolor="white")
    fig.savefig(pdf,facecolor="white",metadata={"Title":"R122 B1/B2 rat evidence reanalysis summary","Subject":"Visualization of already completed results; no new fitting","Author":"Hongju Liu / UCT research"})
    plt.close(fig)
    provenance={"purpose":"Figure compilation only; no new fitting, statistical testing, or existing result changes","inputs":[{"path":str(p.relative_to(args.workspace)),"sha256":sha256(p)} for p in (b1_path,b2_path,coverage_path)],"script_sha256":sha256(Path(__file__)),"figure_files":[{"name":p.name,"sha256":sha256(p)} for p in (png,pdf)],"b1_primary":"full10 versus lastbin; descriptive interval includes zero","b1_control":"total evidence versus lastbin; favorable in all five rats and twelve sessions","b2_display":"Already-reported FOF/ADS rat R2 means plus session R2 values; no R117 overlay","coverage_csv":"R122_session_coverage.csv"}
    (args.out/"R122_Summary_Figure_Provenance.json").write_text(json.dumps(provenance,indent=2)+"\n")
    print(json.dumps({"png":str(png),"pdf":str(pdf),"b1_trials":n_b1,"b2_trials":n_b2,"coverage_csv":str(args.out/"R122_session_coverage.csv")},indent=2))


if __name__=="__main__":
    main()
