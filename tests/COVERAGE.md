# API Test Coverage Report

Generated: 2026-03-06

**Total API Endpoints Defined:** 419 across 8 OpenAPI spec files
**Total Endpoints Currently Tested:** 24 (5.7%)

## Coverage by Spec

| Spec File | Total | Tested | Coverage |
|-----------|-------|--------|----------|
| authentication.yaml | 9 | 3 | 33% |
| user_account_operations.yaml | 158 | 11 | 7% |
| base_operations.yaml | 52 | 7 | 13% |
| system_admin_account_operations.yaml | 97 | 2 | 2% |
| team_admin_account_operations.yaml | 66 | 1 | 2% |
| file_operations.yaml | 9 | 2 | 22% |
| ping_and_info.yaml | 6 | 0 | 0% |
| python-scheduler.yaml | 6 | 0 | 0% |

## Tested Endpoints

### Authentication (3/9)

- `POST /api2/auth-token/` — getAccountTokenfromUsername
- `GET /api/v2.1/dtable/app-access-token/` — getBaseTokenWithApiToken
- `GET /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/access-token/` — getBaseTokenWithAccountToken

### User Account Operations (11/158)

- createBase, deleteBase, createGroup, deleteGroup, listWorkspaces
- Plus fixtures for setup/teardown

### Base Operations (7/52)

- createTable, appendRows, getRow, listRows, querySQL, insertColumn, createRowLink

### System Admin (2/97)

- getAccountTokenfromUsername (via auth), addTeam (fixture)

### Team Admin (1/66)

- addTeam (fixture)

### File Operations (2/9)

- getUploadLink, uploadFile

### Ping and Info (0/6)

No tests.

### Python Scheduler (0/6)

No tests.

## Not Tested (Selection)

### Authentication (6 missing)

- listApiTokens, createApiToken, createTempApiToken, updateApiToken, deleteApiToken
- getBaseTokenWithExternLink

### User Account Operations (147 missing)

- Account info (getAccountInfo, updateEmailAddress, addUserAvatar)
- User/public info (getPublicUserInfo, listPublicUserInfos, searchUser)
- Base operations (updateBase, listFavorites, favoriteBase/unfavoriteBase)
- Folder management (createFolder, updateFolder, deleteFolder)
- Base passwords, trash recovery
- Group members (getGroupMembers, addGroupMember, updateGroupRole)
- Sharing (listMyShares, createUserShare, updateUserShare, deleteUserShare)
- External links (listBaseExternalLinks, createBaseExternalLink)
- Common datasets (listCommonDataset, publishCommonDataset, importCommonDataset)
- Forms (listForms, createForm, updateForm, deleteForm)
- Automation rules (listAutomationRules, createAutomationRule, updateAutomationRule)
- Notification rules (listNotificationRules, addNotificationRule)
- Webhooks (listWebhooks, createWebhook, updateWebhook, deleteWebhook)
- Snapshots and activities

### Base Operations (45 missing)

- Row management (updateRow, deleteRow, lockRows, unlockRows)
- Links (listRowLinks, updateRowLink, deleteRowLink, autoLinks)
- Tables (renameTable, deleteTable, duplicateTable)
- Views (listViews, createView, getView, updateView, deleteView)
- Columns (listColumns, updateColumn, deleteColumn, appendColumns)
- Select options (addSelectOption, updateSelectOption, deleteSelectOption)
- Big data operations (moveRowsToBigData, moveRowsToNormalBackend)
- Comments (listRowComments, getComment, deleteComment)
- Notifications (listBaseNotifications, markBaseNotificationsAsSeen)
- Activities (getBaseActivityLog, listRowActivities, createSnapshot)

### System Admin (95 missing)

- User management (listUsers, addNewUser, getUser, updateUser, deleteUser)
- Group management (listGroups, createGroup, transferGroup, deleteGroup)
- Team management (listTeams, searchTeam, updateTeam, deleteTeam)
- Base admin (listAllBases, deleteBase, restoreTrashedBase)
- Audit & logging (listLoginLogs, listAuditLogs)
- Statistics (getActiveUsersPerDay, getAutomationRules)
- System configuration (getSystemInformation, updateGeneralSettings)

### Team Admin (65 missing)

- Team user management (listTeamUsers, addUser, getUser, updateUser, deleteUser)
- Team base management (listBases, getBase, deleteBase)
- Team group management (listGroups, addGroup, updateGroup)
- Team sharing and external links
- Team settings, logs, and statistics

## Prioritization

### High Priority

1. Ping endpoints (quick wins, 6 endpoints)
2. Row CRUD (updateRow, deleteRow) — core functionality
3. View and column management — frequently used
4. User/group management (system admin) — critical for admin API
5. Sharing and permissions

### Medium Priority

1. Automation rules and webhooks
2. Snapshots and activities
3. Common datasets
4. Forms
5. External links

### Low Priority

1. Big data operations
2. SAML/team settings
3. Python scheduler
4. Audit logs
5. System configuration
