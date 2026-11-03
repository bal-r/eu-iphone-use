# Changes

## 0.6.0 — Codex integration

- Stable version-aware MCP registration, concise initial instructions and visible server version.
- Cancellation of queued/remaining steps, uncertain in-flight writes and content-free progress.
- Shared phone ownership, idle/crash release and optional reviewed Stop/Interrupt hooks.
- User-selected target context from the preview without phone input.
- Typed result outcomes, bounded optional selector taps and persistent CLI sessions.


## 0.5.0 — usability candidate

- Compact known-step batches can return a final observation without another agent call.
- Reuse the authenticated USB HTTP connection; failed writes are never automatically replayed.
- Reuse preview geometry while fresh frame dimensions agree; refresh after rotation or stale metadata.
- Add Auto / Eco / Fast preview pacing and capture presets, frame age and explicit Pause/Resume takeover.
- Support missing CoreDevice reality metadata and first-time signing-device registration.
- Improve native switch targeting, covered-row recovery, cross-process authentication pauses, preview identity refresh and private startup diagnostics.
- Broader host diagnostic logging remains off unless explicitly enabled.

This candidate is validated with isolated regression fixtures. It has not yet undergone a physical-phone performance or takeover acceptance session.

## 0.4.0 — Balta Tech private derivative

Removed upstream product telemetry, tracking configuration, dashboards, online app search, and unused host adapters. Added hash-verified phone loopback hardening, an authenticated browser-resistant Mac USB proxy, separate private runtime state, and observation-image cleanup on orderly shutdown.

Rewrote privacy and setup documentation, translated preview controls, refreshed dependencies, and added focused regression checks. See [UPSTREAM.md](UPSTREAM.md) for provenance and the complete material changes, and [TESTING.md](TESTING.md) for the actual validation state.
