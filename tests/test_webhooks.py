from conftest import Base, Secret, user_account_operations
from schemathesis import Case


def test_webhook_lifecycle(base: Base, account_token: Secret):
    """Tests createWebhook, listWebhooks, updateWebhook, deleteWebhook."""
    path_parameters = {'workspace_id': base.workspace_id, 'base_name': 'Automated Tests'}
    headers = {'Authorization': f'Bearer {account_token.value}'}

    # 1. Create webhook
    body = {'url': 'https://example.com/webhook'}
    case: Case = user_account_operations.find_operation_by_id('createWebhook') \
        .Case(path_parameters=path_parameters, body=body)
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert 'webhook' in data
    webhook_id = data['webhook']['id']
    assert data['webhook']['url'] == 'https://example.com/webhook'

    # 2. List webhooks
    case: Case = user_account_operations.find_operation_by_id('listWebhooks') \
        .Case(path_parameters=path_parameters)
    response = case.call(headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert 'webhook_list' in data
    webhook_ids = [w['id'] for w in data['webhook_list']]
    assert webhook_id in webhook_ids

    # 3. Update webhook
    path_params_with_id = {**path_parameters, 'webhook_id': webhook_id}
    body = {'url': 'https://example.com/webhook-updated'}
    case: Case = user_account_operations.find_operation_by_id('updateWebhook') \
        .Case(path_parameters=path_params_with_id, body=body)
    response = case.call(headers=headers)

    assert response.status_code == 200
    assert response.json()['webhook']['url'] == 'https://example.com/webhook-updated'

    # 4. Delete webhook
    case: Case = user_account_operations.find_operation_by_id('deleteWebhook') \
        .Case(path_parameters=path_params_with_id)
    response = case.call(headers=headers)

    assert response.status_code == 200
    assert response.json()['success'] is True

    # Verify it's gone
    case: Case = user_account_operations.find_operation_by_id('listWebhooks') \
        .Case(path_parameters=path_parameters)
    response = case.call(headers=headers)

    assert response.status_code == 200
    webhook_ids = [w['id'] for w in response.json()['webhook_list']]
    assert webhook_id not in webhook_ids
