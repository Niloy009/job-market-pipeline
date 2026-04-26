variable "gcp_credentials_path" {
  description = "Path to the GCP service account JSON key file"
  type        = string
}

variable "project_id" {
  description = "GCP project ID"
  type        = string
  default     = "job-market-pipeline-494012"
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-west3"
}

variable "dataset_id" {
  description = "BigQuery dataset ID"
  type        = string
  default     = "raw_jobs"
}

variable "dataset_location" {
  description = "BigQuery dataset location"
  type        = string
  default     = "EU"
}