"""Fetch job postings from the Bundesagentur fur Arbeit API.

This module retrieves German job postings from the official
Bundesagentur fur Arbeit (Federal Employment Agency) API and
saves them as a CSV file for downstream processing.

Typical usage:
    python -m src.fetch_jobs
"""

from pathlib import Path

import pandas as pd
import requests

from src.config import config
from src.logger import get_logger

logger = get_logger(__name__)

DEFAULT_PAGES = 5
PAGE_SIZE = 50


def fetch_jobs(keyword: str = config.default_keyword, location: str = config.default_location,
            pages: int = DEFAULT_PAGES) -> pd.DataFrame:
    """Fetch job postings from the Bundesagentur fuer Arbeit API.

    Args:
        keyword: Job title or skill to search for.
        location: Geographic location to filter jobs by.
        pages: Maximum number of pages to fetch.

    Returns:
        A DataFrame containing all fetched job postings.

    Raises:
        requests.HTTPError: If the API returns a non-200 status code.
    """
    all_jobs = []
    headers = {"X-API-Key": config.api_key}

    for page in range(1, pages + 1):
        params = {
            "was": keyword,
            "wo": location,
            "page": page,
            "size": PAGE_SIZE,
        }

        response = requests.get(
            config.api_base_url,
            params=params,
            headers=headers,
            timeout=10,
        )

        if response.status_code != 200:
            logger.error(
                "API request failed on page %d with status %d.",
                page,
                response.status_code,
            )
            break

        jobs = response.json().get("stellenangebote", [])

        if not jobs:
            logger.info("No more jobs found after page %d.", page - 1)
            break

        all_jobs.extend(jobs)
        logger.info("Fetched page %d — %d jobs retrieved.", page, len(jobs))

    if not all_jobs:
        logger.warning("No jobs were fetched. Returning empty DataFrame.")
        return pd.DataFrame()

    df = pd.DataFrame(all_jobs)
    logger.info("Total jobs fetched: %d", len(df))
    return df


def save_to_csv(df: pd.DataFrame, output_path: Path = config.output_path) -> None:
    """Save a DataFrame to a CSV file.

    Args:
        df: The DataFrame to save.
        output_path: The file path where the CSV will be written.

    Raises:
        ValueError: If the DataFrame is empty.
    """
    if df.empty:
        raise ValueError("Cannot save an empty DataFrame to CSV.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info("Data saved to %s", output_path)


def main() -> None:
    """Main entry point for fetching and saving job postings."""
    df = fetch_jobs()
    save_to_csv(df)


if __name__ == "__main__":
    main()
