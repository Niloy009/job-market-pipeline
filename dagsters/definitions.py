"""Dagster definitions — registers assets, jobs, schedules, and resources."""

from dagster import Definitions

from dagsters.assets.raw_jobs import raw_job_postings
from dagsters.assets.job_details import job_details
from dagsters.assets.enriched_jobs import enriched_job_postings
from dagsters.jobs.pipeline_job import job_market_pipeline_job
from dagsters.schedules.daily_schedule import daily_job_market_schedule
from dagsters.resources import airbyte_resource

defs = Definitions(
    assets=[
        raw_job_postings,
        job_details,
        enriched_job_postings,
    ],
    jobs=[
        job_market_pipeline_job,
    ],
    schedules=[
        daily_job_market_schedule,
    ],
    resources={
        "airbyte": airbyte_resource,
    },
)
