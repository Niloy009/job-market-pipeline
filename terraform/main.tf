terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = "job-market-pipeline-494012"
  region = "europe-west3"
}

resource "google_bigquery_dataset" "raw_jobs" {
  dataset_id = "raw_jobs"
  location = "EU"
  description = "Raw job postings from Bundesagentur fuer Arbeit"
}

resource "google_bigquery_table" "job_postings" {
  dataset_id = google_bigquery_dataset.raw_jobs.dataset_id
  table_id = "postings"
  deletion_protection = false
}