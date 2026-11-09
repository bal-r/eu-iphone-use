# Performance improvements and estimates

EU iPhone Use 0.6.1 reduces orchestration calls, repeated USB connection setup, redundant geometry queries, and idle preview capture. This document separates implemented behaviour, a recorded device baseline, and calculated planning estimates.

## Implemented improvements

| Area | Behaviour in 0.6.1 | Source |
| --- | --- | --- |
| Batching | Up to 20 known steps in one tool call; top-level `observe` adds one final observation. Compact output removes repeated target detail. | `server/wda_controller.py`, `Phone.batch` |
| USB HTTP | One serial keep-alive connection per proxy; each incoming request authenticates. Failed requests are reported without replay. | `tooling/proxy.mjs` |
| Model-facing HTTP | Persistent local HTTP transport, bounded deadlines, and a retry only for eligible reads. | `server/wda_client.py` |
| Geometry | Cache for 10 seconds, accepted only with matching fresh frame geometry; rotation and stale information force refresh. | `server/iphone_use.py`, `Runtime.screen_gesture`; `server/wda_screen.py`, `ScreenHub.fresh_geometry` |
| Preview | Auto requests 2 FPS idle and 8 FPS around activity; Eco 2 FPS; Fast 8 FPS. | `server/iphone_use.py`, `Runtime.screen_gesture`; `ui/src/app.ts` |
| Tree reads | Exclude expensive visibility/accessibility attributes by default; reuse app and viewport data from the source where available. | `server/wda_controller.py`, `Phone.tree` |
| App resolution | Installed-device inventory has a five-minute local cache; no online catalog lookup. | `server/wda_apps.py` |
| Session lifecycle | Release ownership without stopping the runner; 60-second idle lease expiry. | `server/device_lease.py`, `USABILITY.md` |

Batching preserves errors, uncertainty, input continuation, cancellation, and submission barriers. It is intended for known steps. Removing intermediate model decisions does not remove the need to inspect unfamiliar screens.

## Recorded physical baseline

On 3 November 2026, the 0.4.0 runner completed `12 × 34 = 408` in Calculator using seven taps and a final tree observation. The metrics recorded **5.2074 seconds and 23 HTTP requests**. Use **5.2 seconds** in articles. This is tool-layer execution time, excluding model reasoning and host scheduling.

The 0.6.1 integration records 514 passing Python tests, 65 widget tests, 6 authenticated proxy/transport tests, and successful stdio startup/catalog/ping checks. Physical candidate timing remains pending after an XCTest automation-mode startup failure. See [TESTING.md](TESTING.md).

## Absolute workflow estimate

Use this statement in explanatory copy:

> For a known seven-tap workflow followed by a screen read, batching removes seven model/tool handoffs. At three seconds per handoff, that saves 21 seconds of orchestration waiting.

This is a planning calculation, not a measured 0.6.1 speedup. The comparison is eight separate model-visible tool calls versus one batch with a final observation. Both paths perform the same phone actions; phone execution is held constant.

| Scenario | Separate calls | One batch | Estimated time saved |
| --- | --- | --- | --- |
| 1 second per handoff | 8 seconds of orchestration | 1 second | 7 seconds |
| 3 seconds per handoff | 24 seconds of orchestration | 3 seconds | 21 seconds |
| 5 seconds per handoff | 40 seconds of orchestration | 5 seconds | 35 seconds |

With the recorded 5.2-second phone baseline held constant and three seconds per call, the illustrative total is **29.2 seconds versus 8.2 seconds**. This model isolates orchestration savings; it does not predict actual 0.6.1 device latency. Saving 21 seconds on 20 comparable sequences is **7 minutes per day**, or **35 minutes across five working days**.

## Preview work in absolute terms

At the configured limits, 8 FPS requests up to 480 frames per minute and 2 FPS up to 120: **360 fewer requested frames per idle minute**, or **3,600 fewer across ten idle minutes**. This is a 75% reduction in the configured capture rate relative to Fast mode. It is not a measurement of delivered FPS, network bytes, battery life, or CPU use.

Do not add an invented percentage speedup for USB connection reuse or geometry caching. Their concrete benefit is fewer connection establishments and fewer repeated native reads. The source establishes the mechanism; a comparison run establishes elapsed-time improvement.

## Reproduce a device comparison

`scripts/benchmark.py` measures app opening, page reads and scrolling, list collection, long text input with readback, and a screenshot in Settings. Run it only during a dedicated session on your own unlocked test phone; it operates the phone and clears its test search input.

```sh
python3 scripts/benchmark.py --run --pages 10 --characters 600
```

Use the same Mac, phone, app state, runner build, preview preset, and task on each version. Keep raw results outside Git. Compare whole-task seconds, model-visible calls, HTTP requests, and response bytes. Report the median of five completed runs alongside failures. Use `pua_metrics` for session timing; the benchmark script alone does not measure model reasoning time.
