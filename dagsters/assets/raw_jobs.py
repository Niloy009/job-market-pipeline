"""Dagster asset — ingest raw job postings via Airbyte."""

from dagster import asset, AssetExecutionContext
from dagster_airbyte import AirbyteResource

from src.config import config
from src.logger import get_logger

logger = get_logger(__name__)


@asset(
    group_name="ingestion",
    description=(
        "Triggers an Airbyte sync that pulls job postings from the "
        "Bundesagentur fuer Arbeit API and lands them directly into "
        "the BigQuery raw layer. Replaces the custom Python ingestor."
    ),
)
def raw_job_postings(
    context: AssetExecutionContext,
    airbyte: AirbyteResource,
) -> None:
    """Trigger the Airbyte sync and record outcome metadata.

    Args:
        context: Dagster execution context for metadata and logging.
        airbyte: Injected :class:`AirbyteResource` instance.

    Raises:
        dagster.Failure: If the Airbyte sync fails or times out.
    """
    connection_id = config.airbyte_connection_id

    logger.info("Triggering Airbyte sync for connection_id=%s", connection_id)

    airbyte_output = airbyte.sync_and_poll(
        connection_id=connection_id,
        poll_interval=10,
        poll_timeout=600,
    )

    try:
        records_synced = (
            airbyte_output.job_details
            .attempts[-1]
            .attempt
            .total_stats
            .records_committed
        )
    except (AttributeError, IndexError):
        records_synced = "unknown"

    context.add_output_metadata(
        {
            "connection_id": connection_id,
            "airbyte_job_id": str(airbyte_output.job_details.get("job", {}).get("id", "unknown")),
            "records_synced": str(records_synced)
        }
    )

    logger.info(
        "Airbyte sync completed for connection_id=%s — records_synced=%s",
        connection_id,
        records_synced
    )
