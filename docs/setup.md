# Set up iPhone Use

Install the plugin on your Mac, connect your iPhone over USB, and verify the connection in Calculator. Check the [requirements](requirements.md) first.

## Install the plugin

```sh
mkdir -p ~/dev/projects
cd ~/dev/projects
git clone https://github.com/bal-r/eu-iphone-use.git
cd eu-iphone-use
sh scripts/install.sh
```

A private repository requires access through your GitHub account. If you already have the checkout, run the installer from that directory.

The installer adds the plugin and registers its local MCP server. Reconnect Codex or open a new chat, then enable **EU iPhone Use** if prompted.

## Connect your phone

1. Open **Xcode → Settings → Accounts** and sign in to your own Apple account in Apple's UI.
2. Connect and unlock your iPhone. Accept **Trust This Computer**, then let **Xcode → Window → Devices and Simulators** prepare it.
3. Enable **Settings → Privacy & Security → Developer Mode** when requested, including its restart and confirmation. Enable **Settings → Developer → Enable UI Automation** if requested. Trust only your own development identity if iOS asks.
4. Ask Codex:

   ```text
   Use iphone-use-setup to configure my USB-connected iPhone.
   Use this checkout, my own Apple team, and a unique bundle ID.
   Fetch the pinned WDA, verify its loopback patch, then build and start it.
   Wait for pua_ready to return ready=true.
   Open Calculator and verify 12 × 34 = 408.
   I will handle sign-in, trust prompts, unlock, and authentication directly.
   ```

Confirm that Calculator shows **408** before moving on to your task.

## Use and stop

Name the app and the result you want. Pause observation when you need to handle authentication yourself, then explicitly resume.

- `pua_device(action="release")` releases conversation ownership while keeping the runner warm.
- `pua_setup(action="stop")` stops the owned runner job.

To finish a phone session, stop the runner, close the preview, and disconnect USB. Closing the chat can leave the runner active.

## MCP connection

The recommended installer includes the tools and operating skills. It registers `balta_iphone_use` through a stable launcher, so plugin updates do not depend on an old version directory.

```sh
codex mcp list
codex mcp get balta_iphone_use --json
```

The MCP server uses local stdio. The internal `127.0.0.1:18100` endpoint is a device HTTP proxy, not a Streamable HTTP MCP endpoint. [MCP configuration documentation](https://learn.chatgpt.com/docs/extend/mcp).

On hosts verified to support plugin-bundled MCP servers, `sh scripts/install.sh --native` uses that mode and removes only a recognised compatibility registration. The default installer supports older CLI builds.

## Troubleshooting

| Problem | Check |
| --- | --- |
| Tools are missing | Reconnect MCP or open a new chat; check the plugin and `balta_iphone_use` registration. |
| Phone is missing | Check the USB data cable, unlock, trust prompt, and Xcode device preparation. |
| Signing fails | Check your Apple team, unique bundle ID, and provisioning in Xcode. |
| Automation mode times out | Unlock the phone, check UI Automation, and read setup status and local startup diagnostics. |
| Running and installed versions differ | Reconnect the MCP process to load the installed version. |
| Another chat holds the phone | Release ownership in that chat or wait for its idle lease to expire. |

`pua_setup(action="status")` reports the service and running version. Failed starts retain a private XCTest result and redacted diagnostics under the runtime's `diagnostics/` directory. Nothing is uploaded. Optional broader Mac log capture is off by default; `IPHONE_USE_XCTEST_HOST_LOG=1` enables it deliberately.

See [controls](usage.md), [privacy](privacy.md), and [security](../.github/SECURITY.md) for details.
