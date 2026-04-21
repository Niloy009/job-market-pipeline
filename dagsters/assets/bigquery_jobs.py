"""Dagster asset for loading job postings into BigQuery.

This module defines the bigquery_job_postings asset which reads
the raw CSV and loads it into the BigQuery postings table.
"""

from dagster import asset, AssetExecutionContext

from src.config import config
from src.load_bigquery import load_to_bigquery, read_and_clean_csv
from src.logger import get_logger

logger = get_logger(__name__)


@asset(
    group_name="ingestion",
    description="Loads cleaned job postings into BigQuery.",
    deps=["raw_job_postings"],
)
def bigquery_job_postings(context: AssetExecutionContext) -> None:
    """Load cleaned job postings CSV into BigQuery.

    Depends on raw_job_postings asset being materialised first.

    Args:
        context: Dagster asset execution context for logging
            and metadata.
    """
    df = read_and_clean_csv()
    load_to_bigquery(df)

    context.add_output_metadata(
        {
            "num_rows": len(df),
            "project_id": config.project_id,
            "dataset_id": config.dataset_id,
            "table_id": config.table_id,
        }
    )

    logger.info(
        "bigquery_job_postings asset completed. Loaded %d rows.", len(df)
    )
