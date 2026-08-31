"""Tests for the base asset endpoints."""

from conftest import Base, Secret, user_account_operations
from schemathesis import Case


def test_getBaseAssetSize(base: Base, account_token: Secret):
    """A base without attachments reports a size of 0 and can be exported with its assets."""
    case: Case = user_account_operations.find_operation_by_id('getBaseAssetSize') \
        .Case(path_parameters={'base_uuid': base.uuid})
    response = case.call(headers={'Authorization': f'Bearer {account_token.value}'})

    assert response.status_code == 200
    assert response.json() == {
        'asset_size': 0,
        'max_size_of_export': 100,
        'unit': 'mb',
        'can_export_asset': True,
    }
