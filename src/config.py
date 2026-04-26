"""Pipeline configuration loaded from environment variables."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from src.logger import get_logger

load_dotenv()

logger = get_logger(__name__)


@dataclass(frozen=True)
class PipelineConfig:
    """Immutable config for the job market pipeline.

    Attributes:
        gcp_credentials: Path to the GCP service account JSON key.
        project_id: GCP project ID.
        dataset_id: BigQuery dataset ID.
        table_id: BigQuery table ID for raw postings.
        api_base_url: Bundesagentur job search API base URL.
        api_key: Bundesagentur API key.
        detail_base_url: Bundesagentur job detail API base URL.
        airbyte_connection_id: UUID of the Airbyte connection to trigger.
        airbyte_host: Host where Airbyte OSS is running.
        airbyte_port: Port where Airbyte OSS is running.
        airbyte_username: Airbyte UI username.
        airbyte_password: Airbyte UI password.
        default_keyword: Default job search keyword.
        default_location: Default job search location.
        output_path: Local path for the job details CSV.
    """

    gcp_credentials: str
    project_id: str
    dataset_id: str
    table_id: str
    api_base_url: str
    api_key: str
    detail_base_url: str
    airbyte_connection_id: str
    airbyte_host: str
    airbyte_port: str
    airbyte_username: str
    airbyte_password: str
    default_keyword: str
    default_location: str
    output_path: Path


def _load_config() -> PipelineConfig:
    """Load and validate config from environment variables.

    Returns:
        Populated :class:`PipelineConfig` instance.

    Raises:
        EnvironmentError: If any required environment variable is missing.
    """
    required_vars = [
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GCP_PROJECT_ID",
        "BQ_DATASET_ID",
        "BQ_TABLE_ID",
        "API_BASE_URL",
        "API_KEY",
        "DETAIL_BASE_URL",
        "AIRBYTE_CONNECTION_ID",
    ]

    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {missing}"
        )

    return PipelineConfig(
        gcp_credentials=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        project_id=os.getenv("GCP_PROJECT_ID"),
        dataset_id=os.getenv("BQ_DATASET_ID"),
        table_id=os.getenv("BQ_TABLE_ID"),
        api_base_url=os.getenv("API_BASE_URL"),
        api_key=os.getenv("API_KEY"),
        detail_base_url=os.getenv("DETAIL_BASE_URL"),
        airbyte_connection_id=os.getenv("AIRBYTE_CONNECTION_ID"),
        airbyte_host=os.getenv("AIRBYTE_HOST", "localhost"),
        airbyte_port=os.getenv("AIRBYTE_PORT", "8000"),
        airbyte_username=os.getenv("AIRBYTE_USERNAME", "airbyte"),
        airbyte_password=os.getenv("AIRBYTE_PASSWORD"),
        default_keyword=os.getenv("DEFAULT_KEYWORD", "data engineer"),
        default_location=os.getenv("DEFAULT_LOCATION", "Deutschland"),
        output_path=Path(os.getenv("OUTPUT_PATH", "data/raw_jobs.csv")),
    )


config = _load_config()
