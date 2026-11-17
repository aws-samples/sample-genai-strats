variable "permissions_boundary_arn" {
  description = "Permissions boundary for the IAM roles this lab creates. Set by the workshop environment (TF_VAR_permissions_boundary_arn); leave unset in your own account."
  type        = string
  default     = null
}
