"""Dagster asset for fetching raw job postings.

This module defines the raw_job_postings asset which fetches
job postings from the Bundesagentur fuer Arbeit API and saves
them as a CSV file.
"""

import pandas as pd
from dagster import asset, AssetExecutionContext

from src.config import config
from src.fetch_jobs import fetch_jobs, save_to_csv
from src.logger import get_logger

logger = get_logger(__name__)


@asset(
    group_name="ingestion",
    description="Fetches raw job postings from Bundesagentur fuer Arbeit API.",
)
def raw_job_postings(context: AssetExecutionContext) -> pd.DataFrame:
    """Fetch raw job postings and save them to CSV.

    Args:
        context: Dagster asset execution context for logging
            and metadata.

    Returns:
        A DataFrame containing the fetched job postings.
    """
    df = fetch_jobs(
        keyword=config.default_keyword,
        location=config.default_location,
    )

    save_to_csv(df)

    context.add_output_metadata(
        {
            "num_rows": len(df),
            "keyword": config.default_keyword,
            "location": config.default_location,
            "output_path": str(config.output_path),
        }
    )

    logger.info("raw_job_postings asset completed with %d rows.", len(df))
    return df
