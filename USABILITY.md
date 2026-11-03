# Usability work — 0.5.0 candidate

All changes are developed in an isolated checkout. The installed 0.4.0 plugin and the original checkout are unchanged. `feat/usability-integration` combines the work; it is a testing candidate and is not merged to main.

## Independent first five branches

| Branch | Change |
| --- | --- |
| `feat/batch-workflow` | `pua_batch` adds top-level `observe` and `compact` options. Known steps can return one final observation. Error, uncertainty, input-continuation and submission barriers remain. `compact=false` retains diagnostic detail. |
| `perf/usb-connection-reuse` | One bounded serial keep-alive USB HTTP connection, with per-request authentication and no request replay on failure. |
| `perf/preview-geometry-cache` | A 10-second cache is used only when a fresh stream frame agrees with pointer geometry. Missing/stale geometry and rotation force native reads. Uncertain gestures invalidate the cache. |
| `feat/adaptive-preview` | Auto requests 2 FPS idle and 8 FPS near activity. Eco requests 2 FPS; Fast requests 8 FPS. Viewer pacing follows capture. Settings changes defer while input is busy. The rate is a limit, not a delivered-FPS guarantee. |
| `fix/first-device-setup` | Accept missing CoreDevice `reality`, continue rejecting explicit simulators, and include first-device provisioning registration in Xcode builds. |

These five branches independently start at main commit `1b2fa1e`. Later usability branches are stacked on the integration work because they share runtime, preview and authentication boundaries.

## Selected upstream work

| Branch | Upstream basis | Adaptation |
| --- | --- | --- |
| `fix/usable-targets` | #34, #35 | Native switch selection and one bounded lift of covered list content before resolving again. No repeated blind scrolling. |
| `fix/authentication-pause-gate` | #45 | Pause blocks reads/actions across local conversations and discards stale queued work and responses. Explicit UI takeover, private export guards and English UI are retained. |
| `fix/preview-device-identity` | #53 | Retry metadata discovery, reject old lookup generations and clear another phone's retained pixels. |
| `feat/startup-diagnostics` | #26 | Preserve early runner evidence and distinguish exit codes; broader host logs are opt-in. |

PR #44's loopback boundary was already implemented by this fork. PR #41's geometry idea is covered by the cache; its async gesture routes no longer match its runner dependency. Photo import (#32), device leases (#52), automatic authentication recovery (#46), wireless transports, Android and Windows remain separate future milestones. They expand runtime/permission/platform behaviour beyond this first usability candidate.

## Use the batch improvement

```json
{
  "steps": [
    {"op": "tap", "args": {"selector": {"label": "Known field"}}},
    {"op": "type_text", "args": {"text": "The full intended text"}}
  ],
  "observe": "tree"
}
```

This is for already known steps. Inspect unfamiliar pages before building a batch. A completed batch with `observation_error` or `observation_pending` requires a fresh observation, not replay of its completed actions.

## Controlled physical acceptance still required

Use a dedicated test session after switching to this candidate. Verify Calculator results, compare whole-task time and tool round-trip counts, try repeated selector/preview taps, rotate the phone, exercise Auto/Eco/Fast, and run a sustained preview/control session. Test pause during a pending read and during an action; private pixels and queued work must not reappear after resume. Verify resume needs fresh state, and stop/restart only the owned job. Test the first-device setup path on an unregistered test device.

No physical speedup or measured delivered frame rate is claimed by these code changes. Regression results are recorded in TESTING.md.
