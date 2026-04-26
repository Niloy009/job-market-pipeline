"""Job definition for the full ingestion and enrichment pipeline."""

from dagster import AssetSelection, define_asset_job


job_market_pipeline_job = define_asset_job(  # pylint: disable=assignment-from-no-return
    name="job_market_pipeline_job",
    selection=(
        AssetSelection.groups("ingestion") |
        AssetSelection.groups("enrichment")
    ),
    description=(
        "Triggers Airbyte sync, fetches full job descriptions, "
        "and enriches with LLM-extracted skills into BigQuery."
    ),
)
