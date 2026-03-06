from conftest import Base, Secret, user_account_operations
from schemathesis import Case


def test_favorite_lifecycle(base: Base, account_token: Secret):
    """Tests favoriteBase, listFavorites, unfavoriteBase in sequence."""
    headers = {'Authorization': f'Bearer {account_token.value}'}

    # 1. Favorite the base
    body = {'dtable_uuid': base.uuid}
    case: Case = user_account_operations.get_operation_by_id('favoriteBase') \
        .make_case(body=body)
    response = case.call(headers=headers)

    assert response.status_code == 200
    assert response.json()['success'] is True

    # 2. List favorites and verify it's there
    case: Case = user_account_operations.get_operation_by_id('listFavorites').make_case()
    response = case.call(headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert 'user_starred_dtable_list' in data
    starred_uuids = [d['uuid'] for d in data['user_starred_dtable_list']]
    assert base.uuid in starred_uuids

    # 3. Unfavorite
    query = {'dtable_uuid': base.uuid}
    case: Case = user_account_operations.get_operation_by_id('unfavoriteBase') \
        .make_case(query=query)
    response = case.call(headers=headers)

    assert response.status_code == 200
    assert response.json()['success'] is True

    # 4. Verify it's gone
    case: Case = user_account_operations.get_operation_by_id('listFavorites').make_case()
    response = case.call(headers=headers)

    assert response.status_code == 200
    starred_uuids = [d['uuid'] for d in response.json()['user_starred_dtable_list']]
    assert base.uuid not in starred_uuids
