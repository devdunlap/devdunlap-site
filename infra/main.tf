terraform {
  required_version = ">= 1.5.0"

  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
}

# The API token comes from the CLOUDFLARE_API_TOKEN environment variable.
# Credentials are never written into code or committed to the repo.
provider "cloudflare" {}

# The Pages project that serves the site. Content deploys stay with the
# CI pipeline (Wrangler); Terraform owns the project's existence and
# settings, which is the part that should be reviewed as code.
resource "cloudflare_pages_project" "site" {
  account_id        = var.account_id
  name              = var.pages_project_name
  production_branch = "main"
}

# Attaches the custom domain to the Pages project. Cloudflare issues the
# certificate automatically once the domain validates.
resource "cloudflare_pages_domain" "site" {
  account_id   = var.account_id
  project_name = cloudflare_pages_project.site.name
  domain       = var.domain
}

# Apex record pointing the domain at the Pages deployment. Pages creates
# this record itself when the custom domain attaches; it is declared here
# so the desired end state is visible — and reviewable — in code.
# Import the existing record before the first apply (see infra/README.md).
resource "cloudflare_record" "apex" {
  zone_id = var.zone_id
  name    = "@"
  type    = "CNAME"
  content = var.pages_subdomain
  proxied = true
  ttl     = 1 # 1 = automatic when proxied
}

# Baseline zone hardening for a public static site: HTTPS everywhere,
# modern TLS floor, no downgrade path.
resource "cloudflare_zone_settings_override" "site" {
  zone_id = var.zone_id

  settings {
    ssl                      = "strict"
    always_use_https         = "on"
    automatic_https_rewrites = "on"
    min_tls_version          = "1.2"
  }
}
