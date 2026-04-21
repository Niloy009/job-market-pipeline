"""Dagster schedule for the job market pipeline.

This module defines a daily schedule that automatically triggers
the full ingestion pipeline every day at 8:00 AM UTC.
"""

from dagster import ScheduleDefinition

from dagsters.jobs.pipeline_job import job_market_pipeline_job

daily_job_market_schedule = ScheduleDefinition(
    name="daily_job_market_schedule",
    job=job_market_pipeline_job,
    cron_schedule="0 8 * * *",
    description="Runs the job market pipeline every day at 8AM UTC.",
)
