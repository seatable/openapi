import pytest
from conftest import Base, Secret, user_account_operations
from schemathesis import Case


BASE_NAME = 'Automated Tests'


def _headers(account_token: Secret) -> dict:
    return {'Authorization': f'Bearer {account_token.value}'}


def test_getBaseActivities(base: Base, account_token: Secret):
    case: Case = user_account_operations.find_operation_by_id('getBaseActivities') \
        .Case(query={'page': 1, 'per_page': 25})
    response = case.call(headers=_headers(account_token))

    assert response.status_code == 200
    data = response.json()
    assert 'table_activities' in data


def test_listAutomationRules(base: Base, account_token: Secret):
    case: Case = user_account_operations.find_operation_by_id('listAutomationRules') \
        .Case(
            path_parameters={'workspace_id': base.workspace_id, 'base_name': BASE_NAME},
        )
    response = case.call(headers=_headers(account_token))

    assert response.status_code == 200
    data = response.json()
    assert 'dtable_automation_rule_list' in data


def test_listMyGroupShares(account_token: Secret):
    case: Case = user_account_operations.find_operation_by_id('listMyGroupShares') \
        .Case()
    response = case.call(headers=_headers(account_token))

    assert response.status_code == 200
    data = response.json()
    assert 'group_shared_dtables' in data


def test_listCollaboratorsAsUser(base: Base, account_token: Secret):
    case: Case = user_account_operations.find_operation_by_id('listCollaboratorsAsUser') \
        .Case(
            path_parameters={'workspace_id': base.workspace_id, 'base_name': BASE_NAME},
        )
    response = case.call(headers=_headers(account_token))

    assert response.status_code == 200
    data = response.json()
    assert 'user_list' in data


def test_listUserShares(base: Base, account_token: Secret):
    case: Case = user_account_operations.find_operation_by_id('listUserShares') \
        .Case(
            path_parameters={'workspace_id': base.workspace_id, 'base_name': BASE_NAME},
        )
    response = case.call(headers=_headers(account_token))

    assert response.status_code == 200
    data = response.json()
    assert 'user_list' in data


def test_markNotificationAsSeen(account_token: Secret):
    case: Case = user_account_operations.find_operation_by_id('markNotificationAsSeen') \
        .Case()
    response = case.call(headers=_headers(account_token))

    assert response.status_code == 200
