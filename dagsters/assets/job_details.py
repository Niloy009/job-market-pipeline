"""Dagster asset — fetch full job descriptions from the Bundesagentur API."""

import pandas as pd
from dagster import asset, AssetExecutionContext

from src.fetch_job_details import fetch_all_job_details
from src.logger import get_logger

logger = get_logger(__name__)


@asset(
    group_name="ingestion",
    description=(
        "Reads refnr values from BigQuery (Airbyte raw layer), fetches "
        "full job descriptions from the Bundesagentur API, and saves "
        "enriched data for downstream LLM processing."
    ),
    deps=["raw_job_postings"],
)
def job_details(context: AssetExecutionContext) -> pd.DataFrame:
    """Fetch full descriptions for all jobs in the BigQuery raw layer.

    Args:
        context: Dagster execution context for metadata and logging.

    Returns:
        DataFrame with a ``stellenbeschreibung`` column appended.
    """
    df = fetch_all_job_details()

    filled = df["stellenbeschreibung"].astype(bool).sum()

    context.add_output_metadata(
        {
            "num_rows": len(df),
            "rows_with_description": int(filled),
            "rows_without_description": int(len(df) - filled),
            "source": "BigQuery (Airbyte raw layer)",
        }
    )

    logger.info(
        "job_details asset completed. %d of %d rows have descriptions.",
        filled,
        len(df),
    )

    return df
