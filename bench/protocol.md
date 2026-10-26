# Benchmark protocol

Goal: fill `bench/results/results.csv` with **3 repetitions** for each cell below, then run
`plot_results.py`. Budget: about 1.5 h on a GPU laptop.

| Condition | Showcase | Sizes | Cells x reps |
| --- | --- | --- | --- |
| A-local | A | foot_64, foot_128, foot_256 | 3 x 3 (automated) |
| B-local | B | wavelet 64³, 128³, 256³ | 3 x 3 |
| B-remote | B | wavelet 64³, 128³, 256³ | 3 x 3 |

Do **not** rank A against B: A renders a volume, B an isosurface. State the localhost caveat
(near-zero network latency flatters remote rendering) in the report.

## 0. One-time setup (10 min)

1. Plug the laptop into mains power, set the OS power mode to "performance", close other apps
   (browsers, IDEs, video calls). Use Chrome or Edge (current), **one** window, 1280 x 720
   (DevTools undocked, or closed during runs).
2. Check `chrome://gpu`. "WebGL2: Hardware accelerated" must show. If it says software or
   SwiftShader, fix drivers first. Note the exact renderer string (also shown in the Showcase A
   info panel). It goes into `gpu_renderer` and the report.
3. `cd` to the repo root and run `.venv/bin/python bench/sysinfo.py`
   (Windows: `.venv\Scripts\python bench\sysinfo.py`). It writes `bench/results/sysinfo.json`.
4. Pick a `machine_id` (for example `laptop-a`) and use it in every row.

## 1. A-local (automated, 15 min)

For each size, one command; the page reloads itself 3 times (cold start each time):

```
http://localhost:5173/?bench=1&data=foot_64.vti&frames=360&reps=3&machine=laptop-a&restart=1
http://localhost:5173/?bench=1&data=foot_128.vti&frames=360&reps=3&machine=laptop-a&restart=1
http://localhost:5173/?bench=1&data=foot_256.vti&frames=360&reps=3&machine=laptop-a&restart=1
```

Start Showcase A with `scripts/run_a.sh` (or `.ps1`). When the overlay says "bench complete",
click **Download CSV**, then import it:

```
.venv/bin/python bench/add_row.py --import-a ~/Downloads/bench_rows.csv
```

Important: the `bench_rows` list in localStorage accumulates across sizes, so downloading after the
third size gives **all 9 rows in one file**; download once at the end, or clear it with
`localStorage.removeItem('bench_rows')` in the console between sizes. Do not import the same file twice.
FPS is paced by `requestAnimationFrame`, so it is capped by the display refresh rate (60 or 144 Hz); say
so in the report. For a run that can exceed the cap, note it in `notes`.

## 2. B-local and B-remote

Start the server for each size and mode, for example:

```
scripts/run_b.sh --size 128 --mode remote      # or: --mode local
```

(The Local rendering switch also changes the mode live, but restarting per cell gives a cold start.)
Open http://localhost:8080 in a **fresh** tab with DevTools closed.

### Option 1, scripted (recommended: same mouse path every time)

```
cd bench && npm ci            # once
node auto_b.mjs --mode remote --size 128 --rep 1      # opens Chrome, orbits 10 s, prints numbers
```

Use the server from step 2 (`scripts/run_b.sh` running). The script prints a ready `add_row.py` command; replace `<fill>` with your GPU
string and machine id. What it measures:

* `ws_bytes`: bytes of all WebSocket frames received and sent during the 10 s orbit.
* FPS: remote = binary image frames received per second; local = page animation frames per second
  (vtk.js renders on every mouse event, so this is the client render rate). `fps_p5` here is the
  **minimum of the 1 s bins**, a coarse stand-in for the 5th percentile; say so in the report.
* `ttfr_ms`: from navigation start until the trame state has triangles and a canvas exists. Compare
  with the server log line `[bench] first client connected ... ms after server start`.
* Triangles, geometry KB and server RSS come from the app's own stats.

### Option 2, manual with DevTools

1. Open DevTools. **Network**: tick Disable cache, filter WS, reload the page; note the time of the first
   `101` WebSocket row and the first image (remote) as `ttfr_ms`.
2. **Rendering** tab: tick "Frame Rendering Stats".
3. Orbit with the left mouse button for 10 s in steady circles. Read the FPS overlay every second
   (10 readings). `fps_median` is the median, `fps_p5` the lowest reading.
4. `ws_bytes`: Network, WS row, Messages: the sum of the sizes of the messages in those 10 s
   (select the row range; or use Option 1, which does this for you).
5. Client memory: Chrome Task Manager (Shift+Esc), the tab's "Memory footprint".
6. Server numbers: copy `triangles`, `geometry_kb` and RSS from the Server stats card.

### Also for B-remote

Press **Benchmark orbit** (remote mode only). The card shows total time and ms per step, and a row `orbit`
is appended to `bench/results/server_events.csv`. Add the per-step ms to `notes`. This is the server's
upper bound on frame rate (no browser involved), useful next to the browser-measured FPS.

## 3. Record every run

```
.venv/bin/python bench/add_row.py --showcase B --condition B-remote --dataset wavelet --size 128 \
    --rep 1 --ttfr-ms 850 --fps-median 24 --fps-p5 18 --client-mem-mb 310 --server-rss-mb 745 \
    --ws-bytes 18400000 --triangles 114560 --geometry-kb 5226 --browser "Chrome 151" \
    --gpu-renderer "<chrome://gpu string>" --machine-id laptop-a --notes "wired, power on"
```

`add_row.py` validates every row (allowed conditions, numeric fields, p5 <= median) and refuses bad rows.
Write anything odd (thermal throttling, tab suspended, background update) in `--notes`. Never edit
`results.csv` by hand.

## 4. Build figures and tables

```
.venv/bin/python bench/plot_results.py
```

Outputs `fig_fps_by_size.png`, `fig_ttfr_bytes.png` and `results_table.md` in `bench/results/figures/`,
copied to `report/figures/`.

## 5. Checklist

- [ ] `sysinfo.json` written; GPU shows hardware WebGL2
- [ ] 9 A-local rows, 9 B-local rows, 9 B-remote rows (3 reps x 3 sizes each)
- [ ] `server_events.csv` has orbit rows for B-remote
- [ ] Figures regenerated after the last row
- [ ] Notes list anything unusual; validity limits are stated in the report
