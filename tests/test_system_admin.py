import schemathesis
from conftest import BASE_URL, Secret, system_admin_account_operations, USERNAME
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.filters import props
from syrupy.matchers import path_type


def test_getSystemInformation(system_admin_account_token: Secret, snapshot_json: SnapshotAssertion):
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}

    case: Case = system_admin_account_operations.get_operation_by_id('getSystemInformation').make_case()
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert 'version' in data
    assert isinstance(data['version'], str)
    assert isinstance(data['users_count'], int)
    assert isinstance(data['dtables_count'], int)
    assert data['with_license'] is True

    matcher = path_type({
        'version': (str,),
        'users_count': (int,),
        'active_users_count': (int,),
        'groups_count': (int,),
        'org_count': (int,),
        'dtables_count': (int,),
        'license_expiration': (str,),
        'license_to': (str,),
        'license_maxusers': (int,),
        r"dtable_server_info\..*\.web_socket_count": (int,),
        r"dtable_server_info\..*\.operation_count_since_up": (int,),
        r"dtable_server_info\..*\.loaded_dtables_count": (int,),
        r"dtable_server_info\..*\.last_period_operations_count": (int,),
        r"dtable_server_info\..*\.app_connection_count": (int,),
        r"dtable_server_info\..*\.last_dtable_saving_count": (int,),
        'archived_base_count': (int,),
        'archived_row_count': (int,),
        'archived_base_storage': (int,),
    }, regex=True)

    assert snapshot_json(
        # Exclude nullable props
        exclude=props('last_dtable_saving_start_time', 'last_dtable_saving_end_time'),
        matcher=matcher,
    ) == data


def test_listUsers(system_admin_account_token: Secret, snapshot_json: SnapshotAssertion):
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}
    query = {'page': 1, 'per_page': 25}

    case: Case = system_admin_account_operations.get_operation_by_id('listUsers') \
        .make_case(query=query)
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert 'data' in data
    assert isinstance(data['data'], list)
    assert data['total_count'] >= 2  # admin + testuser

    emails = [u['contact_email'] for u in data['data']]
    assert USERNAME in emails

    matcher = path_type({
        r"data\..*\.email": (str,),
        r"data\..*\.create_time": (str,),
        r"data\..*\.last_login": (str, type(None)),
        r"data\..*\.storage_usage": (int,),
        r"data\..*\.rows_count": (int,),
        r"data\..*\.avatar_url": (str,),
        r"data\..*\.workspace_id": (int,),
    }, regex=True)

    assert snapshot_json(matcher=matcher) == data


def test_getUser(system_admin_account_token: Secret, snapshot_json: SnapshotAssertion):
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}

    # First get user list to find the user_id
    case: Case = system_admin_account_operations.get_operation_by_id('listUsers').make_case()
    response = case.call(headers=headers)
    assert response.status_code == 200

    # Find testuser's email (auth.local format)
    user = next(u for u in response.json()['data'] if u['contact_email'] == USERNAME)
    user_id = user['email']

    # Get user details
    path_parameters = {'user_id': user_id}
    case: Case = system_admin_account_operations.get_operation_by_id('getUser') \
        .make_case(path_parameters=path_parameters)
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert data['contact_email'] == USERNAME

    matcher = path_type({
        'email': (str,),
        'create_time': (str,),
        'avatar_url': (str,),
        'row_limit': (int,),
        'storage_quota': (int,),
    })

    assert snapshot_json(matcher=matcher) == data
