"""Dagster asset for LLM enrichment of job postings.

This module defines the enriched_job_postings asset which reads
job details from the local CSV, enriches them using a local
Ollama LLM, and loads the results into BigQuery.
"""

from dagster import asset, AssetExecutionContext

from src.enrich_jobs import (
    fetch_raw_jobs,
    enrich_jobs,
    load_enriched_jobs_to_bigquery,
)
from src.logger import get_logger

logger = get_logger(__name__)


@asset(
    group_name="enrichment",
    description="Enriches job postings with LLM-extracted skills and metadata.",
    deps=["job_details"],
)
def enriched_job_postings(context: AssetExecutionContext) -> None:
    """Enrich job postings with LLM-extracted skills and load to BigQuery.

    Depends on job_details asset being materialised first.

    Args:
        context: Dagster asset execution context for logging
            and metadata.
    """
    df = fetch_raw_jobs()
    enriched_df = enrich_jobs(df)
    load_enriched_jobs_to_bigquery(enriched_df)

    seniority_counts = enriched_df["seniority"].value_counts().to_dict()
    role_counts = enriched_df["role_category"].value_counts().to_dict()

    context.add_output_metadata(
        {
            "num_rows": len(enriched_df),
            "seniority_breakdown": str(seniority_counts),
            "role_category_breakdown": str(role_counts),
        }
    )

    logger.info(
        "enriched_job_postings asset completed. %d rows enriched.",
        len(enriched_df),
    )
