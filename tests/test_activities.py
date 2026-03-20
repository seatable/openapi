import pytest
from conftest import Base, base_operations_schema
from schemathesis import Case

from test_base_operations import create_table, append_rows


def _headers(base):
    return {'Authorization': f'Bearer {base.token}'}


def test_getBaseActivityLog(base: Base):
    # Generate some activity first
    SIMPLE_COLUMNS = [{'column_name': 'text', 'column_type': 'text'}]
    table_name = 'test_activity_log'
    create_table(base, table_name, SIMPLE_COLUMNS)
    append_rows(base, table_name, [{'text': 'activity row'}])

    case: Case = base_operations_schema.find_operation_by_id('getBaseActivityLog') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            query={'page': 1, 'per_page': 25},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200
    data = response.json()
    assert 'operations' in data


def test_listRowActivities(base: Base):
    SIMPLE_COLUMNS = [{'column_name': 'text', 'column_type': 'text'}]
    table_name = 'test_row_activities'
    create_table(base, table_name, SIMPLE_COLUMNS)
    row_ids = append_rows(base, table_name, [{'text': 'activity target'}])

    case: Case = base_operations_schema.find_operation_by_id('listRowActivities') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            query={'row_id': row_ids[0], 'page': 1, 'per_page': 25},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200
    data = response.json()
    assert 'activities' in data


def test_createSnapshot(base: Base):
    case: Case = base_operations_schema.find_operation_by_id('createSnapshot') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            body={'dtable_name': 'Automated Tests'},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200
    data = response.json()
    # API may return {"snapshot": ...} or {"status": "time_is_short"} if called too frequently
    assert 'snapshot' in data or 'success' in data or 'status' in data
