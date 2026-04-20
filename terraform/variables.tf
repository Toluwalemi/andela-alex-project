variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-west1"
}

variable "github_repo" {
  description = "GitHub repository owner/name permitted to deploy with WIF"
  type        = string
}

variable "backend_service_name" {
  description = "Cloud Run backend service name"
  type        = string
  default     = "alex-api"
}

variable "frontend_service_name" {
  description = "Cloud Run frontend service name"
  type        = string
  default     = "alex-web"
}

variable "artifact_repository_id" {
  description = "Artifact Registry Docker repository"
  type        = string
  default     = "alex-repo"
}

variable "openrouter_api_key" {
  description = "OpenRouter API key"
  type        = string
  sensitive   = true
}

variable "clerk_issuer" {
  description = "Clerk JWT issuer"
  type        = string
}

variable "clerk_jwks_url" {
  description = "Clerk JWKS URL"
  type        = string
}

variable "uploads_bucket_name" {
  description = "Optional explicit uploads bucket name"
  type        = string
  default     = ""
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "alex"
}

variable "db_user" {
  description = "PostgreSQL database user"
  type        = string
  default     = "alex"
}

