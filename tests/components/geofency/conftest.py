"""Common fixtures for the Geofency tests."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.components.geofency.const import DOMAIN
from homeassistant.const import CONF_WEBHOOK_ID

from tests.common import MockConfigEntry


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Override async_setup_entry."""
    with patch(
        "homeassistant.components.geofency.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture(name="config_entry")
def mock_config_entry() -> MockConfigEntry:
    """Mock Geofency configuration entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Geofency Webhook",
        data={
            "cloudhook": False,
            CONF_WEBHOOK_ID: "webhook_id",
        },
        entry_id="01JRD840SAZ55DGXBD78PTQ4EF",
    )
