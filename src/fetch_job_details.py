"""Fetch full job details from the Bundesagentur fuer Arbeit API.

This module reads reference numbers from the raw jobs CSV,
fetches full job details including descriptions for each posting,
and saves the enriched data as a new CSV file.

Typical usage:
    python -m src.fetch_job_details
"""

import base64
import time
from pathlib import Path

import pandas as pd
import requests

from src.config import config
from src.logger import get_logger


logger = get_logger(__name__)

# --- Constants ---
REQUEST_DELAY_SECONDS = 0.3
OUTPUT_PATH = Path("data/raw_jobs_with_details.csv")


def fetch_job_detail(refnr: str, headers: dict) -> dict:
    """Fetch full job details for a single job posting.

    Args:
        refnr: The unique job reference number.
        headers: HTTP headers including the API key.

    Returns:
        A dictionary containing the full job detail response,
        or an empty dict if the request fails.
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
    """Extract the job description text from a detail response.

    Args:
        detail: Full job detail dictionary from the API.

    Returns:
        The job description string, or empty string if not found.
    """
    return detail.get("stellenangebotsBeschreibung", "")


def fetch_all_job_details(
    input_path: Path = config.output_path,
    output_path: Path = OUTPUT_PATH,
) -> pd.DataFrame:
    """Fetch full details for all jobs in the raw jobs CSV.

    Reads reference numbers from the raw jobs CSV, fetches
    the full description for each job, and saves the result
    as a new CSV with the description column added.

    Args:
        input_path: Path to the raw jobs CSV file.
        output_path: Path to save the enriched CSV file.

    Returns:
        A DataFrame with job descriptions added.

    Raises:
        FileNotFoundError: If the input CSV does not exist.
        ValueError: If the input CSV is empty or missing refnr column.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_csv(input_path)

    if df.empty:
        raise ValueError("Input CSV is empty.")

    if "refnr" not in df.columns:
        raise ValueError("Input CSV missing required column: refnr.")

    logger.info("Fetching details for %d jobs from %s.", len(df), input_path)

    headers = {"X-API-Key": config.api_key}
    descriptions = []
    total = len(df)

    for idx, row in df.iterrows():
        refnr = row["refnr"]
        logger.info("Fetching detail %d of %d — refnr: %s.", idx + 1, total, refnr)

        detail = fetch_job_detail(refnr, headers)
        description = extract_description(detail)
        descriptions.append(description)

        time.sleep(REQUEST_DELAY_SECONDS)

    df["stellenbeschreibung"] = descriptions

    filled = df["stellenbeschreibung"].astype(bool).sum()
    logger.info("Descriptions fetched: %d of %d jobs had content.", filled, total)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info("Saved enriched data to %s.", output_path)

    return df


def main() -> None:
    """Main entry point for fetching full job details."""
    fetch_all_job_details()


if __name__ == "__main__":
    main()
