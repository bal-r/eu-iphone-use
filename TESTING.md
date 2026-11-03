# Validation status

This document records the original Balta Tech 0.4.0 acceptance evidence and the separate 0.5.0 usability candidate checks. It is updated when validation completes. Physical-device testing is a distinct acceptance step and must not be inferred from unit tests or an unsigned build.

## 0.5.0 usability candidate — 3 November 2026

The isolated `feat/usability-integration` checkout passes:

| Check | Result |
| --- | --- |
| Complete Python regression suite | 500 passed |
| Authenticated proxy/transport fixtures | 6 passed; sequential read/write connection reuse and no replay after interrupted mutation verified |
| Widget DOM and interaction tests | 63 passed |
| UI typecheck and self-contained production bundle | Passed |
| Plugin manifests, tool-schema budgets and package round-trip | Passed |
| Real stdio MCP startup/catalog/ping smoke | Passed; version 0.5.0, 20 tools |
| Whitespace/diff check | Passed |

The tests use temporary runtime directories and synthetic phone/Xcode endpoints. No connected iPhone was operated, no installed plugin was replaced, and no service was restarted for this work. The phone runner revision, loopback patch and third-party dependency versions are unchanged.

Physical acceptance of 0.5.0 remains pending: sustained preview/control operation, actual delivered frame rates and end-to-end task latency, rotation, cross-process authentication takeover, stop/reconnect, and first-device signing registration. The 0.4.0 physical results below do not establish these new behaviours. See [USABILITY.md](USABILITY.md).

## Original 0.4.0 automated checks

Validated locally on 3 November 2026 (Mac, Xcode 26.2, Python 3.14.0, Node.js 25.6.0):

| Check | Result |
| --- | --- |
| Python regression suite | 450 passed |
| Preview typecheck and production build | Passed; self-contained asset rebuilt |
| Widget DOM and interaction tests | 57 passed |
| Authenticated USB-proxy tests | 4 passed, including Python transport integration |
| Plugin manifests, schemas, package round-trip and resource serving | Passed |
| Current npm audit, both lockfiles | Zero known vulnerabilities reported |
| Current OSV scan | 265 dependency/version combinations checked; zero matches |
| Pinned, hardened WDA integrity | Approved hash verified before compilation |
| Unsigned iPhoneOS Xcode build-for-testing | TEST BUILD SUCCEEDED |
| Real USB library import with production install flags | Passed |

The proxy's initial boundary tests also passed with an OS network policy allowing loopback fixtures and blocking external networking. The complete native macOS regression suite was run in the normal local test environment. No personal phone data, device signing identity, or Apple credentials were used by these checks.

These results establish a candidate ready for controlled physical-device acceptance. They do not establish device pairing, personal-team signing, installation, Wi-Fi isolation on a particular phone, or compatibility with a personal app such as Hinge. Advisory databases and dependency risk can change after this date.

## Physical-device acceptance

First device acceptance session completed on 3 November 2026 with an iPhone 16 Pro Max running iOS 27.0.1, using Xcode 26.2 and the user's own development team. No signing-team ID, device UDID, certificate, profile, or captured phone image is stored in this repository.

Verified during that session:

- The selected phone was connected over USB, paired, and had Developer Mode enabled.
- The hardened runner built with development signing, installed, and started successfully.
- `pua_ready` returned `ready=true` with a usable session, an unlocked phone, readable UI source, and a valid viewport.
- Calculator was found from the installed-device inventory and launched with foreground verification.
- Seven known keypad actions produced `12 × 34 = 408`; both the accessibility result and a fresh screenshot confirmed it.
- TCP connections to the phone's Wi-Fi address on ports 8100 and 9100 were refused.
- An unauthenticated request to the Mac's local proxy returned HTTP 403.
- The installed MCP entrypoint exposed 20 tools and its preview resource. The chat used the reviewed CLI fallback because newly installed MCP bindings were not loaded into the existing chat.

The temporary Calculator exports were removed after inspection. The USB service was intentionally left running at the user's request to start the connection. Native chat-preview rendering, a manual phone-lock/authentication handoff, and an explicit stop/restart acceptance cycle remain untested on this physical phone. Hinge editing has not yet been tested.

The full acceptance checklist remains below; the items above are the checks with actual device evidence.

1. Pair the user's phone through Xcode and enable Developer Mode in Apple's UI.
2. Configure the user's explicit device, Apple team, and unique bundle identifier. Build, sign, install, and start the exact hardened runner.
3. Verify the authenticated Mac connection and require `pua_ready` to report `ready=true` with a fresh UI observation.
4. Use Calculator to verify `12 × 34 = 408`, including a screenshot of the result.
5. Confirm preview pause/resume around a manual phone unlock. Do not collect passwords or passcodes.
6. Verify that the phone HTTP and MJPEG services are not accessible through the phone's Wi-Fi address. This must be performed as an explicit test of the user's own phone; source-level loopback checks alone are not device evidence.
7. Confirm that no telemetry module, telemetry identity, or analytics traffic is created. Distinguish setup downloads and AI-provider processing from device control.
8. Stop only the owned WDA job, verify the local proxy has stopped, close the session, and inspect removal of that session's temporary images.
9. Only then proceed to the requested personal-app task.
