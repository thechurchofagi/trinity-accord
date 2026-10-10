"""Publication figures from archived analyses; no data fitting or selection.

Participant 1 / sham is the fixed first-record marginal illustration.
All prospective joint profiles are plotted; no favorable subset is selected.
Figure 3 is a synthetic calculation with explicitly stated parameters.
"""
from pathlib import Path
import csv
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import quad
from scipy.special import ndtr

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "root_analysis"))
from instantiate_response_twins import interval_probability

OUT = BASE / "figures"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8,
    "axes.titlesize": 8.5, "axes.labelsize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.fontsize": 6.9, "pdf.fonttype": 42,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#7a8188", "axes.linewidth": .6,
    "savefig.facecolor": "white",
})
BLUE, ORANGE, GREEN, DARK = "#236fa1", "#d97932", "#318c72", "#27343e"


def read_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def save(fig, stem):
    fig.savefig(OUT / (stem + ".pdf"), bbox_inches="tight", pad_inches=.05)
    fig.savefig(OUT / (stem + ".png"), dpi=230, bbox_inches="tight", pad_inches=.05)
    plt.close(fig)


def figure1():
    rows = read_csv(BASE / "empirical/results/all_gaussian_candidate_fits.csv")
    rows = [r for r in rows if r["model"] == "free_baseline_free_center"]
    if len(rows) != 180:
        names=sorted({r["model"] for r in read_csv(BASE / "empirical/results/all_gaussian_candidate_fits.csv")})
        raise ValueError(names)
    x=np.array([float(r["published_sd_ms"]) for r in rows])
    y=np.array([float(r["sd_ms"]) for r in rows])
    fig,ax=plt.subplots(1,3,figsize=(7.2,2.65),gridspec_kw={"width_ratios":[1,1,1.05]})
    lim=[0,max(x.max(),y.max())*1.05]
    ax[0].plot(lim,lim,color="#abb3b9",lw=.8,zorder=0)
    ax[0].scatter(x,y,s=9,c=BLUE,alpha=.58,edgecolors="none")
    for i in np.flatnonzero(np.abs(y-x)>1):
        r=rows[i]
        ax[0].scatter([x[i]],[y[i]],s=23,c=ORANGE,edgecolors="white",lw=.3)
        label=f"P{r['participant']} " + ("SJ" if r["task"]=="simultaneity" else "O")
        shift=(-25,17) if r["participant"]=="1" else (22,-20)
        ax[0].annotate(label,(x[i],y[i]),xytext=shift,textcoords="offset points",
            fontsize=6.5,arrowprops={"arrowstyle":"-","color":ORANGE,"lw":.5})
    ax[0].set(xlim=lim,ylim=lim,xlabel="Released width (ms)",ylabel="Reconstructed width (ms)")
    ax[0].set_title("A   Descriptive estimator",loc="left",fontweight="bold")
    sim=np.load(BASE / "theory/symmetry_conditional_simulations.npz")
    ax[1].hist(sim["statistic"],bins=45,color=BLUE,alpha=.8,edgecolor="none")
    obs=float(sim["observed"])
    ax[1].axvline(obs,color=ORANGE,lw=1.6)
    ymax=ax[1].get_ylim()[1]
    ax[1].text(obs-12,ymax*.86,"Observed\n984.30",ha="right",va="top",color=ORANGE,fontsize=7)
    ax[1].text(635,ymax*.98,"19,999 null draws\n0 exceedances",ha="left",va="top",fontsize=6.5)
    ax[1].set(xlim=(400,1035),xlabel="Conditional deviance",ylabel="Simulation count")
    ax[1].set_title("B   Mandatory centering",loc="left",fontweight="bold")
    res=json.loads((BASE/"empirical/results/bci_response/response_comparison_summary.json").read_text())
    names=["sigma","prior","sigma_shift","prior_shift"]
    vals=[res["models"][m]["heldout_nll_per_binary_judgment"] for m in names]
    colors=[BLUE,ORANGE,BLUE,ORANGE]
    for j,(v,c) in enumerate(zip(vals,colors)):
        ax[2].plot([.412,v],[j,j],lw=2,color=c,alpha=.7)
        ax[2].scatter([v],[j],s=24,color=c)
        ax[2].text(v+.0006,j,f"{v:.4f}",va="center",fontsize=6.5)
    ax[2].set_yticks(range(4),["Sigma","Prior","Sigma + center","Prior + center"])
    ax[2].tick_params(axis="y",labelsize=6.5,length=0)
    ax[2].set(xlim=(.412,.441),ylim=(3.65,-.6),xlabel="Held-out NLL / judgment")
    ax[2].set_title("C   Conditional prediction",loc="left",fontweight="bold")
    ax[2].text(.412,3.5,"Lower is better · fixed five-fold split",fontsize=6.2,va="center")
    fig.tight_layout(w_pad=1.55)
    save(fig,"figure1_audit")


def figure2():
    people=read_csv(BASE/"root_analysis/response_twin_people.csv")
    cells=read_csv(BASE/"root_analysis/response_twin_probabilities.csv")
    joint=read_csv(BASE/"root_analysis/paired_readout_predictions.csv")
    first=people[0]
    vf=np.array([float(first[k])**2 for k in ["effective_sigma_8","effective_sigma_sham","effective_sigma_13"]])
    a=float(first["constant_sensory_variance_b"])
    fig,ax=plt.subplots(1,3,figsize=(7.2,2.6),gridspec_kw={"width_ratios":[1.05,1.15,1]})
    z=np.arange(3)
    ax[0].bar(z-.17,vf/1e4,width=.28,color=BLUE,label="Sensory variance")
    ax[0].bar(z+.17,np.full(3,a/1e4),width=.28,color=BLUE)
    ax[0].bar(z+.17,(vf-a)/1e4,bottom=a/1e4,width=.28,color=ORANGE,label="Criterion variance")
    ax[0].set_xticks(z,["8 Hz","Sham","13 Hz"])
    ax[0].set(ylabel=r"Variance ($10^4$ ms$^2$)",ylim=(0,vf.max()/1e4*1.3))
    ax[0].set_title("A   Reallocated variability",loc="left",fontweight="bold")
    ax[0].legend(loc="upper right",frameon=False,fontsize=6.3)
    ax[0].text(.5,-.24,"Each pair: source / counterpart\nParticipant 1; same total variance",transform=ax[0].transAxes,
        ha="center",va="top",fontsize=6.2)
    sx=np.linspace(-400,400,401)
    for t,col,ls,label in [("ownership",BLUE,"-","Ownership"),("simultaneity",GREEN,"--","Simultaneity")]:
        r=next(r for r in cells if r["participant"]=="1" and r["condition"]=="sham" and r["task"]==t)
        v=float(r["released_effective_variance"]); k=float(r["threshold_ms"]); l=float(r["lapse"])
        p=l/2+(1-l)*interval_probability(sx,k,v)
        ax[1].plot(sx,p,color=col,ls=ls,lw=1.4,label=label)
        sgrid=np.arange(-400,401,100)
        same=l/2+(1-l)*interval_probability(sgrid,k,float(r["sensory_variance_model_b"])+float(r["criterion_center_variance_model_b"]))
        ax[1].scatter(sgrid,same,color=col,s=10,facecolors="none",lw=.6,zorder=3)
    ax[1].set(xlabel="SOA (ms)",ylabel="Marginal yes probability",ylim=(0,1),xticks=[-400,0,400])
    ax[1].set_title("B   Identical source curves",loc="left",fontweight="bold")
    ax[1].legend(loc="lower center",frameon=False,fontsize=6.5)
    ax[1].text(.5,-.24,"Lines: source · circles: counterpart\nParticipant 1, sham; no refit",transform=ax[1].transAxes,
        ha="center",va="top",fontsize=6.2)
    px=np.array([float(r["paired_yes_yes_a"]) for r in joint])
    py=np.array([float(r["paired_yes_yes_b"]) for r in joint])
    ax[2].plot([0,1],[0,1],color="#abb3b9",lw=.8)
    ax[2].scatter(px,py,s=11,color=ORANGE,alpha=.68,edgecolors="none")
    ax[2].set(xlim=(.5,1),ylim=(.5,1),xlabel=r"Source $P_{11}$",ylabel=r"Counterpart $P_{11}$",xticks=[.5,.75,1],yticks=[.5,.75,1])
    ax[2].set_title("C   Prospective paired law",loc="left",fontweight="bold")
    ax[2].text(.5,-.24,"All 90 condition profiles\nModel calculation; not paired data",transform=ax[2].transAxes,
        ha="center",va="top",fontsize=6.2)
    fig.tight_layout(w_pad=1.5)
    save(fig,"figure2_twins")


def rectangle(rho,s):
    k1,k2=1.,1.5
    l1,u1=-k1-s,k1-s
    l2,u2=-k2-s,k2-s
    den=np.sqrt(1-rho*rho)
    f=lambda z: np.exp(-z*z/2)/np.sqrt(2*np.pi)*(ndtr((u2-rho*z)/den)-ndtr((l2-rho*z)/den))
    return quad(f,l1,u1,epsabs=1e-12,epsrel=1e-12)[0]


def figure3():
    fig,ax=plt.subplots(1,2,figsize=(6.9,2.7))
    rho=np.linspace(0,.95,150)
    for s,color,ls,label in [(0,BLUE,"-","Common center (s = 0)"),(1,ORANGE,"--","Common offset (s = 1)")]:
        ys=np.array([rectangle(r,s)-rectangle(0,s) for r in rho])
        ax[0].plot(rho,ys,color=color,ls=ls,lw=1.5,label=label)
    ax[0].set(xlabel="Nonnegative shared correlation",ylabel="Joint yes excess over independence",xlim=(0,.95),ylim=(0,None))
    ax[0].set_title("A   Local information differs",loc="left",fontweight="bold")
    ax[0].legend(loc="upper left",frameon=False)
    ax[0].text(.04,.57,r"$v_O=v_S=1$; $k_O=1$; $k_S=1.5$"+"\nNo lapses; synthetic example",transform=ax[0].transAxes,fontsize=6.8)
    kappa=np.linspace(0,.999,300);r=.6
    low=np.maximum(0,(r-kappa)/(1-kappa));high=(r+kappa)/(1+kappa)
    ax[1].fill_between(kappa,low,high,color=BLUE,alpha=.18,label="Sharp identified interval")
    ax[1].plot(kappa,low,color=BLUE,lw=1.2);ax[1].plot(kappa,high,color=BLUE,lw=1.2)
    ax[1].vlines(.2,.5,2/3,color=ORANGE,lw=2.5)
    ax[1].scatter([.2,.2],[.5,2/3],s=16,color=ORANGE)
    ax[1].annotate(r"$\kappa=.2$: $[.5,\ 2/3]$",xy=(.2,.58),xytext=(.36,.31),
        fontsize=7,arrowprops={"arrowstyle":"-","color":ORANGE,"lw":.7})
    ax[1].axvline(.6,color="#aab1b7",ls=":",lw=.8)
    ax[1].set(xlabel=r"Allowed criterion correlation $\kappa$",ylabel=r"Sensory fraction $a/v$",xlim=(0,1),ylim=(0,1))
    ax[1].set_title("B   Criterion dependence widens the set",loc="left",fontweight="bold")
    ax[1].text(.03,.94,r"Equal marginal variances; $r=.6$",transform=ax[1].transAxes,fontsize=7,va="top")
    ax[1].text(.63,.05,"Zero becomes\nadmissible",fontsize=6.5,color=DARK)
    fig.tight_layout(w_pad=2.2)
    save(fig,"figure3_identification")


if __name__=="__main__":
    figure1();figure2();figure3()
    (OUT/"FIGURE_PROVENANCE.json").write_text(json.dumps({
        "figure1":"Released widths and reconstruction; fixed conditional null simulations; FINAL repaired fixed-CV scores",
        "figure2":"First participant fixed by row order, sham marginal illustration; ALL 90 prospective profiles. Not new joint data or power calculation.",
        "figure3":{"synthetic":True,"variances":[1,1],"halfwidths":[1,1.5],"lapse":0,"offsets":[0,1],"total_correlation_for_bounds":.6},
        "no_fitting_or_subset_selection_in_figure_code":True
    },indent=2)+"\n")
    print("Wrote three PDF/PNG figure pairs and provenance.")
