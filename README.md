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

## Deploy — blue-green, automatic on push

Each colour has its own Cloudflare Pages project (its slot), and
production is a third:

| Slot | Folder | Pages project | URL |
| --- | --- | --- | --- |
| Blue | `blue/` | `devdunlap-site-blue` | https://devdunlap-site-blue.pages.dev |
| Green | `green/` | `devdunlap-site-green` | https://devdunlap-site-green.pages.dev |
| Production | — | `devdunlap-site` | https://devdunlap.site |

Pushing to `main` is the launch — `.github/workflows/deploy.yml` runs
the checks, then:

- A colour whose folder changed ships to its own slot project and is
  smoke-tested on its slot URL.
- Production serves whichever colour **the switch** names: the
  `active_slot` variable in `infra/active_slot.tf` (Terraform). If the
  switch changed, or the active colour's folder changed, that colour
  is copied into the production project — that copy is the traffic
  switch — and https://devdunlap.site is smoke-tested.

So the everyday moves are just edits plus a push:

- **Tweak a design** — edit its folder, push. Its slot updates;
  production is untouched.
- **Take green live** — set `active_slot` to `"green"` in
  `infra/active_slot.tf`, push.
- **Roll back** — set it back to `"blue"`, push.

The **Blue-Green Deploy** workflow (`.github/workflows/blue-green.yml`)
remains as a manual override from the Actions tab — deploy one slot,
or promote a colour without a code change. Requires the repository
secrets `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`.

## Infrastructure as code

`infra/` holds the Terraform for the Cloudflare Pages projects (the
production project plus the blue and green slot projects), the
custom domain, the apex DNS record, and zone security settings. It
also holds the deployment switch: `active_slot` in
`infra/active_slot.tf` names the colour production serves, and the
deploy workflow reads it on every push. The resources predate the
code (created via the API at first deploy), so the config documents
the import-first adoption path — see `infra/README.md`. CI validates
the code; it does not plan or apply.
