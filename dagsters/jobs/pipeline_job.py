"""Dagster job definition for the job market pipeline.

This module defines the job that combines all ingestion assets
into a single executable unit.
"""

from dagster import AssetSelection, define_asset_job


job_market_pipeline_job = define_asset_job(  # pylint: disable=assignment-from-no-return
    name="job_market_pipeline_job",
    selection=(
        AssetSelection.groups("ingestion") |
        AssetSelection.groups("enrichment")),
    description="Fetches job postings and loads them into BigQuery."
)
