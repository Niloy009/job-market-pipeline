# BigQuery table for LLM enriched job postings.

resource "google_bigquery_table" "enriched_jobs" {
  dataset_id          = google_bigquery_dataset.raw_jobs.dataset_id
  table_id            = "enriched_jobs"
  deletion_protection = false
  description         = "Job postings enriched with LLM-extracted skills and metadata"

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
    { name = "stellenbeschreibung",             type = "STRING", mode = "NULLABLE" },
    { name = "extracted_skills",                type = "STRING", mode = "NULLABLE" },
    { name = "seniority",                       type = "STRING", mode = "NULLABLE" },
    { name = "role_category",                   type = "STRING", mode = "NULLABLE" },
  ])
}