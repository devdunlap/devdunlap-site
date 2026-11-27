# Infrastructure as code — devdunlap.site on Cloudflare

Terraform for the Cloudflare side of the site: the Pages project, the
custom-domain attachment, the apex DNS record, and baseline zone
security settings.

## Honest status

These resources already exist — they were created through the
Cloudflare API on Nov 24, 2026, during the original deploy. This
configuration describes them as code after the fact, which is the
normal way IaC gets adopted on a live system: **declare, import, then
manage**. Nothing here has been applied yet.

## What CI does with it

The CI workflow runs only the credential-free checks on every push
and pull request:

```bash
terraform fmt -check -diff -recursive
terraform init -backend=false
terraform validate
```

`plan` and `apply` are deliberately **not** in CI: they need a real
API token and a state backend, and a static personal site does not
earn that machinery yet. If this were a team environment, the next
step would be remote state (an R2 or S3 backend) plus a plan-on-PR /
apply-on-merge workflow with the token stored as a CI secret.

## Adopting it for real (one-time)

```bash
cd infra
export CLOUDFLARE_API_TOKEN="..."   # scoped token, never committed
terraform init

terraform import cloudflare_pages_project.site        "<account_id>/devdunlap-site"
terraform import cloudflare_pages_project.blue        "<account_id>/devdunlap-site-blue"
terraform import cloudflare_pages_project.green       "<account_id>/devdunlap-site-green"
terraform import cloudflare_pages_domain.site         "<account_id>/devdunlap-site/devdunlap.site"
terraform import cloudflare_record.apex               "<zone_id>/<record_id>"
terraform import cloudflare_zone_settings_override.site "<zone_id>"

terraform plan   # expect: no changes, or only cosmetic drift
```

Account and zone IDs are passed as variables (`terraform.tfvars`,
git-ignored) — they are identifiers, not credentials, but they still
do not belong in a public repo's code.

## The blue/green switch

`active_slot.tf` declares one variable, `active_slot` (`"blue"` or
`"green"`, default `"blue"`): the colour production serves. It is a
plain variable default in a `.tf` file — not a tfvars value — so the
setting is committed, reviewed, and covered by `fmt`/`validate`.

The deploy workflow (`.github/workflows/deploy.yml`) reads that
default on every push to `main`: when the switch changes, or when the
active colour's folder changes, the workflow copies that colour into
the production Pages project. Terraform itself still does not apply
from CI (no remote state yet — see above); the variable is the
declared intent, and the workflow is the actuator.
