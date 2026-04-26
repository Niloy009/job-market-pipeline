"""Dagster resource definitions."""

from dagster_airbyte import AirbyteResource

from src.config import config

airbyte_resource = AirbyteResource(
    host=config.airbyte_host,
    port=config.airbyte_port,
    use_https=False,
    username=config.airbyte_username,
    password=config.airbyte_password
)
