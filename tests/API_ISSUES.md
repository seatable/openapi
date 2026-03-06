# API Issues and Inconsistencies

Issues discovered during automated testing against SeaTable 6.0.10. These are candidates for API improvements in future versions.

## Missing Operations

### No createRowComment endpoint
There is no API endpoint to create a row comment. The `create_row_comment` schema exists in `base_operations.yaml` but no POST operation is defined on `/api-gateway/api/v2/dtables/{base_uuid}/comments/` (returns 405 Method Not Allowed). The dtable-server path `/dtable-server/api/v1/dtables/{uuid}/comments/` also returns 400 regardless of parameters.

**Impact:** Comments cannot be created via API, only listed, read, and deleted. This makes it impossible to fully test comment operations.

**Status:** Will be re-added in 6.1.

## Missing or Incorrect Spec Definitions

### deleteUserShare missing requestBody
The `deleteUserShare` operation in `user_account_operations.yaml` had no `requestBody` defined, but the API requires `email` as form data in the request body.

**Fixed in:** This repository (commit 188837f).

## Inconsistent Response Status Codes

### createWebhook returns 200 instead of 201
`POST /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/webhooks/` returns HTTP 200 on success. Creating a resource should return 201 Created per REST conventions.

### createGroupShare returns 200 instead of 201
`POST /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/group-shares/` returns HTTP 200 on success. Should return 201 Created.

### createUserShare returns 201 (correct)
For comparison, `createUserShare` correctly returns 201. The behavior should be consistent across all share/create endpoints.

## Inconsistent Data Types

### group_id returned as string in createGroupShare response
`POST /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/group-shares/` returns `group_id` as a string (e.g., `"44"`) in the response, even though it is sent as a string and represented as an integer everywhere else (e.g., in `listGroupShares` and path parameters).

The `group_id` should consistently be returned as an integer.

## License Limitations Affecting Testing

### addNewUser returns 403 when user limit is reached
`POST /api/v2.1/admin/users/` returns `403 {"error_msg": "The number of users exceeds the limit."}` instead of a more specific status code (e.g., 402 Payment Required or 409 Conflict). A 403 typically means insufficient permissions, which is misleading here.

## Naming Inconsistencies

### listColumns excludes auto-created Name column
`GET /api-gateway/api/v2/dtables/{base_uuid}/columns/` only returns explicitly created columns when a table was created with a columns array via `createTable`. The auto-created default `Name` column is not included in the response if custom columns were specified during table creation.

This is not necessarily a bug, but the behavior may be unexpected.
