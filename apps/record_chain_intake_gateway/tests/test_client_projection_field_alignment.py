from apps.record_chain_intake_gateway.app import _UNSIGNED_CLIENT_PROJECTION_FIELDS
from apps.record_chain_intake_gateway.gateway.authorship import UNSIGNED_PROJECTION_FIELDS


def test_gateway_rejects_every_field_removed_from_signed_pending_domain() -> None:
    assert _UNSIGNED_CLIENT_PROJECTION_FIELDS == UNSIGNED_PROJECTION_FIELDS
