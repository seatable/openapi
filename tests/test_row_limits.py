"""Size limits for the row endpoints (see intro/limits.md).

Observed behaviour (SeaTable 7.0, Go and JS dtable-server):

- listRows returns at most 1,000 rows per call. Larger ``limit`` values are
  silently capped, so clients must paginate with ``start``/``limit``.
- appendRows and updateRow accept at most 1,000 rows, deleteRow at most 10,000
  row IDs. Larger requests fail with HTTP 413 and nothing is changed.
- lockRows and unlockRows have no row limit.
"""

import pytest
import requests
import secrets
import string
from conftest import Base, BASE_URL, USES_GO_DTABLE_SERVER, base_operations_schema
from schemathesis import Case

from test_base_operations import create_table, append_rows


TABLE_NAME = 'test_row_limits'
ROW_LIMIT = 1000
DELETE_LIMIT = 10000


def _headers(base: Base) -> dict:
    return {'Authorization': f'Bearer {base.token}'}


def _random_row_id() -> str:
    """Syntactically valid row ID that does not exist in the table."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(22))


def _rows_url(base: Base) -> str:
    return f'{BASE_URL}/api-gateway/api/v2/dtables/{base.uuid}/rows/'


def _list_rows(base: Base, **query) -> list[dict]:
    case: Case = base_operations_schema.find_operation_by_id('listRows') \
        .Case(path_parameters={'base_uuid': base.uuid},
              query={'table_name': TABLE_NAME, **query},
              headers=_headers(base))
    response = case.call()
    assert response.status_code == 200
    return response.json()['rows']


def _list_all_rows(base: Base) -> list[dict]:
    rows, start = [], 0
    while True:
        page = _list_rows(base, start=start, limit=ROW_LIMIT)
        rows += page
        if len(page) < ROW_LIMIT:
            return rows
        start += ROW_LIMIT


@pytest.fixture(scope='module')
def row_ids(base: Base) -> list[str]:
    """Table with ROW_LIMIT + 1 rows (two appendRows calls, since one call is capped)."""
    create_table(base, TABLE_NAME, [{'column_name': 'text', 'column_type': 'text'}])
    ids = append_rows(base, TABLE_NAME, [{'text': f'row-{i}'} for i in range(ROW_LIMIT)])
    ids += append_rows(base, TABLE_NAME, [{'text': f'row-{ROW_LIMIT}'}])
    assert len(ids) == ROW_LIMIT + 1
    return ids


# listRows

def test_listRows_default_limit(base: Base, row_ids: list[str]):
    assert len(_list_rows(base)) == ROW_LIMIT


def test_listRows_limit_above_maximum_is_capped(base: Base, row_ids: list[str]):
    # No error: the server silently returns only ROW_LIMIT rows
    assert len(_list_rows(base, limit=ROW_LIMIT + 1)) == ROW_LIMIT


def test_listRows_pagination_returns_all_rows(base: Base, row_ids: list[str]):
    assert len(_list_rows(base, start=ROW_LIMIT, limit=ROW_LIMIT)) == 1
    assert {r['_id'] for r in _list_all_rows(base)} == set(row_ids)


# appendRows

def test_appendRows_above_limit(base: Base, row_ids: list[str]):
    # Bypasses the schema hook: the JS dtable-server returns a non-JSON body (see test below)
    body = {'table_name': TABLE_NAME, 'rows': [{'text': 'too-many'}] * (ROW_LIMIT + 1)}
    response = requests.post(_rows_url(base), json=body, headers=_headers(base))

    assert response.status_code == 413
    assert len(_list_all_rows(base)) == ROW_LIMIT + 1


@pytest.mark.xfail(
    not USES_GO_DTABLE_SERVER,
    reason="appendRows returns the plain-text body 'Exceed the operation limit on rows' "
           "with an application/json content-type on 413 (not valid JSON)",
)
def test_appendRows_above_limit_returns_json(base: Base, row_ids: list[str]):
    body = {'table_name': TABLE_NAME, 'rows': [{'text': 'too-many'}] * (ROW_LIMIT + 1)}
    case: Case = base_operations_schema.find_operation_by_id('appendRows') \
        .Case(path_parameters={'base_uuid': base.uuid}, body=body, headers=_headers(base))
    response = case.call()

    assert response.status_code == 413
    assert 'error_message' in response.json()


# updateRow

def _update_rows(base: Base, ids: list[str]):
    body = {
        'table_name': TABLE_NAME,
        'updates': [{'row_id': row_id, 'row': {'text': 'updated'}} for row_id in ids],
    }
    case: Case = base_operations_schema.find_operation_by_id('updateRow') \
        .Case(path_parameters={'base_uuid': base.uuid}, body=body, headers=_headers(base))
    return case.call()


def test_updateRow_at_limit(base: Base, row_ids: list[str]):
    response = _update_rows(base, row_ids[:ROW_LIMIT])
    assert response.status_code == 200


def test_updateRow_above_limit(base: Base, row_ids: list[str]):
    response = _update_rows(base, row_ids)

    assert response.status_code == 413
    assert 'error_message' in response.json()


# deleteRow (limit is checked before row IDs are resolved, so random IDs suffice)

def _delete_rows(base: Base, ids: list[str]):
    body = {'table_name': TABLE_NAME, 'row_ids': ids}
    case: Case = base_operations_schema.find_operation_by_id('deleteRow') \
        .Case(path_parameters={'base_uuid': base.uuid}, body=body, headers=_headers(base))
    return case.call()


def test_deleteRow_at_limit(base: Base, row_ids: list[str]):
    response = _delete_rows(base, [_random_row_id() for _ in range(DELETE_LIMIT)])
    assert response.status_code == 200


def test_deleteRow_above_limit(base: Base, row_ids: list[str]):
    response = _delete_rows(base, [_random_row_id() for _ in range(DELETE_LIMIT + 1)])

    assert response.status_code == 413
    assert 'error_message' in response.json()


# lockRows / unlockRows (no limit)

def _call_lock_operation(base: Base, operation_id: str, ids: list[str]):
    body = {'table_name': TABLE_NAME, 'row_ids': ids}
    case: Case = base_operations_schema.find_operation_by_id(operation_id) \
        .Case(path_parameters={'base_uuid': base.uuid}, body=body, headers=_headers(base))
    response = case.call()
    assert response.status_code == 200


def test_lockRows_unlockRows_above_row_limit(base: Base, row_ids: list[str]):
    _call_lock_operation(base, 'lockRows', row_ids)
    assert sum(1 for r in _list_all_rows(base) if r.get('_locked')) == len(row_ids)

    _call_lock_operation(base, 'unlockRows', row_ids)
    assert not any(r.get('_locked') for r in _list_all_rows(base))


@pytest.mark.parametrize('operation_id', ['lockRows', 'unlockRows'])
def test_lockRows_unlockRows_above_delete_limit(base: Base, row_ids: list[str], operation_id: str):
    _call_lock_operation(base, operation_id, [_random_row_id() for _ in range(DELETE_LIMIT + 1)])


# Runs last: deletes all rows of the shared table

def test_deleteRow_above_row_limit(base: Base, row_ids: list[str]):
    response = _delete_rows(base, row_ids)

    assert response.status_code == 200
    assert _list_all_rows(base) == []
    assert response.json() == {'deleted_rows': len(row_ids)}
