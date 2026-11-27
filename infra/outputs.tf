output "site_url" {
  description = "The public site on its custom domain."
  value       = "https://${var.domain}"
}

output "pages_dev_url" {
  description = "The project's permanent pages.dev address."
  value       = "https://${var.pages_subdomain}"
}

output "active_slot" {
  description = "The colour production currently serves, as declared in active_slot.tf."
  value       = var.active_slot
}

output "blue_slot_url" {
  description = "The blue version, always live on its own slot."
  value       = "https://devdunlap-site-blue.pages.dev"
}

output "green_slot_url" {
  description = "The green version, always live on its own slot."
  value       = "https://devdunlap-site-green.pages.dev"
}
