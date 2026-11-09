# Development

## Checks

```sh
npm ci --prefix ui --ignore-scripts --no-audit --no-fund
npm run build --prefix ui
npm test --prefix ui
node --test tooling/tests/*.test.mjs
sh scripts/check.sh
```

The preview build is committed as a self-contained HTML resource and must match its source. Runtime USB dependencies use the committed lockfile and `npm ci --ignore-scripts`.

The phone runner is pinned. Its approved loopback patch is verified before managed builds and startup. Review dependency and runner changes deliberately.

## Validation record

See [testing](../TESTING.md) for automated results, physical-device acceptance, and remaining checks. See [performance](../PERFORMANCE.md) for the recorded baseline and benchmark procedure.

## Packages

`python3 scripts/package.py` creates the install tree and source archive under `dist/`. Files are selected explicitly. Local article drafts under `promo/`, evaluation cases, experiment plugins, credentials, and installed dependencies are excluded.
