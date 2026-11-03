# Provenance and changes from upstream

Upstream: [zhongerxin/iPhone-use](https://github.com/zhongerxin/iPhone-use), version 0.3.16, commit `3ce9c080534e89fab91a237bf1c53a4a7e9d80a7`.

This independent private repository starts from that source snapshot. It is not part of GitHub's public fork network. Original copyright and the MIT licence are preserved in [LICENSE](LICENSE); dependencies retain their respective licences.

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

The reviewed diff is in [patches/wda-loopback.patch](patches/wda-loopback.patch). [server/wda_hardening.py](server/wda_hardening.py) verifies the original and patched file hashes. Unrecognised modifications are rejected rather than reset. No signing identity, personal device identifier, Apple credential, or provisioning profile is included in this repository.

Changes from upstream must be reviewed deliberately. Updating a pinned revision requires updating the approved patch, hashes, dependencies, and validation evidence together.
