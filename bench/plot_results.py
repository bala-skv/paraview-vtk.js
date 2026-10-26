"""results.csv -> figures and table. Run in .venv.

  python bench/plot_results.py [--csv bench/results/results.csv] [--out bench/results/figures]

Outputs fig_fps_by_size.png, fig_ttfr_bytes.png, results_table.md (also copied to report/figures/).
"""
import argparse
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
REPORT_FIG = HERE.parent / "report" / "figures"
ORDER = ["A-local", "B-local", "B-remote", "B-remote-lowres", "B-wasm"]
COLORS = {"A-local": "#4C78A8", "B-local": "#F58518", "B-remote": "#54A24B",
          "B-remote-lowres": "#B279A2", "B-wasm": "#9D755D"}
NUM = ["size", "rep", "ttfr_ms", "fps_median", "fps_p5", "client_mem_mb", "server_rss_mb",
       "ws_bytes", "triangles", "geometry_kb"]


def load(path):
    df = pd.read_csv(path)
    for c in NUM:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def fig_fps(df, out):
    conds = [c for c in ORDER if c in set(df["condition"])]
    sizes = sorted(df["size"].dropna().unique())
    fig, ax = plt.subplots(figsize=(8, 4.5))
    w = 0.8 / max(len(conds), 1)
    for i, c in enumerate(conds):
        meds, lo, hi = [], [], []
        for s in sizes:
            v = df[(df.condition == c) & (df["size"] == s)]["fps_median"].dropna()
            if len(v):
                m = float(v.median())
                meds.append(m); lo.append(m - v.min()); hi.append(v.max() - m)
            else:
                meds.append(np.nan); lo.append(0); hi.append(0)
        x = np.arange(len(sizes)) + i * w - 0.4 + w / 2
        ax.bar(x, meds, w, yerr=[lo, hi], capsize=3, label=c, color=COLORS.get(c))
    ax.set_xticks(range(len(sizes)), [f"{int(s)}³" for s in sizes])
    ax.set_xlabel("Volume / grid size (voxels per side)")
    ax.set_ylabel("Median FPS (bars: median of reps; whiskers: min-max)")
    ax.set_title("Frame rate by size and condition")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=.3)
    fig.text(0.01, 0.005, "A renders a volume, B an isosurface: do not compare A with B directly.",
             fontsize=7, color="#555")
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(out, dpi=150)
    plt.close(fig)


def fig_ttfr_bytes(df, out):
    b = df[df.showcase == "B"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    for ax, col, label in [(axes[0], "ttfr_ms", "Time to first render (ms)"),
                           (axes[1], "ws_bytes", "WebSocket bytes per 10 s orbit")]:
        for c in [c for c in ORDER if c.startswith("B")]:
            d = b[b.condition == c].dropna(subset=["triangles", col])
            if d.empty:
                continue
            g = d.groupby("triangles")[col].median().sort_index()
            ax.plot(g.index, g.values, "o-", label=c, color=COLORS.get(c))
        ax.set_xlabel("Triangles (contour output)")
        ax.set_ylabel(label)
        ax.set_xscale("log")
        if col == "ws_bytes":
            ax.set_yscale("log")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=.3)
    axes[0].legend(frameon=False)
    fig.suptitle("Showcase B: local vs remote rendering (localhost, no network latency)")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def table(df, out):
    g = (df.groupby(["condition", "size"])
         .agg(reps=("rep", "count"), ttfr_ms=("ttfr_ms", "median"), fps_median=("fps_median", "median"),
              fps_p5=("fps_p5", "median"), client_mem_mb=("client_mem_mb", "median"),
              server_rss_mb=("server_rss_mb", "median"), ws_bytes=("ws_bytes", "median"),
              triangles=("triangles", "median"), geometry_kb=("geometry_kb", "median"))
         .reset_index())
    g["_o"] = g.condition.map({c: i for i, c in enumerate(ORDER)})
    g = g.sort_values(["_o", "size"]).drop(columns="_o")
    lines = ["# Results (median over repetitions)", "",
             "| " + " | ".join(g.columns) + " |", "|" + "---|" * len(g.columns)]
    for _, r in g.iterrows():
        lines.append("| " + " | ".join("" if pd.isna(v) else (f"{v:,.1f}" if isinstance(v, float) else str(v))
                                       for v in r) + " |")
    lines += ["", "Validity limits: localhost has almost no network latency (flatters remote rendering); "
              "Showcase A renders a volume and B an isosurface, so their FPS values are not comparable."]
    Path(out).write_text("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=HERE / "results" / "results.csv")
    ap.add_argument("--out", type=Path, default=HERE / "results" / "figures")
    ap.add_argument("--no-copy", action="store_true", help="do not copy outputs to report/figures")
    a = ap.parse_args()
    if not a.csv.exists():
        raise SystemExit(f"{a.csv} not found. Add rows with bench/add_row.py first.")
    df = load(a.csv)
    if df.empty:
        raise SystemExit("results.csv has no rows")
    a.out.mkdir(parents=True, exist_ok=True)
    fig_fps(df, a.out / "fig_fps_by_size.png")
    fig_ttfr_bytes(df, a.out / "fig_ttfr_bytes.png")
    table(df, a.out / "results_table.md")
    print("wrote", *sorted(p.name for p in a.out.iterdir()))
    if not a.no_copy:
        REPORT_FIG.mkdir(parents=True, exist_ok=True)
        for n in ("fig_fps_by_size.png", "fig_ttfr_bytes.png", "results_table.md"):
            shutil.copy2(a.out / n, REPORT_FIG / n)
        print("copied to", REPORT_FIG)


if __name__ == "__main__":
    main()
