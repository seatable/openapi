"""Tests for the base/table import endpoints (Import & Export group).

These go through schemathesis ``Case`` like the rest of the suite, so the
``after_call`` hook validates every response against the OpenAPI schema. The
multipart file part itself is passed via ``case.call(files=..., data=...)``
(forwarded to ``requests``): schemathesis's own multipart serializer never emits
a filename, but these endpoints read ``request.FILES`` and reject a file part
without one (``{"error_msg": "file invalid."}``).

Bases created by the import-to-base endpoints are made inside the shared ``base``
fixture's workspace and registered with ``cleanup_bases`` so they are deleted
before the module's group teardown (a group with remaining bases cannot be
deleted).
"""

import pytest
from conftest import Base, Secret, base_operations_schema, user_account_operations
from schemathesis import Case

from test_base_operations import create_table, append_rows


NAME_NUMBER_COLUMNS = [
    {'column_name': 'Name', 'column_type': 'text'},
    {'column_name': 'Number', 'column_type': 'number'},
]

# CSV whose header row matches NAME_NUMBER_COLUMNS
CSV = b'Name,Number\nAlice,1\nBob,2\n'


@pytest.fixture
def cleanup_bases(base: Base, account_token: Secret):
    """Delete bases created during a test before the module's group teardown runs
    (a group with remaining bases cannot be deleted). Register a base name before
    creating it; cleanup is best-effort."""
    names: list[str] = []
    yield names
    for name in names:
        case: Case = user_account_operations.find_operation_by_id('deleteBase').Case(
            path_parameters={'workspace_id': base.workspace_id},
            body={'name': name},
        )
        case.call(headers={'Authorization': f'Bearer {account_token.value}'})


def _list_rows(base: Base, table_name: str) -> list[dict]:
    """Read a table's rows back once (keyed by column name)."""
    case: Case = base_operations_schema.find_operation_by_id('listRows').Case(
        path_parameters={'base_uuid': base.uuid},
        query={'table_name': table_name, 'convert_keys': True},
        headers={'Authorization': f'Bearer {base.token}'},
    )
    response = case.call()
    assert response.status_code == 200
    return response.json()['rows']


def test_importBasefromFile(base: Base, account_token: Secret, cleanup_bases: list[str]):
    """Create a new base by uploading a CSV file."""
    cleanup_bases.append('test_importBasefromFile')
    case: Case = user_account_operations.find_operation_by_id('importBasefromFile').Case(
        path_parameters={'workspace_id': base.workspace_id},
        headers={'Authorization': f'Bearer {account_token.value}'},
    )
    response = case.call(files={'dtable': ('test_importBasefromFile.csv', CSV, 'text/csv')})

    assert response.status_code == 200
    assert response.json()['success'] is True


def test_importBasefromDTableFile(base: Base, account_token: Secret, cleanup_bases: list[str]):
    """Create a new base by uploading a .dtable file (obtained by exporting a base)."""
    cleanup_bases.append('test_importBasefromDTableFile')
    headers = {'Authorization': f'Bearer {account_token.value}'}

    # Export the shared base to get a valid .dtable file to import
    export_case: Case = user_account_operations.find_operation_by_id('exportBase').Case(
        path_parameters={'workspace_id': base.workspace_id},
        query={'dtable_name': base.name},
        headers=headers,
    )
    exported = export_case.call()
    assert exported.status_code == 200

    case: Case = user_account_operations.find_operation_by_id('importBasefromDTableFile').Case(
        path_parameters={'workspace_id': base.workspace_id},
        headers=headers,
    )
    response = case.call(
        files={'dtable': ('test_importBasefromDTableFile.dtable', exported.content, 'application/x-zip-compressed')},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data['task_id'], str)
    assert data['table']['name'] == 'test_importBasefromDTableFile'


def test_importTableFromFile(base: Base, account_token: Secret):
    """Import a CSV file as a new table in an existing base."""
    case: Case = user_account_operations.find_operation_by_id('importTableFromFile').Case(
        path_parameters={'workspace_id': base.workspace_id},
        headers={'Authorization': f'Bearer {account_token.value}'},
    )
    response = case.call(
        data={'dtable_uuid': base.uuid},
        files={'file': ('test_importTableFromFile.csv', CSV, 'text/csv')},
    )

    assert response.status_code == 200
    assert response.json()['success'] is True

    # The new table is named after the uploaded file
    rows = _list_rows(base, 'test_importTableFromFile')
    assert len(rows) == 2


def test_appendToTableFromFile(base: Base, account_token: Secret):
    """Append rows from a CSV file to an existing table."""
    table_name = 'test_appendToTableFromFile'
    create_table(base, table_name, NAME_NUMBER_COLUMNS)

    case: Case = user_account_operations.find_operation_by_id('appendToTableFromFile').Case(
        path_parameters={'workspace_id': base.workspace_id},
        headers={'Authorization': f'Bearer {account_token.value}'},
    )
    response = case.call(
        data={'dtable_uuid': base.uuid, 'table_name': table_name},
        files={'file': ('append.csv', CSV, 'text/csv')},
    )

    assert response.status_code == 200
    assert response.json()['success'] is True

    rows = _list_rows(base, table_name)
    assert {r['Name'] for r in rows} == {'Alice', 'Bob'}


def test_updateFromFile(base: Base, account_token: Secret):
    """Update matched rows and insert unmatched rows from a CSV file."""
    table_name = 'test_updateFromFile'
    create_table(base, table_name, NAME_NUMBER_COLUMNS)
    append_rows(base, table_name, [{'Name': 'Alice', 'Number': 1}])

    # Alice matches the existing row (updated to 99); Charlie is new (inserted)
    csv = b'Name,Number\nAlice,99\nCharlie,3\n'
    case: Case = user_account_operations.find_operation_by_id('updateFromFile').Case(
        path_parameters={'workspace_id': base.workspace_id},
        headers={'Authorization': f'Bearer {account_token.value}'},
    )
    response = case.call(
        data={'dtable_uuid': base.uuid, 'table_name': table_name, 'selected_columns': 'Name'},
        files={'file': ('update.csv', csv, 'text/csv')},
    )

    assert response.status_code == 200
    assert response.json()['success'] is True

    rows = {r['Name']: r['Number'] for r in _list_rows(base, table_name)}
    assert rows['Alice'] == 99
    assert rows['Charlie'] == 3
