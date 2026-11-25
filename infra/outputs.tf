output "site_url" {
  description = "The public site on its custom domain."
  value       = "https://${var.domain}"
}

output "pages_dev_url" {
  description = "The project's permanent pages.dev address."
  value       = "https://${var.pages_subdomain}"
}
