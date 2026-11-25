# devdunlap.site

Andrew Dunlap's consulting site — kept in two versions so the site itself
demonstrates a blue-green deployment:

- **`blue/`** — the original dark "Ops Console" design (terminal-style,
  single file, Overview / Services / Field Logs / About).
- **`green/`** — the editorial redesign: hand-coded HTML/CSS, first-person
  copy, real photo, services as a priced list.

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

## Deploy — blue-green

Each colour has its own Cloudflare Pages project (its slot), and
production is a third:

| Slot | Folder | Pages project | URL |
| --- | --- | --- | --- |
| Blue | `blue/` | `devdunlap-site-blue` | https://devdunlap-site-blue.pages.dev |
| Green | `green/` | `devdunlap-site-green` | https://devdunlap-site-green.pages.dev |
| Production | — | `devdunlap-site` | https://devdunlap.site |

Deploys are manual on purpose, from the Actions tab, using the
**Blue-Green Deploy** workflow (`.github/workflows/blue-green.yml`):

- **deploy-slot** ships one colour's folder to its own slot project and
  smoke-tests the slot URL.
- **promote** copies that colour's folder into the production project —
  that copy is the traffic switch. Rollback is promoting the other
  colour back.

Nothing deploys on push; every move is a deliberate button press, which
is the point of the demo. Requires the repository secrets
`CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`.

## Infrastructure as code

`infra/` holds the Terraform for the Cloudflare Pages project, the
custom domain, the apex DNS record, and zone security settings. The
resources predate the code (created via the API at first deploy), so
the config documents the import-first adoption path — see
`infra/README.md`. CI validates the code; it does not plan or apply.
