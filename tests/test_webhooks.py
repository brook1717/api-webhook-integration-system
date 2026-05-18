import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

VALID_PAYLOAD = {
    "order_id": "ORD-12345",
    "customer_email": "test@example.com",
    "total_amount": 99.99,
    "items": [{"name": "Widget", "qty": 2}],
}


class TestWebhookEndpoint:
    """Tests for POST /webhooks/event"""

    @patch("app.routes.webhooks.process_order_event")
    def test_valid_payload_returns_202(self, mock_process):
        response = client.post("/webhooks/event", json=VALID_PAYLOAD)

        assert response.status_code == 202
        body = response.json()
        assert body["message"] == "accepted"
        assert "event_id" in body

    @patch("app.routes.webhooks.process_order_event")
    def test_valid_payload_triggers_background_task(self, mock_process):
        response = client.post("/webhooks/event", json=VALID_PAYLOAD)

        assert response.status_code == 202
        mock_process.assert_called_once()
        args = mock_process.call_args[0]
        assert args[1]["order_id"] == "ORD-12345"

    def test_missing_required_field_returns_422(self):
        incomplete_payload = {
            "order_id": "ORD-99999",
            "total_amount": 50.0,
            "items": [],
        }
        response = client.post("/webhooks/event", json=incomplete_payload)

        assert response.status_code == 422

    def test_invalid_email_returns_422(self):
        bad_email_payload = {
            "order_id": "ORD-00001",
            "customer_email": "not-an-email",
            "total_amount": 10.0,
            "items": ["item1"],
        }
        response = client.post("/webhooks/event", json=bad_email_payload)

        assert response.status_code == 422

    def test_invalid_amount_type_returns_422(self):
        bad_amount_payload = {
            "order_id": "ORD-00002",
            "customer_email": "user@test.com",
            "total_amount": "not_a_number",
            "items": [],
        }
        response = client.post("/webhooks/event", json=bad_amount_payload)

        assert response.status_code == 422

    @patch("app.routes.webhooks.process_order_event")
    def test_response_contains_valid_uuid(self, mock_process):
        import uuid

        response = client.post("/webhooks/event", json=VALID_PAYLOAD)
        event_id = response.json()["event_id"]

        parsed = uuid.UUID(event_id)
        assert str(parsed) == event_id

    def test_empty_body_returns_422(self):
        response = client.post("/webhooks/event", json={})

        assert response.status_code == 422

    @patch("app.routes.webhooks.process_order_event")
    def test_extra_fields_are_ignored(self, mock_process):
        payload_with_extras = {**VALID_PAYLOAD, "unexpected_field": "should be fine"}
        response = client.post("/webhooks/event", json=payload_with_extras)

        assert response.status_code == 202
