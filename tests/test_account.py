from conftest import Secret, user_account_operations
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.filters import props
from syrupy.matchers import path_type


def test_getAccountInfo(account_token: Secret, snapshot_json: SnapshotAssertion):
    headers = {'Authorization': f'Bearer {account_token.value}'}

    case: Case = user_account_operations.get_operation_by_id('getAccountInfo').make_case()
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert 'email' in data
    assert 'name' in data
    assert isinstance(data['usage'], int)
    assert isinstance(data['total'], int)

    matcher = path_type({
        'email': (str,),
        'avatar_url': (str,),
        'login_id': (str,),
        'contact_email': (str,),
        'space_usage': (str,),
        'row_total': (int,),
        'row_usage_rate': (str,),
        'row_usage': (int,),
        'total': (int,),
    })

    assert snapshot_json(
        # v6.1+
        exclude=props('automation_count', 'automation_limit', 'automation_usage_rate'),
        matcher=matcher,
    ) == data


def test_listWorkspaces(account_token: Secret, snapshot_json: SnapshotAssertion):
    headers = {'Authorization': f'Bearer {account_token.value}'}

    case: Case = user_account_operations.get_operation_by_id('listWorkspaces').make_case()
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert 'workspace_list' in data
    assert isinstance(data['workspace_list'], list)
