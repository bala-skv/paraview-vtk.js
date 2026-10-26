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


def download(url, dest):
    last = None
    for attempt in range(3):
        try:
            tmp = dest.with_suffix(dest.suffix + ".part")
            with urllib.request.urlopen(url, timeout=60) as r, open(tmp, "wb") as f:
                while chunk := r.read(1 << 20):
                    f.write(chunk)
            tmp.replace(dest)
            return
        except Exception as e:  # noqa: BLE001
            last = e
            wait = 2 ** (attempt + 1)
            print(f"  attempt {attempt + 1}/3 failed: {e}; retrying in {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise SystemExit(f"FAIL: could not download {url}: {last}")


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
