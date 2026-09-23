from conftest import Base, base_operations_schema
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type

from test_base_operations import create_table, append_rows


SIMPLE_COLUMNS = [
    {'column_name': 'text', 'column_type': 'text'},
]


def _headers(base):
    return {'Authorization': f'Bearer {base.token}'}


def test_listRowComments(base: Base, snapshot_json: SnapshotAssertion):
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
    assert snapshot_json == response.json()


def test_getRowCommentsCount(base: Base, snapshot_json: SnapshotAssertion):
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
    assert snapshot_json == response.json()


def test_listCommentsWithinDays(base: Base, snapshot_json: SnapshotAssertion):
    case: Case = base_operations_schema.find_operation_by_id('listCommentsWithinDays') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            query={'days': 7},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200
    assert snapshot_json == response.json()


def test_getNumberOfComments(base: Base, snapshot_json: SnapshotAssertion):
    case: Case = base_operations_schema.find_operation_by_id('getNumberOfComments') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200
    assert snapshot_json == response.json()


def _table_id(base: Base, table_name: str) -> str:
    metadata: Case = base_operations_schema.find_operation_by_id('getMetadata') \
        .Case(path_parameters={'base_uuid': base.uuid}, headers=_headers(base))
    tables = metadata.call().json()['metadata']['tables']
    return next(t['_id'] for t in tables if t['name'] == table_name)


def _list_comment_ids(base: Base, row_id: str) -> list[int]:
    """createRowComment does not return the new comment's id, so look it up via listRowComments."""
    case: Case = base_operations_schema.find_operation_by_id('listRowComments') \
        .Case(path_parameters={'base_uuid': base.uuid}, query={'row_id': row_id}, headers=_headers(base))
    return [c['id'] for c in case.call().json()]


def test_getComment(base: Base, snapshot_json: SnapshotAssertion):
    table_name = 'test_getComment'
    create_table(base, table_name, SIMPLE_COLUMNS)
    row_ids = append_rows(base, table_name, [{'text': 'comment target'}])

    comment_text = 'Test comment from automated tests'
    create: Case = base_operations_schema.find_operation_by_id('createRowComment') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            query={'table_id': _table_id(base, table_name), 'row_id': row_ids[0]},
            body={'comment': comment_text},
            headers=_headers(base),
        )
    create_response = create.call()
    assert create_response.status_code == 200, \
        f'Failed to create comment: {create_response.status_code} {create_response.text}'

    # createRowComment does not return the comment ID, so we need to fetch all comments for this row
    comment_ids = _list_comment_ids(base, row_ids[0])
    assert len(comment_ids) == 1
    comment_id = comment_ids[0]

    case: Case = base_operations_schema.find_operation_by_id('getComment') \
        .Case(
            path_parameters={'base_uuid': base.uuid, 'comment_id': comment_id},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200
    data = response.json()
    assert data['id'] == comment_id
    # dtable_uuid is masked in the snapshot, so check its format (with dashes) here
    assert data['dtable_uuid'] == base.uuid

    matcher = path_type({
        'author': (str,),
        'created_at': (str,),
        'dtable_uuid': (str,),
        'id': (int,),
        'row_id': (str,),
        'updated_at': (str,),
    })

    assert snapshot_json(matcher=matcher) == data


def test_deleteComment(base: Base, snapshot_json: SnapshotAssertion):
    table_name = 'test_deleteComment'
    create_table(base, table_name, SIMPLE_COLUMNS)
    row_ids = append_rows(base, table_name, [{'text': 'delete target'}])

    create: Case = base_operations_schema.find_operation_by_id('createRowComment') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            query={'table_id': _table_id(base, table_name), 'row_id': row_ids[0]},
            body={'comment': 'Test comment from automated tests'},
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
    assert snapshot_json == response.json()


def _create_row_with_comments(base: Base, table_name: str, comments: list[str]) -> str:
    create_table(base, table_name, SIMPLE_COLUMNS)
    row_id = append_rows(base, table_name, [{'text': 'comment target'}])[0]
    table_id = _table_id(base, table_name)

    for comment in comments:
        create: Case = base_operations_schema.find_operation_by_id('createRowComment') \
            .Case(
                path_parameters={'base_uuid': base.uuid},
                query={'table_id': table_id, 'row_id': row_id},
                body={'comment': comment},
                headers=_headers(base),
            )
        create_response = create.call()
        assert create_response.status_code == 200, \
            f'Failed to create comment: {create_response.status_code} {create_response.text}'

    return row_id


MULTIPLE_COMMENTS = ['First comment', 'Second comment']

COMMENT_MATCHER = path_type({
    r'(.*\.)?author': (str,),
    r'(.*\.)?created_at': (str,),
    r'(.*\.)?dtable_uuid': (str,),
    r'(.*\.)?id': (int,),
    r'(.*\.)?row_id': (str,),
    r'(.*\.)?updated_at': (str,),
}, regex=True)


def test_listRowComments_multiple_comments(base: Base, snapshot_json: SnapshotAssertion):
    row_id = _create_row_with_comments(base, 'test_listRowComments_multiple_comments', MULTIPLE_COMMENTS)

    case: Case = base_operations_schema.find_operation_by_id('listRowComments') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            query={'row_id': row_id},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200
    data = response.json()
    # dtable_uuid is masked in the snapshot, so check its format (with dashes) here
    assert all(c['dtable_uuid'] == base.uuid for c in data)
    assert snapshot_json(matcher=COMMENT_MATCHER) == data


def test_getRowCommentsCount_multiple_comments(base: Base, snapshot_json: SnapshotAssertion):
    row_id = _create_row_with_comments(base, 'test_getRowCommentsCount_multiple_comments', MULTIPLE_COMMENTS)

    case: Case = base_operations_schema.find_operation_by_id('getRowCommentsCount') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            query={'row_id': row_id},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200
    assert snapshot_json == response.json()


def test_listCommentsWithinDays_multiple_comments(base: Base, snapshot_json: SnapshotAssertion):
    row_id = _create_row_with_comments(base, 'test_listCommentsWithinDays_multiple_comments', MULTIPLE_COMMENTS)

    case: Case = base_operations_schema.find_operation_by_id('listCommentsWithinDays') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            query={'days': 7},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200
    data = response.json()

    # The endpoint lists all comments in the (module-scoped) base, so only keep this row's comments
    data['comments'] = [c for c in data['comments'] if c['row_id'] == row_id]
    # dtable_uuid is masked in the snapshot, so check its format (with dashes) here
    assert all(c['dtable_uuid'] == base.uuid for c in data['comments'])

    assert snapshot_json(matcher=COMMENT_MATCHER) == data


def test_getNumberOfComments_multiple_comments(base: Base, snapshot_json: SnapshotAssertion):
    row_id = _create_row_with_comments(base, 'test_getNumberOfComments_multiple_comments', MULTIPLE_COMMENTS)

    case: Case = base_operations_schema.find_operation_by_id('getNumberOfComments') \
        .Case(
            path_parameters={'base_uuid': base.uuid},
            headers=_headers(base),
        )
    response = case.call()

    assert response.status_code == 200
    data = response.json()

    # The response is keyed by row ID and covers all rows in the (module-scoped) base
    assert data['rows_comments_num'][row_id] == 2
