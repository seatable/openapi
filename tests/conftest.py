import os
import pytest
import schemathesis
import secrets
import string
from dataclasses import dataclass, field
from datetime import datetime
from random import randint
from requests import Response
from schemathesis import Case
from syrupy.extensions.json import JSONSnapshotExtension
from typing import Generator

BASE_URL = os.environ.get('SEATABLE_SERVER')
USERNAME = os.environ.get('SEATABLE_USERNAME')
PASSWORD = os.environ.get('SEATABLE_PASSWORD')
ADMIN_USERNAME = os.environ.get('SEATABLE_ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('SEATABLE_ADMIN_PASSWORD')
CLEANUP_AFTER_TESTS = os.environ.get('CLEANUP_AFTER_TESTS', 'True')

assert BASE_URL is not None, 'SEATABLE_SERVER environment variable is not set'
assert USERNAME is not None, 'SEATABLE_USERNAME environment variable is not set'
assert PASSWORD is not None, 'SEATABLE_PASSWORD environment variable is not set'
assert ADMIN_USERNAME is not None, 'SEATABLE_ADMIN_USERNAME environment variable is not set'
assert ADMIN_PASSWORD is not None, 'SEATABLE_ADMIN_PASSWORD environment variable is not set'
assert CLEANUP_AFTER_TESTS in ["True", "False"], "CLEANUP_AFTER_TESTS environment variable must be either 'True' or 'False'"

# TODO: Make sure credentials are never logged to the console (in case of exceptions/assertion errors)
# https://github.com/pytest-dev/pytest/issues/8613

user_account_operations = schemathesis.from_path('../user_account_operations.yaml', base_url=BASE_URL, validate_schema=True)
system_admin_account_operations = schemathesis.from_path('../system_admin_account_operations.yaml', base_url=BASE_URL, validate_schema=True)
authentication_schema = schemathesis.from_path('../authentication.yaml', base_url=BASE_URL, validate_schema=True)
base_operations_schema = schemathesis.from_path('../base_operations.yaml', base_url=BASE_URL, validate_schema=True)

@schemathesis.hook
def after_call(context, case, response: Response):
    # TODO: Disable redirects for all tests? (to prevent issues like https://forum.seatable.com/t/seatable-4-4-out-now/4237/4)

    # Log all request URLs. You have to run pytest with '-rA' in order to see these for successful tests.
    print(f'{response.request.method} {response.request.url}')

@dataclass
class Base:
    """Class for storing base info"""
    workspace_id: int
    uuid: str
    # Hide base token from console output by setting repr=False
    token: str = field(repr=False)
    # Temporary API token for file uploads
    api_token: str = field(repr=False)

@dataclass
class TeamAdmin:
    """Class for storing team/org info"""
    team_id: int
    # Hide base token from console output by setting repr=False
    account_token: str = field(repr=False)

class Secret:
    """
    Class to store a secret, ensures that the value will not be printed (e.g. if an assertion fails)
    Based on https://github.com/pytest-dev/pytest/issues/8613#issuecomment-830011874
    """
    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        return "Secret(********)"

    def __str__(self):
        return "*******"

@pytest.fixture
def snapshot_json(snapshot):
    # https://github.com/tophat/syrupy#jsonsnapshotextension
    return snapshot.use_extension(JSONSnapshotExtension)

# scope='module' ensures that this functions runs only once for all tests in this module
@pytest.fixture(scope='module')
def account_token() -> str:
    body = {"username": USERNAME, "password": PASSWORD}

    operation = authentication_schema.get_operation_by_id('getAccountTokenfromUsername')
    case: Case = operation.make_case(body=body)
    response = case.call()

    assert response.status_code == 200

    account_token = response.json()['token']
    assert isinstance(account_token, str)

    return Secret(account_token)

@pytest.fixture(scope='module')
def base(account_token: Secret):
    group_name = f'Automated Tests {datetime.today().strftime("%Y-%m-%d %H-%M-%S")}'
    group_id, workspace_id = create_group(account_token=account_token, group_name=group_name)

    base_name = 'Automated Tests'

    body = {"workspace_id": workspace_id, "name": base_name}
    case: Case = user_account_operations.get_operation_by_id('createBase').make_case(body=body)
    response = case.call(headers={"Authorization": f"Bearer {account_token.value}"})

    assert response.status_code == 201

    base_uuid = response.json()["table"]["uuid"]
    assert isinstance(base_uuid, str)

    path_parameters = {'workspace_id': workspace_id, 'base_name': base_name}
    headers = {'Authorization': f'Bearer {account_token.value}'}

    operation = authentication_schema.get_operation_by_id('getBaseTokenWithAccountToken')
    case: Case = operation.make_case(path_parameters=path_parameters)
    response = case.call(headers=headers)

    assert response.status_code == 200

    base_token = response.json()['access_token']
    assert isinstance(base_token, str)

    # Get API token for file uploads
    api_token = get_api_token(account_token, workspace_id, base_name)

    # Yield back to the test function
    yield Base(workspace_id=workspace_id, uuid=base_uuid, token=base_token, api_token=api_token.value)

    if CLEANUP_AFTER_TESTS == 'True':
        # Delete base to not cause any issues on future test runs
        path_parameters = {'workspace_id': workspace_id}
        body = {'name': base_name}

        case: Case = user_account_operations.get_operation_by_id('deleteBase').make_case(path_parameters=path_parameters, body=body)
        response = case.call(headers={"Authorization": f"Bearer {account_token.value}"})

        assert response.status_code == 200

        delete_group(account_token, group_id)

def get_api_token(account_token: Secret, workspace_id: int, base_name: str) -> Secret:
    path_parameters = {'workspace_id': workspace_id, 'base_name': base_name}
    headers = {'Authorization': f'Bearer {account_token.value}'}
    case: Case = authentication_schema.get_operation_by_id('createTempApiToken').make_case(path_parameters=path_parameters)
    response = case.call(headers=headers)

    assert response.status_code == 200

    api_token = response.json()['api_token']
    assert isinstance(api_token, str)

    return Secret(api_token)

@pytest.fixture(scope='module')
def workspace_id(account_token: Secret) -> Generator[int, None, None]:
    base_name = "automated-testing-ahSh2sot"

    group_name = f'Automated Tests {datetime.today().strftime("%Y-%m-%d %H-%M-%S")} {randint(1, 100)}'
    group_id, workspace_id = create_group(account_token=account_token, group_name=group_name)

    yield workspace_id

    if CLEANUP_AFTER_TESTS == 'True':
        # Delete base to not cause any issues on future test runs
        path_parameters = {'workspace_id': workspace_id}
        body = {'name': base_name}

        case: Case = user_account_operations.get_operation_by_id('deleteBase').make_case(path_parameters=path_parameters, body=body)
        response = case.call(headers={"Authorization": f"Bearer {account_token.value}"})

        assert response.status_code == 200

        delete_group(account_token=account_token, group_id=group_id)

# scope='module' ensures that this functions runs only once for all tests in this module
@pytest.fixture(scope='module')
def system_admin_account_token() -> Secret:
    body = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}

    operation = authentication_schema.get_operation_by_id('getAccountTokenfromUsername')
    case: Case = operation.make_case(body=body)
    response = case.call()

    assert response.status_code == 200

    account_token = response.json()['token']
    assert isinstance(account_token, str)

    return Secret(account_token)

@pytest.fixture
def team(system_admin_account_token: Secret) -> Generator[int, None, None]:
    team_name = f'automated-testing-org-{randint(1, 10000)}'
    team_admin_email = 'automated-testing-team-admin@seatable.io'
    team_admin_password = generate_password()

    body = {
        'org_name': team_name,
        'admin_email': team_admin_email,
        'password': team_admin_password,
        'with_workspace': True,
    }
    case: Case = system_admin_account_operations.get_operation_by_id('addTeam').make_case(body=body)
    response = case.call(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})

    assert response.status_code == 200

    team = response.json()
    team_id = team['org_id']
    assert isinstance(team_id, int)

    # Fetch account token for team admin
    body = {"username": team_admin_email, "password": team_admin_password}
    operation = authentication_schema.get_operation_by_id('getAccountTokenfromUsername')
    case: Case = operation.make_case(body=body)
    response = case.call()

    assert response.status_code == 200

    account_token = response.json()['token']
    assert isinstance(account_token, str)

    yield TeamAdmin(team_id=team_id, account_token=account_token)

    if CLEANUP_AFTER_TESTS == 'True':
        path_parameters = {'org_id': team_id}
        case: Case = system_admin_account_operations.get_operation_by_id('deleteTeam').make_case(path_parameters=path_parameters)
        response = case.call(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})

@pytest.fixture
def team_name(system_admin_account_token: Secret) -> Generator[str, None, None]:
    team_name = f'automated-testing-org-{randint(1, 10000)}'

    yield team_name

    if CLEANUP_AFTER_TESTS == 'True':
        # Remove team to not cause issues on future test runs
        case: Case = system_admin_account_operations.get_operation_by_id('listTeams').make_case()
        response = case.call(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})
        data = response.json()

        assert response.status_code == 200

        # Find the organization we want to delete
        org_id = next((team['org_id'] for team in data['organizations'] if team['org_name'] == team_name), None)
        assert isinstance(org_id, int)

        path_parameters = {'org_id': org_id}
        case: Case = system_admin_account_operations.get_operation_by_id('deleteTeam').make_case(path_parameters=path_parameters)
        response = case.call(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})

def generate_password() -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(20))

def create_group(account_token: Secret, group_name: str) -> tuple[int, int]:
    """Creates a group and returns (group_id, workspace_id)"""
    body = {'name': group_name}
    headers = {'Authorization': f'Bearer {account_token.value}'}
    case: Case = user_account_operations.get_operation_by_id('createGroup') \
        .make_case(body=body)
    response = case.call(headers=headers)
    assert response.status_code == 201

    group_id = response.json()['id']
    assert isinstance(group_id, int)

    # TODO: Is there an easier way to get the workspace ID of a group?

    # TODO: Fix bug with query
    query = {'detail': False}
    case: Case = user_account_operations.get_operation_by_id('listWorkspaces') \
        .make_case()
    response = case.call(headers=headers)

    assert response.status_code == 200

    workspaces = response.json()['workspace_list']
    workspace_id = next((w['id'] for w in workspaces if w.get('group_id', None) == group_id), None)
    assert isinstance(workspace_id, int)

    return (group_id, workspace_id)

def delete_group(account_token: Secret, group_id: int):

    if CLEANUP_AFTER_TESTS == 'True':
        path_parameters = {'group_id': group_id}
        headers = {'Authorization': f'Bearer {account_token.value}'}
        case: Case = user_account_operations.get_operation_by_id('deleteGroup') \
            .make_case(path_parameters=path_parameters)
        response = case.call(headers=headers)

        assert response.status_code == 200
