"""Enrich job postings with LLM-extracted skills and metadata.

This module reads raw job postings with descriptions from a local
CSV file, sends each job description to a local Ollama LLM,
extracts structured skill and role information, and writes the
enriched data back to a new BigQuery table.

Typical usage:
    python -m src.enrich_jobs
"""

import json
import time
from pathlib import Path

import pandas as pd
from google.cloud import bigquery
import ollama

from src.config import config
from src.logger import get_logger

logger = get_logger(__name__)

# --- Constants ---
OLLAMA_MODEL = "llama3.1:8b"
ENRICHED_TABLE_ID = "enriched_jobs"
BATCH_DELAY_SECONDS = 0.5
DETAILS_CSV_PATH = Path("data/raw_jobs_with_details.csv")
MAX_DESCRIPTION_LENGTH = 2000

EXTRACTION_PROMPT = """Du bist ein Jobanalyse-Experte. Extrahiere strukturierte Informationen aus der folgenden Stellenbeschreibung.

Antworte NUR mit einem gültigen JSON-Objekt. Keine Erklärung, kein Markdown, kein zusätzlicher Text.

JSON Format:
{{
  "skills": ["skill1", "skill2"],
  "seniority": "junior | mid | senior",
  "role_category": "Data Engineering | Data Science | ML Engineering | Other"
}}

Stellenbeschreibung:
{description}
"""


def extract_skills_from_description(description: str) -> dict:
    """Extract skills and metadata from a job description using Ollama.

    Sends the job description to a local LLaMA model and parses
    the structured JSON response.

    Args:
        description: Raw job description text in German or English.

    Returns:
        A dictionary containing extracted skills, seniority level,
        and role category. Returns default values on failure.
    """
    default = {
        "skills": [],
        "seniority": "unknown",
        "role_category": "Other",
    }

    if not description or pd.isna(description):
        return default

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": EXTRACTION_PROMPT.format(
                        description=str(description)[:MAX_DESCRIPTION_LENGTH]
                    ),
                }
            ],
        )

        raw_text = response["message"]["content"].strip()

        # Strip markdown code fences if present
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]

        extracted = json.loads(raw_text.strip())
        logger.debug("Successfully extracted: %s", extracted)
        return extracted

    except json.JSONDecodeError:
        logger.warning(
            "Failed to parse JSON from LLM response. Raw: %s",
            raw_text,
        )
        return default
    except Exception as e:
        logger.error("Ollama call failed: %s", e)
        return default


def fetch_raw_jobs() -> pd.DataFrame:
    """Fetch job postings with descriptions from local CSV.

    Returns:
        A DataFrame containing all rows with descriptions.

    Raises:
        FileNotFoundError: If the details CSV does not exist.
        ValueError: If the CSV is empty.
    """
    if not DETAILS_CSV_PATH.exists():
        raise FileNotFoundError(
            f"Details CSV not found at {DETAILS_CSV_PATH}. "
            "Run fetch_job_details first."
        )

    df = pd.read_csv(DETAILS_CSV_PATH)

    if df.empty:
        raise ValueError("Details CSV is empty. Nothing to enrich.")

    logger.info("Loaded %d jobs from %s.", len(df), DETAILS_CSV_PATH)
    return df


def enrich_jobs(df: pd.DataFrame) -> pd.DataFrame:
    """Enrich job postings DataFrame with LLM-extracted metadata.

    Iterates over each row, calls the LLM for skill extraction,
    and appends the results as new columns.

    Args:
        df: Raw job postings DataFrame with descriptions.

    Returns:
        Enriched DataFrame with extracted_skills, seniority, and
        role_category columns added.
    """
    skills_list = []
    seniority_list = []
    role_category_list = []

    total = len(df)

    for idx, row in df.iterrows():
        description = row.get("stellenbeschreibung", "")

        logger.info("Enriching job %d of %d.", idx + 1, total)

        extracted = extract_skills_from_description(description)

        skills_list.append(json.dumps(extracted.get("skills", [])))
        seniority_list.append(extracted.get("seniority", "unknown"))
        role_category_list.append(
            extracted.get("role_category", "Other")
        )

        time.sleep(BATCH_DELAY_SECONDS)

    df["extracted_skills"] = skills_list
    df["seniority"] = seniority_list
    df["role_category"] = role_category_list

    logger.info("Enrichment complete for %d jobs.", total)
    return df


def load_enriched_jobs_to_bigquery(df: pd.DataFrame) -> None:
    """Load enriched job postings into a new BigQuery table.

    Args:
        df: Enriched DataFrame to upload.

    Raises:
        ValueError: If the DataFrame is empty.
        google.api_core.exceptions.GoogleAPIError: If the load fails.
    """
    if df.empty:
        raise ValueError("Cannot load empty DataFrame to BigQuery.")

    client = bigquery.Client(project=config.project_id)

    full_table_id = (
        f"{config.project_id}.{config.dataset_id}.{ENRICHED_TABLE_ID}"
    )

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        autodetect=True,
    )

    logger.info(
        "Loading %d enriched rows into %s.", len(df), full_table_id
    )

    job = client.load_table_from_dataframe(
        df,
        full_table_id,
        job_config=job_config,
    )
    job.result()

    logger.info(
        "Successfully loaded enriched data into %s.", full_table_id
    )


def main() -> None:
    """Main entry point for enriching and loading job postings."""
    df = fetch_raw_jobs()
    enriched_df = enrich_jobs(df)
    load_enriched_jobs_to_bigquery(enriched_df)


if __name__ == "__main__":
    main()
