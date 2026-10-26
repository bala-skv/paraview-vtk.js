# Results (median over repetitions)

| condition | size | reps | ttfr_ms | fps_median | fps_p5 | client_mem_mb | server_rss_mb | ws_bytes | triangles | geometry_kb |
|---|---|---|---|---|---|---|---|---|---|---|
| A-local | 64 | 3 | 215.5 | 59.9 | 59.5 | 19.6 |  |  |  |  |
| A-local | 128 | 3 | 107.2 | 59.9 | 59.5 | 21.3 |  |  |  |  |
| A-local | 256 | 3 | 434.5 | 30.0 | 25.6 | 41.0 |  |  |  |  |
| B-local | 64 | 3 | 376.0 | 60.0 | 60.0 | 10.4 | 709.3 | 0.0 | 66,260.0 | 2,991.0 |
| B-local | 128 | 3 | 357.0 | 60.0 | 60.0 | 11.7 | 757.4 | 0.0 | 272,634.0 | 12,279.0 |
| B-local | 256 | 3 | 356.0 | 60.0 | 60.0 | 11.7 | 958.4 | 0.0 | 1,103,026.0 | 49,615.0 |
| B-remote | 64 | 3 | 400.0 | 20.0 | 20.0 | 10.5 | 732.0 | 3,920,535.0 | 66,260.0 | 2,991.0 |
| B-remote | 128 | 3 | 366.0 | 20.0 | 19.0 | 9.9 | 777.8 | 3,977,234.0 | 272,634.0 | 12,279.0 |
| B-remote | 256 | 3 | 374.0 | 21.0 | 20.0 | 11.2 | 979.5 | 4,034,738.0 | 1,103,026.0 | 49,615.0 |

Validity limits: localhost has almost no network latency (flatters remote rendering); Showcase A renders a volume and B an isosurface, so their FPS values are not comparable.
