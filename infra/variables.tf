variable "account_id" {
  description = "Cloudflare account ID that owns the Pages project and the zone. Not a secret, but kept out of code so the same config works in any account."
  type        = string
}

variable "zone_id" {
  description = "Cloudflare zone ID for devdunlap.site."
  type        = string
}

variable "domain" {
  description = "Custom domain attached to the Pages project."
  type        = string
  default     = "devdunlap.site"
}

variable "pages_project_name" {
  description = "Name of the Cloudflare Pages project."
  type        = string
  default     = "devdunlap-site"
}

variable "pages_subdomain" {
  description = "The project's pages.dev hostname; the apex CNAME points here."
  type        = string
  default     = "devdunlap-site.pages.dev"
}
