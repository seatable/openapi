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
    """Test listing comments for a row.

    Note: API returns [] (array) when no comments exist, but
    {"comments": [...]} when comments exist. The schema says type:object
    which is only true when comments exist. We test the empty case here
    and accept both formats.
    """
    table_name = 'test_listRowComments'
    create_table(base, table_name, SIMPLE_COLUMNS)
    row_ids = append_rows(base, table_name, [{'text': 'target'}])

    import os, requests
    server = os.environ['SEATABLE_SERVER']
    resp = requests.get(
        f'{server}/api-gateway/api/v2/dtables/{base.uuid}/comments/',
        params={'row_id': row_ids[0]},
        headers=_headers(base),
    )

    assert resp.status_code == 200
    data = resp.json()
    # Empty: [] or {"comments": []}
    assert isinstance(data, (list, dict))


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


def test_listCommentsWithinDays(base: Base):
    case: Case = base_operations_schema.find_operation_by_id('listCommentsWithinDays') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            query={'days': 7},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200
    data = response.json()
    assert 'comments' in data


def test_getNumberOfComments(base: Base):
    case: Case = base_operations_schema.find_operation_by_id('getNumberOfComments') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200


def _create_comment(base: Base, row_id: str) -> int:
    """Helper: create a comment via direct API call, returns comment_id."""
    import os, requests
    server = os.environ['SEATABLE_SERVER']
    resp = requests.post(
        f'{server}/api-gateway/api/v2/dtables/{base.uuid}/comments/',
        json={'row_id': row_id, 'comment': 'Test comment from automated tests'},
        headers=_headers(base),
    )
    assert resp.status_code in (200, 201), f'Failed to create comment: {resp.status_code} {resp.text}'
    return resp.json()['id']


def test_getComment(base: Base):
    table_name = 'test_getComment'
    create_table(base, table_name, SIMPLE_COLUMNS)
    row_ids = append_rows(base, table_name, [{'text': 'comment target'}])
    comment_id = _create_comment(base, row_ids[0])

    case: Case = base_operations_schema.find_operation_by_id('getComment') \
        .Case(
            path_parameters={'base_uuid': base.uuid, 'comment_id': comment_id},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200
    data = response.json()
    assert data['id'] == comment_id
    assert 'comment' in data


def test_deleteComment(base: Base):
    table_name = 'test_deleteComment'
    create_table(base, table_name, SIMPLE_COLUMNS)
    row_ids = append_rows(base, table_name, [{'text': 'delete target'}])
    comment_id = _create_comment(base, row_ids[0])

    case: Case = base_operations_schema.find_operation_by_id('deleteComment') \
        .Case(
            path_parameters={'base_uuid': base.uuid, 'comment_id': comment_id},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200
    data = response.json()
    assert data.get('success') is True
