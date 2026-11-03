# Privacy and data flow

Balta Tech iPhone Use minimises data collection by removing collection paths. It has no product telemetry service, analytics opt-in, tracking installation ID, advertising integration, or automatic crash-report upload. There is no developer-operated remote relay or support backdoor.

## While controlling a phone

The MCP server runs locally on your Mac. A token-authenticated HTTP proxy on `127.0.0.1` forwards commands over USB. The pinned WebDriverAgent build on your iPhone is patched to bind its HTTP control port and MJPEG video port to `127.0.0.1`. The patch and its exact source hashes are checked before a managed build or startup.

App discovery queries the selected phone through Xcode's `devicectl` and optionally uses a bundled offline reference. It does not query an online app catalog. The local installed-app cache has a five-minute freshness window; the cache file may remain until you remove the runtime directory.

The live preview receives video in memory. Explicit model observations are returned to your AI host as screen images and accessibility text. That host and its AI provider can process and retain those observations according to your account settings and terms. This project cannot promise EU data residency, local AI inference, or deletion from a provider's chat history.

## Files on your Mac

The default runtime directory is `~/.local/share/balta-tech-iphone-use/`. It is separate from upstream installations and Git checkouts. Directories are restricted to your account; private state and observation images use mode `0600`.

It contains device and signing identifiers, local session state, a private proxy token, build results, the pinned WDA source, dependencies, and diagnostic logs. It contains no analytics identity. Logs redact recognised credential patterns, but should still be treated as private.

Observation images are temporary transport files. Each process removes its own images on orderly shutdown. A crash or forced termination can leave images behind. Remove residual files from the runtime `artifacts/` directory after all sessions stop. The screenshot toolbar intentionally writes an image to the Mac clipboard; the iOS screenshot tool intentionally creates a screenshot in iPhone Photos. These user-requested copies have their respective operating system's retention behaviour. The CLI also supports an explicit `--export-images` directory; those intentional exports remain until the operator removes them.

Local timing metrics are bounded in-memory diagnostics. They are never uploaded by this project.

## Network use during setup

Source and dependency downloads contact GitHub and the public npm registry. Xcode may contact Apple for device preparation, signing, and provisioning. These providers see the requests normally associated with their services. Ordinary phone operation does not need a developer cloud service.

WebDriverAgent and npm packages are external dependencies. Pinning, integrity checks, and tests reduce risk; they do not prove that every dependency is defect-free.

## User control

Keep control scoped to the task you requested. Handle Apple sign-in, phone unlock, passwords, verification codes, Face ID, and Touch ID directly in the relevant system UI. The assistant should pause observation while you authenticate.

Stop the owned runner and disconnect USB to finish a session. To remove the installation, remove the local Codex MCP/plugin registration, delete the runner from your phone, and delete the private runtime directory after stopping all jobs. Do not remove development identities belonging to unrelated projects.

These are engineering privacy choices, not a claim of legal certification or guaranteed GDPR compliance. Organisation-wide retention, access controls, and the AI provider's processing terms remain the operator's responsibility.

Runner startup failures can retain XCTest result bundles, device connection metadata and redacted diagnostic evidence in private runtime directories. These files may contain device or account context and are not uploaded automatically. Mac-wide filtered XCTest log capture is opt-in (`IPHONE_USE_XCTEST_HOST_LOG=1`) and limited to two 1 MiB log files per job. Local diagnostic directories remain until the user removes them.

Phone coordination uses private local files containing a temporary random owner token, process ID, expiry and optional short task label. These fields are used only for local ownership and stale-observation checks. They are not an installation tracking identifier and are not uploaded. Progress contains step counts only. Point mode shares the selected target's label, coordinates and observation context with the AI host only after the user chooses that mode and a target; authentication pauses block it.
