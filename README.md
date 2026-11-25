# devdunlap.site — The Ops Console

Andrew Dunlap's consulting site, designed as a live operations console.
Static single-page site (plain HTML/CSS/JS, no build step): Overview, Services
(DevOps / ClickOps / AI-assisted delivery with Claude), Field Logs, About.
Target: small and mid-sized businesses that want enterprise-level talent.

Live at https://devdunlap.site (Cloudflare Pages).
Built and documented start to finish — see the build log in the FDE goal files.

## CI pipeline

`.github/workflows/ci.yml` runs on every push and pull request to `main`:

1. **Static site checks** — `scripts/check_site.py`, zero dependencies:
   page-weight budget (100 KB), balanced HTML, unique element ids, local
   file references and in-page anchors resolve, meta description/viewport,
   image alt text, `rel="noopener"` on new-tab links, no insecure `http://`
   URLs, no inline `onclick`, no placeholder text.
2. **Terraform checks** — `terraform fmt -check`, `init -backend=false`,
   and `validate` over `infra/`, the Cloudflare setup as code.

Run the site checks locally with the same command CI uses:

```bash
python3 scripts/check_site.py
```

## Deploy

Deploys are manual on purpose: in the Actions tab, run the CI workflow
and tick **deploy**. After the checks pass it ships `index.html` to
Cloudflare Pages with Wrangler and smoke-tests the live pages.dev URL.
Requires the repository secrets `CLOUDFLARE_API_TOKEN` and
`CLOUDFLARE_ACCOUNT_ID`. Day-to-day, the site is redeployed with a
one-command helper; this job exists so the full path — check, ship,
verify — is visible in one place.

## Infrastructure as code

`infra/` holds the Terraform for the Cloudflare Pages project, the
custom domain, the apex DNS record, and zone security settings. The
resources predate the code (created via the API at first deploy), so
the config documents the import-first adoption path — see
`infra/README.md`. CI validates the code; it does not plan or apply.
