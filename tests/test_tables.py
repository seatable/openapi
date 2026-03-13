from conftest import Base, base_operations_schema, normalize, normalize_row
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type

from test_base_operations import create_table, append_rows


def test_renameTable(base: Base):
    create_table(base, 'test_renameTable', [{'column_name': 'text', 'column_type': 'text'}])

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}
    body = {'table_name': 'test_renameTable', 'new_table_name': 'test_renameTable_renamed'}

    case: Case = base_operations_schema.find_operation_by_id('renameTable') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200
    assert response.json()['success'] is True


def test_duplicateTable(base: Base, snapshot_json: SnapshotAssertion):
    create_table(base, 'test_duplicateTable', [
        {'column_name': 'text', 'column_type': 'text'},
        {'column_name': 'number', 'column_type': 'number'},
    ])
    append_rows(base, 'test_duplicateTable', [
        {'text': 'row-1', 'number': 1},
        {'text': 'row-2', 'number': 2},
    ])

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}
    body = {'table_name': 'test_duplicateTable', 'is_duplicate_records': True}

    case: Case = base_operations_schema.find_operation_by_id('duplicateTable') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200

    data = response.json()

    # Normalize volatile row data for stable snapshots
    data['rows'] = sorted(
        [normalize_row(r) for r in data['rows']],
        key=lambda r: r.get('0000', ''),
    )
    id_rows = sorted(data['id_row_map'].values(), key=lambda r: r.get('0000', ''))
    data['id_row_map'] = {
        f'row_{i}': normalize_row(r) for i, r in enumerate(id_rows)
    }

    matcher = path_type({
        '_id': (str,),
        r"columns\..*\.key": (str,),
    }, regex=True)

    assert snapshot_json(matcher=matcher) == data


def test_deleteTable(base: Base):
    create_table(base, 'test_deleteTable', [{'column_name': 'text', 'column_type': 'text'}])

    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': f'Bearer {base.token}'}
    body = {'table_name': 'test_deleteTable'}

    case: Case = base_operations_schema.find_operation_by_id('deleteTable') \
        .Case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call()

    assert response.status_code == 200
    assert response.json()['success'] is True
