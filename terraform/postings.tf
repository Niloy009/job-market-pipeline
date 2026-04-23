# BigQuery table for raw job postings.

resource "google_bigquery_table" "job_postings" {
  dataset_id          = google_bigquery_dataset.raw_jobs.dataset_id
  table_id            = "postings"
  deletion_protection = false
  description         = "Raw job postings fetched from Bundesagentur fuer Arbeit API"

  schema = jsonencode([
    { name = "beruf",                           type = "STRING", mode = "NULLABLE" },
    { name = "titel",                           type = "STRING", mode = "NULLABLE" },
    { name = "refnr",                           type = "STRING", mode = "NULLABLE" },
    { name = "arbeitsort",                      type = "STRING", mode = "NULLABLE" },
    { name = "arbeitgeber",                     type = "STRING", mode = "NULLABLE" },
    { name = "aktuelleVeroeffentlichungsdatum", type = "STRING", mode = "NULLABLE" },
    { name = "modifikationsTimestamp",          type = "STRING", mode = "NULLABLE" },
    { name = "eintrittsdatum",                  type = "STRING", mode = "NULLABLE" },
    { name = "kundennummerHash",                type = "STRING", mode = "NULLABLE" },
    { name = "externeUrl",                      type = "STRING", mode = "NULLABLE" },
  ])
}