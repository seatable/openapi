import pytest
from conftest import Base, base_operations_schema
from schemathesis import Case

from test_base_operations import create_table, append_rows


SIMPLE_COLUMNS = [
    {'column_name': 'text', 'column_type': 'text'},
]


def _headers(base):
    return {'Authorization': f'Bearer {base.token}'}


def test_listRowComments(base: Base):
    """Test listing comments for a row."""
    table_name = 'test_listRowComments'
    create_table(base, table_name, SIMPLE_COLUMNS)
    row_ids = append_rows(base, table_name, [{'text': 'target'}])

    case: Case = base_operations_schema.find_operation_by_id('listRowComments') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            query={'row_id': row_ids[0]},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200
    data = response.json()
    assert 'comment_list' in data
    assert 'count' in data


def test_getRowCommentsCount(base: Base):
    table_name = 'test_getRowCommentsCount'
    create_table(base, table_name, SIMPLE_COLUMNS)
    row_ids = append_rows(base, table_name, [{'text': 'target'}])

    case: Case = base_operations_schema.find_operation_by_id('getRowCommentsCount') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            query={'row_id': row_ids[0]},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200
    data = response.json()
    assert 'count' in data


def test_getNumberOfComments(base: Base):
    case: Case = base_operations_schema.find_operation_by_id('getNumberOfComments') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200


def _table_id(base: Base, table_name: str) -> str:
    metadata: Case = base_operations_schema.find_operation_by_id('getMetadata') \
        .Case(path_parameters={'base_uuid': base.uuid}, headers=_headers(base))
    tables = metadata.call().json()['metadata']['tables']
    return next(t['_id'] for t in tables if t['name'] == table_name)


def _list_comment_ids(base: Base, row_id: str) -> list[int]:
    """createRowComment does not return the new comment's id, so list the row comments."""
    case: Case = base_operations_schema.find_operation_by_id('listRowComments') \
        .Case(path_parameters={'base_uuid': base.uuid}, query={'row_id': row_id}, headers=_headers(base))
    data = case.call().json()
    return [comment['id'] for comment in data['comment_list']]


def test_deleteComment(base: Base):
    table_name = 'test_deleteComment'
    create_table(base, table_name, SIMPLE_COLUMNS)
    row_ids = append_rows(base, table_name, [{'text': 'delete target'}])

    create: Case = base_operations_schema.find_operation_by_id('createRowComment') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            body={
                'table_id': _table_id(base, table_name),
                'row_id': row_ids[0],
                'comment': 'Test comment from automated tests',
            },
            headers=_headers(base),
        )
    create_response = create.call()
    assert create_response.status_code == 200, \
        f'Failed to create comment: {create_response.status_code} {create_response.text}'

    comment_ids = _list_comment_ids(base, row_ids[0])
    assert len(comment_ids) == 1
    comment_id = comment_ids[0]

    case: Case = base_operations_schema.find_operation_by_id('deleteComment') \
        .Case(
            path_parameters={'base_uuid': base.uuid, 'comment_id': comment_id},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200
    data = response.json()
    assert data.get('success') is True
