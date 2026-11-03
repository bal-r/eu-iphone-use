# Balta Tech iPhone Use

Control your own iPhone from Codex over USB, with a live preview and explicit setup through Xcode.

This is Balta Tech's private derivative of [zhongerxin/iPhone-use](https://github.com/zhongerxin/iPhone-use). It removes the upstream product telemetry and online app lookup, restricts both phone services to loopback, and authenticates the Mac's USB proxy. The original authors and MIT licence are retained. [See every material change](UPSTREAM.md).

## Privacy by design

The defaults favour data minimisation, user control, and clear processing boundaries for European privacy expectations. They do not imply EU-only AI hosting or legal certification.

- **No product analytics, usage tracking, installation tracking identifier, advertising SDK, or crash-report upload.** The telemetry implementation and its configuration have been removed, rather than disabled by an environment setting.
- **No developer-operated remote relay or remote administration service.** Device commands travel through your Mac and the USB connection. The phone's HTTP control and video ports bind to `127.0.0.1`.
- **A private local capability.** The Mac proxy also binds to `127.0.0.1`, requires a randomly generated token, rejects browser Origin headers, and does not expose permissive CORS.
- **Local app discovery.** App names are resolved using the connected phone and a small bundled reference. There is no App Store search request.
- **Less retained data.** Preview video stays in memory. Observation images use private files and are deleted on orderly session shutdown. An interrupted process can leave files that need local cleanup.

Your AI provider still processes the screen images and text you ask it to inspect. USB transport does not imply EU-only AI processing or an entirely offline assistant. GitHub, npm, and Apple are contacted during source download, dependency installation, and signing. Read [PRIVACY.md](PRIVACY.md) for the complete data flow.

This is powerful device automation. It can interact with apps beyond the task you named; it is not an iOS app-permission sandbox. We do not claim that software is free of all vulnerabilities or that a source review proves the absence of every possible backdoor. Our specific, testable promise is that this fork contains no product telemetry or developer remote-access mechanism. [Security scope](SECURITY.md).

## Requirements

- A Mac with full Xcode, initial components installed, and support for your phone's iOS version.
- Codex desktop and Codex CLI with local plugin/MCP support.
- Python 3.9 or later; supported Node.js 20.19+, 22.12+, or 24+; npm 10+.
- Your own iPhone, a USB data cable, and your own Apple account for signing.

No jailbreak or separately running Appium server is needed. This uses Apple's developer testing tools rather than Apple's iPhone Mirroring feature. Availability of iPhone Mirroring is therefore not a prerequisite.

## Install

1. Clone this private repository using your authorised GitHub account:

   ```sh
   gh repo clone Balta-Tech/iphone-use
   cd iphone-use
   ```

2. Read [UPSTREAM.md](UPSTREAM.md), [PRIVACY.md](PRIVACY.md), and [SECURITY.md](SECURITY.md). The installation script stages the plugin and registers the local MCP server; it does not require your Apple password.

3. Register the plugin:

   ```sh
   sh scripts/install.sh
   ```

4. Reconnect Codex or open a new chat and enable **Balta Tech iPhone Use** if prompted. New MCP tools may not load into an already running chat.

5. Open Xcode once. In **Xcode → Settings → Accounts**, sign in to your own Apple account. Complete two-factor authentication in Apple's UI. Never paste credentials or verification codes into chat.

6. Connect your iPhone with USB, unlock it, and accept **Trust This Computer** on the phone. In Xcode, open **Window → Devices and Simulators** and wait for preparation to finish.

7. Enable **Settings → Privacy & Security → Developer Mode** on your iPhone when requested. Restart and confirm on the phone. Enable **Settings → Developer → Enable UI Automation** if Xcode or the runner requests it. Trust only your own development identity under **General → VPN & Device Management** if iOS asks.

8. Ask Codex:

   ```text
   Use iphone-use-setup to configure my USB-connected iPhone.
   Use this Balta Tech checkout and my own Apple team and a unique bundle ID.
   Fetch the pinned WDA, apply and verify the supplied loopback hardening,
   then build and start it. Do not reuse an unverified external WDA service.
   Wait for pua_ready to report ready=true and show the phone preview.
   Test 12 × 34 = 408 in Calculator, then stop and report the result.
   I will handle Apple login, trust prompts, device unlock and verification.
   ```

9. Review the Calculator result before using personal apps. State the target app and task explicitly. For example: “Open Hinge and help edit my own profile. Ask me for missing personal facts and leave any account verification to me.”

10. When finished, ask Codex to stop its owned WDA job with `pua_setup(action="stop")`, close the preview, and disconnect USB. Closing the chat alone is not the same as stopping the phone runner.

Apple's free Personal Team can support personal-device testing, but provisioning expires after seven days and the runner must then be rebuilt and reinstalled. Apple also limits the number of development apps and devices. [Apple account guidance](https://developer.apple.com/help/account/basics/about-your-developer-account).

## Development and validation

```sh
npm ci --prefix ui --ignore-scripts --no-audit --no-fund
npm run build --prefix ui
npm test --prefix ui
node --test tooling/tests/*.test.mjs
sh scripts/check.sh
```

The UI build is committed as a self-contained HTML resource and must match the source. Runtime USB dependencies use `npm ci --ignore-scripts` and the committed lockfile. Code changes and dependency updates require a new review; do not silently track upstream `main` on a phone installation.

See [TESTING.md](TESTING.md) for validation evidence and the remaining physical-device checks. Successful unit tests or an unsigned Xcode build do not establish that a particular phone has passed acceptance testing.

## Preview quality

The preview's Auto / Eco / Fast button controls both viewer pacing and the phone's JPEG capture rate. Auto uses 2 FPS while idle and requests 8 FPS around activity; Eco stays at 2 FPS and Fast requests 8 FPS. These are requested limits, not guaranteed delivered frame rates. Changes wait until the phone command channel is available and do not replay gestures. Frame age is shown beside the connection state. Hidden panels stop renewing capture as before.

## Startup diagnostics

Failed runner starts now retain a private XCTest result bundle and a bounded, redacted failure report under the runtime's `diagnostics/` directory. Status distinguishes the runner's exit code from xcodebuild's and preserves early failure evidence. No report is uploaded. Optional broader Mac log capture is off by default; enable it deliberately with `IPHONE_USE_XCTEST_HOST_LOG=1`. Diagnostic files remain locally until removed.

## Usability candidate

The 0.5.0 integration branch combines faster known-step workflows, USB connection reuse, adaptive preview and selected upstream reliability fixes. [USABILITY.md](USABILITY.md) lists the independent branches, APIs and remaining phone acceptance checks.
