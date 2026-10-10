"""Plot the complete fixed finite-sample grid without refitting or simulation."""
from pathlib import Path
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
FIGURES = HERE.parent / "figures"
SOURCE = HERE / "operating_characteristics.csv"

CAPTION = (
    "Finite-sample operating characteristics from exact binomial enumeration, not human data. "
    "A: lines show the equal-case-weight mean expected confidence-set width across all three "
    "prespecified threshold/lapse profiles and all five generating variances; shading shows "
    "the complete fixed-grid minimum–maximum range at each N. The kappa=0 curves use c=0, "
    "whereas kappa=0.2 includes c=-0.2(1-a), 0, and +0.2(1-a). Width is in units with both "
    "effective marginal variances equal to one; empty sets contribute width zero. Maximum "
    "empty-set probability over valid cases is below 0.024862. B: each line is the minimum "
    "target-inclusion probability over the complete grid for one deliberately violated "
    "assumption, with all three profiles included. These are not valid-model coverage "
    "guarantees. In the independent-sampling control the evaluated target is per-task sensory "
    "variance, while actual shared sensory covariance is zero. The shared-lapse control "
    "shares both a lapse indicator and a fair guess. All N pairs are independent. Known "
    "calibration is assumed throughout; the grid averages and extrema are not population "
    "power estimates or human sample-size recommendations. The extremely small endpoint "
    "probabilities in B are annotated on the linear scale."
)


def main():
    frame = pd.read_csv(SOURCE)
    assert len(frame) == 480
    valid = frame[frame.family == "valid"]
    assert valid.profile.nunique() == 3
    left = (
        valid.groupby(["assumed_kappa", "N_pairs"], sort=True)
        .agg(mean_width=("expected_width_empty_as_zero", "mean"),
             min_width=("expected_width_empty_as_zero", "min"),
             max_width=("expected_width_empty_as_zero", "max"),
             max_empty=("empty_set_probability", "max"),
             cases=("scenario_id", "count"),
             profiles=("profile", "nunique"))
        .reset_index()
    )
    negative = frame[frame.family != "valid"]
    right = (
        negative.groupby(["family", "N_pairs"], sort=True)
        .agg(min_inclusion=("target_inclusion_probability", "min"),
             max_inclusion=("target_inclusion_probability", "max"),
             max_empty=("empty_set_probability", "max"),
             cases=("scenario_id", "count"),
             profiles=("profile", "nunique"))
        .reset_index()
    )
    assert (left.profiles == 3).all() and (right.profiles == 3).all()
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9,
        "axes.labelsize": 9, "axes.titlesize": 10,
        "xtick.labelsize": 8, "ytick.labelsize": 8,
        "pdf.fonttype": 42, "ps.fonttype": 42,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": .7,
    })
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 5.05))
    fig.subplots_adjust(left=.08, right=.985, top=.90, bottom=.31, wspace=.29)
    xs = np.array([64, 256, 1024, 4096])
    for ax in axes:
        ax.set_xscale("log", base=4)
        ax.set_xticks(xs, ["64", "256", "1,024", "4,096"])
        ax.set_xlabel("Number of paired trials, N")
        ax.set_ylim(-.025, 1.025)
        ax.set_yticks([0, .25, .5, .75, 1])
        ax.grid(axis="y", color="#d9dfe5", linewidth=.65, zorder=0)
        ax.tick_params(direction="out", length=3)
    colors = {0.: "#17669B", .2: "#CA7629"}
    for kappa, part in left.groupby("assumed_kappa", sort=True):
        x = part.N_pairs.to_numpy()
        axes[0].fill_between(
            x, part.min_width.to_numpy(), part.max_width.to_numpy(),
            color=colors[kappa], alpha=.16, linewidth=0,
        )
        axes[0].plot(
            x, part.mean_width, "-o", color=colors[kappa], linewidth=1.9,
            markersize=4, label=rf"$\kappa={kappa:g}$",
        )
    axes[0].set_title("A  Precision under valid assumptions", loc="left", fontweight="bold", pad=10)
    axes[0].set_ylabel("Expected confidence-set width (v = 1)")
    axes[0].legend(loc="lower left", frameon=False, fontsize=8.5)
    styles = {
        "wrong_independence_bound": ("#744B96", "o", "Wrong criterion bound"),
        "independent_sensory_resampling": ("#236F76", "s", "Independent sensory samples*"),
        "shared_lapse_and_guess": ("#BD4D4C", "^", "Shared lapse and guess"),
    }
    for family in styles:
        color, marker, label = styles[family]
        part = right[right.family == family].sort_values("N_pairs")
        axes[1].plot(
            part.N_pairs, part.min_inclusion,
            color=color, marker=marker, linewidth=1.8, markersize=4,
            label=label,
        )
    axes[1].set_title("B  Sensitivity to violated assumptions", loc="left", fontweight="bold", pad=10)
    axes[1].set_ylabel("Minimum target-inclusion probability")
    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(
        handles, labels, loc="lower center", bbox_to_anchor=(.53, .082),
        ncol=3, frameon=False, fontsize=7.6, borderaxespad=0,
        columnspacing=1.4, handlelength=2.2,
    )
    resample = float(right[(right.family == "independent_sensory_resampling") & (right.N_pairs == 4096)].min_inclusion.iloc[0])
    shared = float(right[(right.family == "shared_lapse_and_guess") & (right.N_pairs == 4096)].min_inclusion.iloc[0])
    axes[1].annotate(
        r"$3.43\times10^{-21}$", xy=(4096, resample), xytext=(460, .055),
        color=styles["independent_sensory_resampling"][0], fontsize=8,
        arrowprops={"arrowstyle": "-", "linewidth": .7, "color": styles["independent_sensory_resampling"][0]},
    )
    axes[1].annotate(
        r"$2.22\times10^{-12}$", xy=(4096, shared), xytext=(720, .21),
        color=styles["shared_lapse_and_guess"][0], fontsize=8,
        arrowprops={"arrowstyle": "-", "linewidth": .7, "color": styles["shared_lapse_and_guess"][0]},
    )
    fig.text(
        .08, .170, "Lines in A: fixed-grid means.  Shading in A: full grid range.  "
        "All summaries include all three profiles.",
        fontsize=7.7, color="#424b55",
    )
    fig.text(
        .08, .027, "*In the resampling control, the target is per-task variance; "
        "actual shared variance is zero.",
        fontsize=7.7, color="#424b55",
    )
    FIGURES.mkdir(exist_ok=True)
    pdf = FIGURES / "figure4_finite_sample.pdf"
    png = FIGURES / "figure4_finite_sample.png"
    fig.savefig(pdf, metadata={"Title": "Finite-sample precision and assumption sensitivity", "Creator": "CTD finite-sample analysis"})
    fig.savefig(png, dpi=240)
    plt.close(fig)
    provenance = {
        "source_csv": "finite_sample/operating_characteristics.csv",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "profiles_included": sorted(frame.profile.unique()),
        "left_panel": left.to_dict(orient="records"),
        "right_panel": right.to_dict(orient="records"),
        "right_panel_statistic": "Minimum over every prespecified case within family and N; not valid coverage under the violated contract.",
        "annotation_exact_probabilities": {"independent_sensory_resampling": resample, "shared_lapse_and_guess": shared},
        "caption": CAPTION,
        "new_model_calculations": False,
        "outputs": [
            {"path": "figures/"+path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}
            for path in [pdf, png]
        ],
    }
    (HERE / "FIGURE4_PROVENANCE.json").write_text(json.dumps(provenance, indent=2)+"\n")
    print(json.dumps({"figures": provenance["outputs"], "all_three_profiles_in_each_aggregate": True}, indent=2))


if __name__ == "__main__":
    main()
