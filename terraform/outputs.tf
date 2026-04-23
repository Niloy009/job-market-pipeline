# Outputs for the job market pipeline infrastructure.

output "bigquery_dataset_id" {
  description = "The BigQuery dataset ID"
  value       = google_bigquery_dataset.raw_jobs.dataset_id
}

output "postings_table_id" {
  description = "The BigQuery postings table ID"
  value       = google_bigquery_table.job_postings.table_id
}

output "enriched_jobs_table_id" {
  description = "The BigQuery enriched jobs table ID"
  value       = google_bigquery_table.enriched_jobs.table_id
}