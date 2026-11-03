# Security scope

This software can read and operate the unlocked iPhone you authorise. It is intended for a single trusted operator on a trusted Mac. The assistant's task scope is not an enforced per-app iOS sandbox.

## Enforced boundaries

- Both phone-side listeners are bound to `127.0.0.1` by an exact, hash-verified patch to pinned WDA source.
- The Mac proxy binds only to `127.0.0.1`, requires a private random bearer capability, rejects Origin-bearing browser requests, and connects only to the selected USB device.
- Arbitrary remote WDA URLs, credentials in URLs, invalid ports, and unrecognised tracked WDA modifications are rejected.
- The proxy does not provide a general-purpose network destination, relay authentication headers to WDA, or publish permissive CORS response headers.
- Runtime directories, tokens, and captured images are restricted to the local account.
- No product analytics or remote support service is included.

Mac processes running as your account can read that account's files and may be able to use the token. A compromised Mac, malicious AI host, unsafe user-approved phone action, or compromised dependency is outside this boundary. Phone screenshots shared with an AI provider are subject to that provider's processing.

## Verification

See [TESTING.md](TESTING.md). A dependency advisory match is not proof of exploitability in this application. Conversely, a clean dependency scan or passing test suite is not proof that every backdoor or vulnerability is absent.

Before using sensitive apps, complete the physical-device acceptance checks and verify that stopping the owned runner closes its services. Use your own signing identity. Never give an assistant Apple passwords, verification codes, or your device passcode.

## Reporting

Report suspected issues privately to the Balta Tech repository administrators using the private repository's security reporting channel when available. If no reporting channel is configured, contact a known administrator directly; do not post credentials, screenshots, device identifiers, or exploit details in a public issue.
