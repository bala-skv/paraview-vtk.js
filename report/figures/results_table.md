# Results (median over repetitions)

| condition | size | reps | ttfr_ms | fps_median | fps_p5 | client_mem_mb | server_rss_mb | ws_bytes | triangles | geometry_kb |
|---|---|---|---|---|---|---|---|---|---|---|
| A-local | 64 | 3 | 215.5 | 59.9 | 59.5 | 19.6 |  |  |  |  |
| A-local | 128 | 3 | 107.2 | 59.9 | 59.5 | 21.3 |  |  |  |  |
| A-local | 256 | 3 | 434.5 | 30.0 | 25.6 | 41.0 |  |  |  |  |

Validity limits: localhost has almost no network latency (flatters remote rendering); Showcase A renders a volume and B an isosurface, so their FPS values are not comparable.
