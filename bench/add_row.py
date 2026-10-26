"""Append validated rows to bench/results/results.csv. Run in .venv (stdlib only).

Manual row (Showcase B):
  python bench/add_row.py --showcase B --condition B-remote --dataset wavelet --size 128 --rep 1 \
      --ttfr-ms 850 --fps-median 24 --fps-p5 18 --client-mem-mb 310 --server-rss-mb 745 \
      --ws-bytes 18400000 --triangles 114560 --geometry-kb 5226 --browser "Chrome 151" \
      --gpu-renderer "Intel Iris Xe" --machine-id laptop

Import the CSV downloaded from Showcase A bench mode (rows are re-validated):
  python bench/add_row.py --import-a ~/Downloads/bench_rows.csv
"""
import argparse
import csv
import json
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
RESULTS = HERE / "results" / "results.csv"
HEADER = ("timestamp,machine_id,browser,gpu_renderer,showcase,condition,dataset,size,rep,ttfr_ms,"
          "fps_median,fps_p5,client_mem_mb,server_rss_mb,ws_bytes,triangles,geometry_kb,"
          "network_profile,notes").split(",")
CONDITIONS = {"A-local": "A", "B-local": "B", "B-remote": "B", "B-remote-lowres": "B", "B-wasm": "B"}
SIZES = {64, 128, 256, 384}
NUMERIC = {"size": int, "rep": int, "ttfr_ms": float, "fps_median": float, "fps_p5": float,
           "client_mem_mb": float, "server_rss_mb": float, "ws_bytes": int, "triangles": int,
           "geometry_kb": float}
REQUIRED = ["machine_id", "browser", "showcase", "condition", "dataset", "size", "rep",
            "ttfr_ms", "fps_median"]


def default_machine():
    return socket.gethostname()


def validate(row):
    """Return a cleaned row (all values str) or raise ValueError listing every problem."""
    errs = []
    out = {c: str(row.get(c, "") if row.get(c) is not None else "").strip() for c in HEADER}
    if not out["timestamp"]:
        out["timestamp"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for c in REQUIRED:
        if not out[c]:
            errs.append(f"missing {c}")
    if out["condition"] and out["condition"] not in CONDITIONS:
        errs.append(f"condition must be one of {sorted(CONDITIONS)}")
    elif out["condition"] and out["showcase"] and CONDITIONS[out["condition"]] != out["showcase"]:
        errs.append(f"condition {out['condition']} belongs to showcase {CONDITIONS[out['condition']]}")
    for c, typ in NUMERIC.items():
        if out[c]:
            try:
                v = typ(float(out[c])) if typ is int else typ(out[c])
                if v < 0:
                    errs.append(f"{c} must be >= 0")
                out[c] = str(v)
            except ValueError:
                errs.append(f"{c} is not a number: {out[c]!r}")
    if out["size"] and out["size"].isdigit() and int(out["size"]) not in SIZES and \
            out["dataset"].startswith(("wavelet", "foot")):
        errs.append(f"size should be one of {sorted(SIZES)}")
    try:
        if out["fps_median"] and out["fps_p5"] and float(out["fps_p5"]) > float(out["fps_median"]):
            errs.append("fps_p5 cannot exceed fps_median")
    except ValueError:
        pass
    if not out["network_profile"]:
        out["network_profile"] = "none"
    if errs:
        raise ValueError("; ".join(errs))
    return out


def append(rows, path=RESULTS):
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists() or path.stat().st_size == 0
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        if new:
            w.writeheader()
        w.writerows(rows)
    return len(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--import-a", metavar="CSV", help="rows downloaded from Showcase A bench mode")
    ap.add_argument("--csv", type=Path, default=RESULTS, help="target file (default bench/results/results.csv)")
    for c in HEADER:
        ap.add_argument("--" + c.replace("_", "-"), dest=c)
    a = ap.parse_args()

    if a.import_a:
        with open(a.import_a, newline="") as f:
            src = list(csv.DictReader(f))
        cleaned, bad = [], 0
        for i, r in enumerate(src, 1):
            try:
                cleaned.append(validate(r))
            except ValueError as e:
                bad += 1
                print(f"row {i}: {e}", file=sys.stderr)
        if bad:
            sys.exit(f"{bad} invalid row(s); nothing written")
        print(f"appended {append(cleaned, a.csv)} row(s) to {a.csv}")
        return

    row = {c: getattr(a, c) for c in HEADER}
    row["machine_id"] = row["machine_id"] or default_machine()
    try:
        cleaned = validate(row)
    except ValueError as e:
        sys.exit(f"invalid row: {e}")
    append([cleaned], a.csv)
    print(f"appended 1 row to {a.csv}: {cleaned['condition']} {cleaned['dataset']} size={cleaned['size']} rep={cleaned['rep']}")


if __name__ == "__main__":
    main()
