"""Dagster asset for fetching full job details.

This module defines the job_details asset which reads reference
numbers from the raw jobs CSV, fetches full job descriptions
from the Bundesagentur fuer Arbeit API, and saves the enriched
CSV locally.
"""

import pandas as pd
from dagster import asset, AssetExecutionContext

from src.fetch_job_details import fetch_all_job_details
from src.logger import get_logger

logger = get_logger(__name__)


@asset(
    group_name="ingestion",
    description="Fetches full job descriptions using refnr from raw jobs.",
    deps=["raw_job_postings"],
)
def job_details(context: AssetExecutionContext) -> pd.DataFrame:
    """Fetch full job details including descriptions for all postings.

    Depends on raw_job_postings asset being materialised first.

    Args:
        context: Dagster asset execution context for logging
            and metadata.

    Returns:
        A DataFrame containing job postings with full descriptions.
    """
    df = fetch_all_job_details()

    filled = df["stellenbeschreibung"].astype(bool).sum()

    context.add_output_metadata(
        {
            "num_rows": len(df),
            "rows_with_description": int(filled),
            "rows_without_description": int(len(df) - filled),
        }
    )

    logger.info(
        "job_details asset completed. %d of %d rows have descriptions.",
        filled,
        len(df),
    )

    return df
