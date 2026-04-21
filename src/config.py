"""Centralised configuration for the job market pipeline.

Loads all environment variables once and exposes them as typed
attributes. All other modules should import from here instead
of calling os.getenv() directly.

Typical usage:
    from src.config import config
    print(config.project_id)
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from src.logger import get_logger

load_dotenv()

logger = get_logger(__name__)


@dataclass(frozen=True)
class PipelineConfig:
    """Immutable configuration for the job market pipeline.

    Attributes:
        gcp_credentials: Path to the GCP service account JSON key.
        project_id: GCP project ID.
        dataset_id: BigQuery dataset ID.
        table_id: BigQuery table ID.
        api_base_url: Base URL for the Bundesagentur API.
        api_key: API key for the Bundesagentur API.
        default_keyword: Default job search keyword.
        default_location: Default job search location.
        output_path: Path to save the raw jobs CSV.
    """

    gcp_credentials: str
    project_id: str
    dataset_id: str
    table_id: str
    api_base_url: str
    api_key: str
    default_keyword: str
    default_location: str
    output_path: Path


def _load_config() -> PipelineConfig:
    """Load and validate configuration from environment variables.

    Returns:
        A fully populated PipelineConfig instance.

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
        default_keyword=os.getenv("DEFAULT_KEYWORD", "data engineer"),
        default_location=os.getenv("DEFAULT_LOCATION", "Deutschland"),
        output_path=Path(os.getenv("OUTPUT_PATH", "data/raw_jobs.csv")),
    )


config = _load_config()
