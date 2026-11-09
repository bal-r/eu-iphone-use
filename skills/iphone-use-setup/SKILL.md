---
name: iphone-use-setup
description: Configure the user's USB-connected iPhone with the hardened Balta Tech runner, their own Apple signing identity, and an authenticated local connection.
---

# Set up Balta Tech iPhone Use

This private derivative has no product telemetry. Read the repository README, docs/setup.md, docs/privacy.md, .github/SECURITY.md, and docs/testing.md when explaining installation or limitations. The user authorises a scoped task on their own phone; no other apps or accounts are implied.

1. Start with `pua_setup(action="status")`. Reuse a healthy managed service or an active owned job. Do not reuse an unverified external runner. Do not infer that a service has stopped from a timeout.
2. For first setup, use `pua_doctor` and `pua_setup(action="discover")`. Confirm full Xcode and the selected physical phone. Never use sample device IDs, another person's signing team, or copied credentials.
3. The user completes Apple login, two-factor authentication, USB trust, Developer Mode, certificate trust, and phone unlock directly in system UI. Explain the exact requested step, pause screen observation for authentication, and wait for their actual completion response.
4. Configure the explicit device ID, the user's own Apple Team ID, and a unique reverse-DNS bundle identifier with `pua_setup(action="configure", ...)`.
5. Use `pua_setup(action="fetch")`. It downloads the pinned phone-runner source and applies the supplied, hash-verified loopback patch. Unrecognised changes are rejected and preserved. Do not remove the source-integrity check or start an unpatched runner.
6. Build with `pua_setup(action="build")`. Poll its job rather than starting duplicate builds. Signing uses the user's existing Xcode identity. Free Personal Team provisioning expires after seven days; do not promise permanent signing.
7. Start with `pua_setup(action="start")`. The bounded wait defaults to 20 seconds. Poll `pua_setup(action="status", job_id=..., wait_seconds=20)` until it is ready. A pending job is unfinished work, not a reason to reinstall.
8. Require `pua_ready(recover=true, screenshot=false)` to return `ready=true` with a fresh UI observation. Status alone is not proof of UI authority.
9. Open the preview with `pua_screen` if it is not already present. Use Calculator to verify `12 × 34 = 408`, inspect the actual result, and report exactly what was tested. Physical-device acceptance in docs/testing.md remains separate from build success.
10. When the task is finished, stop only the owned job with `pua_setup(action="stop")`. Verify shutdown and ask the user to disconnect USB when no more phone work is authorised.

The local proxy requires a private token in the runtime directory. Never print it, put it in chat, commit it, or send it to a network service. Device and signing state stay outside Git. There is no analytics opt-in to configure.

Use narrow recovery: `pua_timeout` is not proof of disconnection. Honor diagnostic-only or no-restart instructions. Do not kill unrelated processes, delete other development apps, bypass trust prompts, or change signing identities to work around a failure.
