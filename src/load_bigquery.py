"""Load job postings CSV data into Google BigQuery.

This module reads the raw job postings CSV file, performs basic
cleaning, and loads the data into a BigQuery table for downstream
processing and analysis.

Typical usage:
    python -m src.load_to_bigquery
"""

from pathlib import Path

import pandas as pd
from google.cloud import bigquery

from src.config import config
from src.logger import get_logger

logger = get_logger(__name__)


def read_and_clean_csv(input_path: Path = config.output_path) -> pd.DataFrame:
    """Read and clean the raw job postings CSV file.

    Reads the CSV, removes duplicate rows, and normalises column
    names to snake_case for BigQuery compatibility.

    Args:
        input_path: Path to the CSV file to read.

    Returns:
        A cleaned DataFrame ready for loading into BigQuery.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If the CSV file is empty.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_csv(input_path)

    if df.empty:
        raise ValueError("Input CSV is empty. Nothing to load.")

    logger.info("Read %d rows from %s.", len(df), input_path)

    df = df.drop_duplicates()
    df.columns = [
        col.lower().replace(" ", "_").replace("-", "_")
        for col in df.columns
    ]

    logger.info("After deduplication: %d rows remaining.", len(df))
    return df


def load_to_bigquery(df: pd.DataFrame) -> None:
    """Load a cleaned DataFrame into a BigQuery table.

    Uploads the DataFrame to the BigQuery table specified in the
    pipeline config. Overwrites the table on each run using
    WRITE_TRUNCATE disposition.

    Args:
        df: The cleaned DataFrame to upload.

    Raises:
        google.api_core.exceptions.GoogleAPIError: If the BigQuery
            load job fails.
    """
    client = bigquery.Client(project=config.project_id)

    full_table_id = (
        f"{config.project_id}.{config.dataset_id}.{config.table_id}"
    )

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        autodetect=True,
    )

    logger.info("Loading %d rows into %s.", len(df), full_table_id)

    job = client.load_table_from_dataframe(
        df,
        full_table_id,
        job_config=job_config,
    )
    job.result()

    logger.info(
        "Successfully loaded %d rows into %s.",
        len(df),
        full_table_id,
    )


def main() -> None:
    """Main entry point for loading job postings into BigQuery."""
    df = read_and_clean_csv()
    load_to_bigquery(df)


if __name__ == "__main__":
    main()
