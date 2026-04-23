# BigQuery dataset for the job market pipeline.

resource "google_bigquery_dataset" "raw_jobs" {
  dataset_id  = var.dataset_id
  location    = var.dataset_location
  description = "Raw and enriched job postings from Bundesagentur fuer Arbeit"
  default_table_expiration_ms = 5184000000
  default_partition_expiration_ms = 5184000000
}