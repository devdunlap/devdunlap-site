# THE SWITCH.
#
# This one value decides which version of the site production serves.
# Change the default to "green", push to main, and the deploy workflow
# promotes the green version to devdunlap.site automatically — no
# buttons in the Actions tab. Change it back to "blue" and push again
# to roll back.
#
# The deploy workflow (.github/workflows/deploy.yml) reads the default
# below on every push; Terraform declares it so the choice is reviewed
# as code, like everything else in this folder.
variable "active_slot" {
  description = "Which colour production serves: \"blue\" (Ops Console) or \"green\" (editorial redesign)."
  type        = string
  default     = "green"

  validation {
    condition     = contains(["blue", "green"], var.active_slot)
    error_message = "active_slot must be \"blue\" or \"green\"."
  }
}
