"""Apply only the exact reviewed loopback patch to pinned WDA source."""
import hashlib
from pathlib import Path

SOURCE_PATH = "WebDriverAgentLib/Routing/FBWebServer.m"
ORIGINAL_SHA256 = "c0f73019f2e69e562229c6845e92ea1c41b173bd5c0a9a9e57e6b564e55cbf56"
PATCHED_SHA256 = "b81b2a5e53983f5988089eb977acd247ebb6c6fd5bdaed8b519286ad392dbefe"
REPLACEMENTS = {'  NSString *bindingIP = FBConfiguration.sharedInstance.bindingIPAddress;': '  NSString *bindingIP = @"127.0.0.1"; // Balta Tech: USB loopback only.', '  self.screenshotsBroadcaster.delegate = self.mjpegServer;': '  self.screenshotsBroadcaster.interface = @"127.0.0.1"; // Balta Tech: no LAN stream.\n  self.screenshotsBroadcaster.delegate = self.mjpegServer;', '  [self.server setDefaultHeader:@"Access-Control-Allow-Origin" value:@"*"];': '  // Balta Tech: no cross-origin browser access.', '  [self.server setDefaultHeader:@"Access-Control-Allow-Headers" value:@"Content-Type, X-Requested-With"];': '  // The authenticated Mac proxy also rejects every Origin header.'}


def verify_hardened_source(source):
    path = Path(source) / SOURCE_PATH
    if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != PATCHED_SHA256:
        raise ValueError("WDA must contain the exact reviewed Balta Tech loopback patch. Run fetch for a hardened checkout.")


def harden_source(source):
    path = Path(source) / SOURCE_PATH
    if path.is_symlink():
        raise ValueError("Refusing a symlinked WDA source file.")
    original = path.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    if digest == PATCHED_SHA256:
        return
    if digest != ORIGINAL_SHA256:
        raise ValueError("Unrecognised WDA source; existing changes are preserved.")
    changed = original.decode()
    for before, after in REPLACEMENTS.items():
        if changed.count(before) != 1:
            raise ValueError("Pinned WDA hardening target changed.")
        changed = changed.replace(before, after)
    if hashlib.sha256(changed.encode()).hexdigest() != PATCHED_SHA256:
        raise ValueError("WDA patch integrity check failed.")
    path.write_bytes(changed.encode())
    verify_hardened_source(source)


if __name__ == "__main__":
    import sys
    harden_source(sys.argv[1])
