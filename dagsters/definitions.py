"""Dagster definitions entry point for the job market pipeline.

This module registers all assets, jobs, and schedules with
Dagster so they are discoverable by the Dagster daemon and UI.
"""

from dagster import Definitions

from dagsters.assets.raw_jobs import raw_job_postings
from dagsters.assets.bigquery_jobs import bigquery_job_postings
from dagsters.jobs.pipeline_job import job_market_pipeline_job
from dagsters.schedules.daily_schedule import daily_job_market_schedule

defs = Definitions(
    assets=[
        raw_job_postings,
        bigquery_job_postings,
    ],
    jobs=[
        job_market_pipeline_job,
    ],
    schedules=[
        daily_job_market_schedule,
    ],
)
