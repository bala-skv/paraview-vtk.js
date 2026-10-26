"""Download raw datasets listed in manifest.json into data/raw/. Standard library only.

  python data/fetch_data.py [--only foot,tooth]
"""
import argparse
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
MANIFEST = HERE / "manifest.json"
RAW = HERE / "raw"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def raw_path(ds):
    return RAW / ds["url"].rsplit("/", 1)[1]


MIN_BPS = 50_000  # abort an attempt that averages less than this over STALL_WINDOW seconds
STALL_WINDOW = 20


def download(url, dest, attempts=6):
    """Resumable (HTTP Range) download that gives up on a trickling connection instead of hanging."""
    tmp = dest.with_suffix(dest.suffix + ".part")
    last = None
    for attempt in range(attempts):
        try:
            have = tmp.stat().st_size if tmp.exists() else 0
            req = urllib.request.Request(url, headers={"Range": f"bytes={have}-"} if have else {})
            with urllib.request.urlopen(req, timeout=30) as r:
                if have and r.status != 206:  # server ignored Range: start over
                    have = 0
                t0, b0 = time.monotonic(), have
                with open(tmp, "ab" if have else "wb") as f:
                    while chunk := r.read(1 << 16):
                        f.write(chunk)
                        have += len(chunk)
                        dt = time.monotonic() - t0
                        if dt > STALL_WINDOW and (have - b0) / dt < MIN_BPS:
                            raise TimeoutError(f"too slow ({(have - b0) / dt / 1000:.0f} kB/s)")
            tmp.replace(dest)
            return
        except Exception as e:  # noqa: BLE001
            last = e
            wait = min(2 ** (attempt + 1), 15)
            print(f"  attempt {attempt + 1}/{attempts} failed at {tmp.stat().st_size if tmp.exists() else 0} bytes: "
                  f"{e}; retrying (resume) in {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise SystemExit(f"FAIL: could not download {url}: {last}\n"
                     f"Fallback: copy the file into data/raw/ by hand (checksum is verified on the next run).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="comma-separated dataset names")
    args = ap.parse_args()
    only = set(args.only.split(",")) if args.only else None

    manifest = json.loads(MANIFEST.read_text())
    RAW.mkdir(exist_ok=True)
    changed = False
    for ds in manifest["datasets"]:
        if only and ds["name"] not in only:
            continue
        dest = raw_path(ds)
        expected = ds["sha256"]
        if dest.exists() and (not expected or sha256(dest) == expected):
            if not expected:
                ds["sha256"], changed = sha256(dest), True
            print(f"skip {ds['name']} (present)")
            continue
        print(f"download {ds['name']} <- {ds['url']}")
        download(ds["url"], dest)
        digest = sha256(dest)
        if not expected:
            ds["sha256"], changed = digest, True
            print(f"  recorded sha256 {digest[:12]}...")
        elif digest != expected:
            dest.unlink()
            raise SystemExit(f"FAIL: checksum mismatch for {ds['name']}: {digest} != {expected}")
        n = ds["dims"][0] * ds["dims"][1] * ds["dims"][2]
        if dest.stat().st_size != n:
            raise SystemExit(f"FAIL: {dest.name} is {dest.stat().st_size} bytes, expected {n}")
    if changed:
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
        print("manifest.json updated with checksums; commit it")


if __name__ == "__main__":
    main()
