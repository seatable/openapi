"""Tests for the base/table/view export endpoints.

Background (ticket): the export endpoints return binary bodies with a specific
Content-Type (``application/x-zip-compressed`` for the ``.dtable`` zip exports,
``application/ms-excel`` for the Excel exports). Historically dtable-web rejected
those exact values in the request ``Accept`` header with
``406 Could not satisfy the request Accept header``, which forced the OpenAPI spec
to declare ``application/json`` as a workaround.

As of the version tested here, the bug is only *partially* fixed:

* Fixed  – the two ``.dtable`` zip exports in the user API accept their real
  media type. These are covered by regular (passing) tests below.
* Broken – the two Excel exports and the sys-admin ``export-dtable`` still return
  406 for their real media type (only ``*/*`` / ``application/json`` work). These
  are covered by ``xfail`` tests that assert the *desired* behaviour, so they will
  turn into ``XPASS`` once the backend is fixed — that is the signal to drop the
  ``application/json`` workaround from the spec and remove the ``xfail`` marker.
"""

import pytest
import requests
from conftest import (
    Base, BASE_URL, Secret,
    user_account_operations, system_admin_account_operations,
    base_operations_schema,
)
from schemathesis import Case

from test_base_operations import create_table, append_rows


SIMPLE_COLUMNS = [
    {'column_name': 'text', 'column_type': 'text'},
    {'column_name': 'number', 'column_type': 'number'},
]

ZIP_CONTENT_TYPE = 'application/x-zip-compressed'
EXCEL_CONTENT_TYPE = 'application/ms-excel'


def _first_table_and_view(base: Base, table_name: str) -> dict:
    """Create a populated table and return its id/name plus its default view id/name."""
    create_table(base, table_name, SIMPLE_COLUMNS)
    append_rows(base, table_name, [{'text': 'a', 'number': 1}, {'text': 'b', 'number': 2}])

    headers = {'Authorization': f'Bearer {base.token}'}
    case: Case = base_operations_schema.find_operation_by_id('getMetadata') \
        .Case(path_parameters={'base_uuid': base.uuid}, headers=headers)
    response = case.call()
    assert response.status_code == 200

    table = next(t for t in response.json()['metadata']['tables'] if t['name'] == table_name)
    view = table['views'][0]
    return {
        'table_id': table['_id'],
        'table_name': table['name'],
        'view_id': view['_id'],
        'view_name': view['name'],
    }


# --- Fixed: .dtable zip exports accept their real media type -----------------

def test_exportBase(base: Base, account_token: Secret):
    """Export a base as a .dtable zip, requesting the real media type via Accept."""
    response = requests.get(
        f'{BASE_URL}/api/v2.1/workspace/{base.workspace_id}/synchronous-export/export-dtable/',
        params={'dtable_name': base.name},
        headers={
            'Authorization': f'Bearer {account_token.value}',
            'Accept': ZIP_CONTENT_TYPE,
        },
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == ZIP_CONTENT_TYPE
    assert len(response.content) > 0


def test_exportBaseFromExternalLink(base: Base, account_token: Secret):
    """Download a base via its external link, requesting the real media type via Accept."""
    # Create a read-only external link for the base
    create_case: Case = user_account_operations.find_operation_by_id('createBaseExternalLink').Case(
        path_parameters={'workspace_id': base.workspace_id, 'base_name': base.name},
    )
    create_response = create_case.call(headers={'Authorization': f'Bearer {account_token.value}'})
    assert create_response.status_code == 200
    external_link_token = create_response.json()['token']

    # Download the zip (public endpoint, no auth required)
    response = requests.get(
        f'{BASE_URL}/dtable/external-links/{external_link_token}/download-zip/',
        headers={'Accept': ZIP_CONTENT_TYPE},
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == ZIP_CONTENT_TYPE
    assert len(response.content) > 0


def test_exportBigDataView(base: Base, account_token: Secret):
    """Trigger a big-data view Excel export; the endpoint returns an async task id."""
    table = _first_table_and_view(base, 'test_exportBigDataView')

    case: Case = user_account_operations.find_operation_by_id('exportBigDataView').Case(
        path_parameters={'workspace_id': base.workspace_id, 'base_name': base.name},
        query={'table_id': table['table_id'], 'view_id': table['view_id']},
        headers={'Authorization': f'Bearer {account_token.value}'},
    )
    response = case.call()

    assert response.status_code == 200
    assert isinstance(response.json()['task_id'], str)


# --- Still broken: Excel exports and admin export reject their real media type ---
#
# These use plain ``requests`` (not schemathesis ``Case``) on purpose: the spec
# still declares ``application/json`` as a workaround, so routing through the
# schemathesis ``after_call`` hook would make the test fail on content-type
# conformance even after the backend is fixed, defeating the XPASS signal.

@pytest.mark.xfail(
    reason="dtable-web returns 406 'Could not satisfy the request Accept header' when "
           "'application/ms-excel' is sent in the Accept header (only */* / application/json work)",
)
def test_exportTable_accepts_excel_content_type(base: Base, account_token: Secret):
    """The table Excel export should accept its real media type in the Accept header."""
    table = _first_table_and_view(base, 'test_exportTable')

    response = requests.get(
        f'{BASE_URL}/api/v2.1/workspace/{base.workspace_id}/synchronous-export/export-table-to-excel/',
        params={
            'table_id': table['table_id'],
            'table_name': table['table_name'],
            'dtable_name': base.name,
        },
        headers={
            'Authorization': f'Bearer {account_token.value}',
            'Accept': EXCEL_CONTENT_TYPE,
        },
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == EXCEL_CONTENT_TYPE
    assert len(response.content) > 0


@pytest.mark.xfail(
    reason="dtable-web returns 406 'Could not satisfy the request Accept header' when "
           "'application/ms-excel' is sent in the Accept header (only */* / application/json work)",
)
def test_exportView_accepts_excel_content_type(base: Base, account_token: Secret):
    """The view Excel export should accept its real media type in the Accept header."""
    table = _first_table_and_view(base, 'test_exportView')

    response = requests.get(
        f'{BASE_URL}/api/v2.1/workspace/{base.workspace_id}/synchronous-export/export-view-to-excel/',
        params={
            'table_id': table['table_id'],
            'table_name': table['table_name'],
            'dtable_name': base.name,
            'view_id': table['view_id'],
            'view_name': table['view_name'],
        },
        headers={
            'Authorization': f'Bearer {account_token.value}',
            'Accept': EXCEL_CONTENT_TYPE,
        },
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == EXCEL_CONTENT_TYPE
    assert len(response.content) > 0


@pytest.mark.needs_large_license
@pytest.mark.xfail(
    reason="dtable-web returns 406 'Could not satisfy the request Accept header' when "
           "'application/x-zip-compressed' is sent in the Accept header on the admin export "
           "endpoint (only */* / application/json work)",
)
def test_adminExportBase_accepts_zip_content_type(base: Base, system_admin_account_token: Secret):
    """The sys-admin base export should accept its real media type in the Accept header."""
    response = requests.get(
        f'{BASE_URL}/api/v2.1/admin/dtables/{base.uuid}/synchronous-export/export-dtable/',
        headers={
            'Authorization': f'Bearer {system_admin_account_token.value}',
            'Accept': ZIP_CONTENT_TYPE,
        },
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == ZIP_CONTENT_TYPE
    assert len(response.content) > 0
