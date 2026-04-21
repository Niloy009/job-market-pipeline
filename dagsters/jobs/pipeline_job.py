"""Dagster job definition for the job market pipeline.

This module defines the job that combines all ingestion assets
into a single executable unit.
"""

from dagster import AssetSelection, define_asset_job

from dagsters.assets.raw_jobs import raw_job_postings
from dagsters.assets.bigquery_jobs import bigquery_job_postings

job_market_pipeline_job = define_asset_job(
    name="job_market_pipeline_job",
    selection=AssetSelection.assets(
        raw_job_postings,
        bigquery_job_postings,
    ),
    description="Fetches job postings and loads them into BigQuery.",
)