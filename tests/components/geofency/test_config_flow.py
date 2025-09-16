"""Test the Geofency config flow."""

from unittest.mock import AsyncMock, patch

from homeassistant.components.geofency.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_WEBHOOK_ID
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from tests.common import MockConfigEntry


async def test_form(hass: HomeAssistant, mock_setup_entry: AsyncMock) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM

    with (
        patch(
            "homeassistant.components.webhook.async_generate_id",
            return_value="webhook_id",
        ),
        patch(
            "homeassistant.components.webhook.async_generate_url",
            return_value="http://example.com:8123",
        ),
    ):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Geofency Webhook"
    assert result["data"] == {
        "cloudhook": False,
        CONF_WEBHOOK_ID: "webhook_id",
    }
    assert result["description_placeholders"] == {
        "docs_url": "https://www.home-assistant.io/integrations/geofency/",
        "webhook_url": "http://example.com:8123",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_import_flow(hass: HomeAssistant, mock_setup_entry: AsyncMock) -> None:
    """Test the import flow."""
    with (
        patch(
            "homeassistant.components.webhook.async_generate_id",
            return_value="webhook_id",
        ),
        patch(
            "homeassistant.components.webhook.async_generate_url",
            return_value="http://example.com:8123",
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "import"},
            data={},
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Geofency Webhook"
    assert result["data"] == {
        "cloudhook": False,
        CONF_WEBHOOK_ID: "webhook_id",
    }
    assert result["description_placeholders"] == {
        "docs_url": "https://www.home-assistant.io/integrations/geofency/",
        "webhook_url": "http://example.com:8123",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_single_instance_allowed(
    hass: HomeAssistant, mock_setup_entry: AsyncMock
) -> None:
    """Test that only one config entry is allowed."""
    # Create first entry
    MockConfigEntry(
        domain=DOMAIN,
        data={CONF_WEBHOOK_ID: "existing_webhook_id"},
    ).add_to_hass(hass)

    # Try to create second entry - should be aborted
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"


async def test_webhook_flow_with_cloudhook(
    hass: HomeAssistant, mock_setup_entry: AsyncMock
) -> None:
    """Test webhook flow with cloudhook enabled automatically when cloud is available."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM

    with (
        patch(
            "homeassistant.components.webhook.async_generate_id",
            return_value="webhook_id",
        ),
        patch(
            "homeassistant.components.cloud.async_active_subscription",
            return_value=True,
        ),
        patch(
            "homeassistant.components.cloud.async_is_connected",
            return_value=True,
        ),
        patch(
            "homeassistant.components.cloud.async_create_cloudhook",
            return_value="https://hooks.nabu.casa/webhook_id",
        ),
        patch.object(hass.config, "components", {"cloud"}),
    ):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Geofency Webhook"
    assert result["data"] == {
        "cloudhook": True,
        CONF_WEBHOOK_ID: "webhook_id",
    }
    assert result["description_placeholders"] == {
        "docs_url": "https://www.home-assistant.io/integrations/geofency/",
        "webhook_url": "https://hooks.nabu.casa/webhook_id",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_webhook_flow_cloud_not_connected(hass: HomeAssistant) -> None:
    """Test webhook flow aborts when cloud is not connected."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM

    with (
        patch(
            "homeassistant.components.webhook.async_generate_id",
            return_value="webhook_id",
        ),
        patch(
            "homeassistant.components.cloud.async_active_subscription",
            return_value=True,
        ),
        patch(
            "homeassistant.components.cloud.async_is_connected",
            return_value=False,
        ),
        patch.object(hass.config, "components", {"cloud"}),
    ):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "cloud_not_connected"
