# Provenance and changes from upstream

Upstream: [zhongerxin/iPhone-use](https://github.com/zhongerxin/iPhone-use), version 0.3.16, commit `3ce9c080534e89fab91a237bf1c53a4a7e9d80a7`.

This independent MIT-licensed derivative starts from that source snapshot and is maintained at [bal-r/eu-iphone-use](https://github.com/bal-r/eu-iphone-use). Original copyright and the MIT licence are preserved in [LICENSE](../LICENSE); dependencies retain their respective licences.

The upstream telemetry was documented. Its presence is not evidence that its author inserted malware. This derivative makes different product and privacy decisions and describes only the behaviour it can substantiate.

## Balta Tech 0.4.0

- Removed the complete telemetry module, PostHog/Google Analytics configuration, app-launch tracking, installation tracking identity, analytics tests, and dashboard files.
- Removed online Apple app searches. App discovery uses the device and a small offline reference.
- Restricted WebDriverAgent HTTP and MJPEG listeners to phone loopback. Removed permissive upstream CORS headers. The supplied deterministic patch is accepted only for the exact pinned source and is reverified before builds and startup.
- Replaced the Mac's unauthenticated raw forwarder with a loopback HTTP proxy requiring a private random capability. Browser Origin headers are rejected and credentials/CORS headers are not forwarded to WDA clients.
- Separated private runtime state from upstream installations.
- Delete process-owned observation images on normal shutdown; document crash leftovers and intentional screenshot copies.
- Removed unrelated host adapters, experiments, product-specific operation notes, promotional screenshots, and online catalog maintenance code.
- Rewrote the installation and privacy documentation in English and translated preview controls. Preserved Unicode input support and the original task/recovery functionality.
- Refreshed dependency lockfiles and added focused privacy, proxy, and WDA-patch regression checks.

The `pua_` tool names remain compatible with existing Codex workflows. The separate `balta_iphone_use` MCP namespace and Balta Tech marketplace avoid replacing the upstream registration.

## WebDriverAgent

The phone runner derives from [Appium WebDriverAgent](https://github.com/appium/WebDriverAgent), version 16.14.0, commit `d17782422d55ff1e5e0ceb74eb1fd509cc0c35b6`.

The reviewed diff is in [patches/wda-loopback.patch](../patches/wda-loopback.patch). [server/wda_hardening.py](../server/wda_hardening.py) verifies the original and patched file hashes. Unrecognised modifications are rejected rather than reset. No signing identity, personal device identifier, Apple credential, or provisioning profile is included in this repository.

Changes from upstream must be reviewed deliberately. Updating a pinned revision requires updating the approved patch, hashes, dependencies, and validation evidence together.

## Balta Tech 0.5.0 usability candidate

The upstream base remains 0.3.16; this release selectively adapts contributions rather than updating to unreviewed upstream code.

- Independent branches add compact batch results with one final observation, authenticated USB connection reuse without action replay, fresh-frame-validated geometry caching, adaptive preview capture/pacing, and first-device setup fixes from issues [#37](https://github.com/zhongerxin/iPhone-use/issues/37) and [#38](https://github.com/zhongerxin/iPhone-use/issues/38).
- Adapted native switch targeting and bounded covered-row recovery from PRs [#34](https://github.com/zhongerxin/iPhone-use/pull/34) and [#35](https://github.com/zhongerxin/iPhone-use/pull/35); narrow switch geometry is clamped within its bounds.
- Adapted the cross-process authentication pause and stale-response gate from PR [#45](https://github.com/zhongerxin/iPhone-use/pull/45), preserving our proxy authentication and telemetry removal. Added an explicit Pause/Resume button and guarded CLI image export. Refresh cannot resume authentication.
- Adapted model-identity refresh, retry and old-device frame invalidation from PR [#53](https://github.com/zhongerxin/iPhone-use/pull/53). No additional hardware-model claims are introduced.
- Adapted startup failure evidence from PR [#26](https://github.com/zhongerxin/iPhone-use/pull/26). Unlike that proposal, broader host log capture is opt-in in this fork; private failure reports remain local.

Original and contributing authors retain their MIT attribution. The phone runner revision and loopback patch are unchanged. See [USABILITY.md](usage.md) for branch boundaries, integration and physical acceptance work.

## Balta Tech 0.6.1 Codex integration candidate

- Added a stable, version-aware compatibility launcher and optional plugin-native registration.
- Shortened initial MCP instructions; added cancellation, content-free progress, typed results and bounded optional selector taps.
- Added private per-device ownership with idle/crash release and optional reviewed Stop/Interrupt hooks. This is an independent implementation of the coordination need discussed in upstream PR #52.
- Added Point mode to share a user-selected target through MCP Apps context without sending a phone gesture.
- Preserved older-host image content and added persistent guarded CLI sessions.
- Fixed local marketplace moves, setup-error normalisation and concurrent lease initialisation during acceptance review.

These changes do not introduce telemetry, a cloud relay, a new phone runner, automatic authentication bypass, or broader host logging. Local ownership metadata is described in [PRIVACY.md](privacy.md). Actual checks and remaining physical/host limitations are recorded in [TESTING.md](testing.md).
