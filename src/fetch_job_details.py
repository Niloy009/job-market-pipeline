"""Fetch full job descriptions from the Bundesagentur API."""

import base64
import time
from pathlib import Path

import pandas as pd
import requests
from google.cloud import bigquery

from src.config import config
from src.logger import get_logger


logger = get_logger(__name__)

REQUEST_DELAY_SECONDS = 0.3
OUTPUT_PATH = Path("data/raw_jobs_with_details.csv")
AIRBYTE_TABLE = "job_postings"


def fetch_refnrs_from_bigquery() -> pd.DataFrame:
    """Read job postings from the BigQuery table Airbyte synced into.

    Returns:
        DataFrame containing all columns from the raw postings table.

    Raises:
        ValueError: If the table is empty or missing the ``refnr`` column.
    """
    client = bigquery.Client(project=config.project_id)

    full_table = (
        f"{config.project_id}.{config.dataset_id}.{AIRBYTE_TABLE}"
    )

    query = f"SELECT * FROM `{full_table}`"

    logger.info("Reading job postings from BigQuery: %s", full_table)

    df = client.query(query).to_dataframe()

    if df.empty:
        raise ValueError(
            f"BigQuery table {full_table} is empty. "
            "Run the Airbyte sync first."
        )

    if "refnr" not in df.columns:
        raise ValueError(
            f"BigQuery table {full_table} is missing the refnr column."
        )

    logger.info("Loaded %d rows from BigQuery.", len(df))
    return df


def fetch_job_detail(refnr: str, headers: dict) -> dict:
    """Fetch full details for a single job posting from the Bundesagentur API.

    Args:
        refnr: Unique job reference number.
        headers: HTTP headers including the API key.

    Returns:
        Parsed JSON response dict, or an empty dict on failure.
    """
    try:
        encoded_refnr = base64.b64encode(refnr.encode()).decode()

        response = requests.get(
            f"{config.detail_base_url}/{encoded_refnr}",
            headers=headers,
            timeout=10,
        )

        if response.status_code != 200:
            logger.warning(
                "Failed to fetch details for refnr %s — status %d.",
                refnr,
                response.status_code,
            )
            return {}

        return response.json()

    except requests.RequestException as e:
        logger.error("Request failed for refnr %s: %s", refnr, e)
        return {}


def extract_description(detail: dict) -> str:
    """Extract the description text from a job detail response.

    Args:
        detail: Parsed job detail dict from the API.

    Returns:
        Description string, or empty string if not present.
    """
    return detail.get("stellenangebotsBeschreibung", "")


def fetch_all_job_details(output_path: Path = OUTPUT_PATH) -> pd.DataFrame:
    """Fetch full descriptions for all jobs in BigQuery and save to CSV.

    Args:
        output_path: Destination path for the enriched CSV file.

    Returns:
        DataFrame with a ``stellenbeschreibung`` column appended.

    Raises:
        ValueError: If the BigQuery table is empty or missing ``refnr``.
    """
    df = fetch_refnrs_from_bigquery()

    logger.info("Fetching descriptions for %d jobs.", len(df))

    headers = {"X-API-Key": config.api_key}
    descriptions = []
    total = len(df)

    for idx, row in df.iterrows():
        refnr = row["refnr"]
        logger.info(
            "Fetching detail %d of %d — refnr: %s.", idx + 1, total, refnr
        )

        detail = fetch_job_detail(refnr, headers)
        description = extract_description(detail)
        descriptions.append(description)

        time.sleep(REQUEST_DELAY_SECONDS)

    df["stellenbeschreibung"] = descriptions

    filled = df["stellenbeschreibung"].astype(bool).sum()
    logger.info(
        "Descriptions fetched: %d of %d jobs had content.", filled, total
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info("Saved enriched data to %s.", output_path)

    return df


def main() -> None:
    fetch_all_job_details()


if __name__ == "__main__":
    main()
