# API Test Coverage Report

Generated: 2026-03-20

**Total API Endpoints Defined:** 343 across 8 OpenAPI spec files
**Total Endpoints Tested:** 100 (29%)

## Coverage by Spec

| Spec File | Total | Tested | Coverage |
|-----------|-------|--------|----------|
| authentication.yaml | 7 | 7 | 100% |
| base_operations.yaml | 52 | 44 | 84% |
| user_account_operations.yaml | 117 | 18 | 15% |
| team_admin_account_operations.yaml | 48 | 4 | 8% |
| system_admin_account_operations.yaml | 98 | 18 | 18% |
| file_operations.yaml | 9 | 3 | 33% |
| ping_and_info.yaml | 6 | 6 | 100% |
| python-scheduler.yaml | 6 | 0 | 0% |

## Authentication (7/7)

### API-Token (3/3)

- [x] `POST /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/api-tokens/` - createApiToken
- [x] `GET /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/temp-api-token/` - createTempApiToken
- [x] `PUT /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/api-tokens/{app_name}/` - updateApiToken

### Account-Token (1/1)

- [x] `POST /api2/auth-token/` - getAccountTokenfromUsername

### Base-Token (3/3)

- [x] `GET /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/access-token/` - getBaseTokenWithAccountToken
- [x] `GET /api/v2.1/dtable/app-access-token/` - getBaseTokenWithApiToken
- [x] `GET /api/v2.1/external-link-tokens/{external_link_token}/access-token/` - getBaseTokenWithExternLink

## Base Operations (31/52)

### Big Data (0/5)

- [ ] `POST /api-gateway/api/v2/dtables/{base_uuid}/add-archived-rows/` - addBigDataRows
- [ ] `GET /api-gateway/api/v2/dtables/{base_uuid}/db-operations/` - getBaseBigDataOperations
- [ ] `POST /api-gateway/api/v2/dtables/{base_uuid}/archive-view/` - moveRowsToBigData
- [ ] `POST /api-gateway/api/v2/dtables/{base_uuid}/unarchive/` - moveRowsToNormalBackend
- [ ] `PUT /api-gateway/api/v2/dtables/{base_uuid}/restore-operations/{op_id}/` - restoreBigDataOperations

### Columns (8/9)

- [x] `POST /api-gateway/api/v2/dtables/{base_uuid}/column-options/` - addSelectOption
- [x] `POST /api-gateway/api/v2/dtables/{base_uuid}/batch-append-columns/` - appendColumns
- [x] `DELETE /api-gateway/api/v2/dtables/{base_uuid}/columns/` - deleteColumn
- [x] `DELETE /api-gateway/api/v2/dtables/{base_uuid}/column-options/` - deleteSelectOption
- [x] `POST /api-gateway/api/v2/dtables/{base_uuid}/columns/` - insertColumn
- [x] `GET /api-gateway/api/v2/dtables/{base_uuid}/columns/` - listColumns
- [x] `PUT /api-gateway/api/v2/dtables/{base_uuid}/columns/` - updateColumn
- [x] `PUT /api-gateway/api/v2/dtables/{base_uuid}/column-options/` - updateSelectOption
- [ ] `POST /api-gateway/api/v2/dtables/{base_uuid}/column-cascade-settings/` - updateColumnCascade

### Rows (8/8)

- [x] `POST /api-gateway/api/v2/dtables/{base_uuid}/rows/` - appendRows
- [x] `DELETE /api-gateway/api/v2/dtables/{base_uuid}/rows/` - deleteRow
- [x] `GET /api-gateway/api/v2/dtables/{base_uuid}/rows/{row_id}/` - getRow
- [x] `GET /api-gateway/api/v2/dtables/{base_uuid}/rows/` - listRows
- [x] `PUT /api-gateway/api/v2/dtables/{base_uuid}/lock-rows/` - lockRows
- [x] `POST /api-gateway/api/v2/dtables/{base_uuid}/sql/` - querySQL
- [x] `PUT /api-gateway/api/v2/dtables/{base_uuid}/unlock-rows/` - unlockRows
- [x] `PUT /api-gateway/api/v2/dtables/{base_uuid}/rows/` - updateRow

### Links (4/6)

- [x] `POST /api-gateway/api/v2/dtables/{base_uuid}/links/` - createRowLink
- [x] `DELETE /api-gateway/api/v2/dtables/{base_uuid}/links/` - deleteRowLink
- [x] `POST /api-gateway/api/v2/dtables/{base_uuid}/query-links/` - listRowLinks
- [x] `PUT /api-gateway/api/v2/dtables/{base_uuid}/links/` - updateRowLink
- [ ] `GET /api-gateway/api/v2/dtables/{base_uuid}/auto-link-task/` - autoLinkTask
- [ ] `POST /api-gateway/api/v2/dtables/{base_uuid}/auto-links/` - autoLinks

### Snapshots (1/1)

- [x] `POST /api-gateway/api/v2/dtables/{base_uuid}/snapshot/` - createSnapshot

### Tables (4/4)

- [x] `POST /api-gateway/api/v2/dtables/{base_uuid}/tables/` - createTable
- [x] `DELETE /api-gateway/api/v2/dtables/{base_uuid}/tables/` - deleteTable
- [x] `POST /api-gateway/api/v2/dtables/{base_uuid}/tables/duplicate-table/` - duplicateTable
- [x] `PUT /api-gateway/api/v2/dtables/{base_uuid}/tables/` - renameTable

### Views (5/5)

- [x] `POST /api-gateway/api/v2/dtables/{base_uuid}/views/` - createView
- [x] `DELETE /api-gateway/api/v2/dtables/{base_uuid}/views/{view_name}/` - deleteView
- [x] `GET /api-gateway/api/v2/dtables/{base_uuid}/views/{view_name}/` - getView
- [x] `GET /api-gateway/api/v2/dtables/{base_uuid}/views/` - listViews
- [x] `PUT /api-gateway/api/v2/dtables/{base_uuid}/views/{view_name}/` - updateView

### Notifications (4/4)

- [x] `DELETE /api-gateway/api/v2/dtables/{base_uuid}/notifications/` - deleteBaseNotifications
- [x] `PUT /api-gateway/api/v2/dtables/{base_uuid}/notifications/{notification_id}/` - markBaseNotificationAsSeen
- [x] `PUT /api-gateway/api/v2/dtables/{base_uuid}/notifications/` - markBaseNotificationsAsSeen
- [x] `POST /api-gateway/api/v2/dtables/{base_uuid}/ui-toasts/` - sendToastNotification

### Row Comments (6/6)

- [x] `DELETE /api-gateway/api/v2/dtables/{base_uuid}/comments/{comment_id}/` - deleteComment
- [x] `GET /api-gateway/api/v2/dtables/{base_uuid}/comments/{comment_id}/` - getComment
- [x] `GET /api/v2.1/dtables/{base_uuid}/rows-comments-num/` - getNumberOfComments
- [x] `GET /api-gateway/api/v2/dtables/{base_uuid}/comments-count/` - getRowCommentsCount
- [x] `GET /api-gateway/api/v2/dtables/{base_uuid}/comments-within-days/` - listCommentsWithinDays
- [x] `GET /api-gateway/api/v2/dtables/{base_uuid}/comments/` - listRowComments

### Activities & Logs (2/2)

- [x] `GET /api-gateway/api/v2/dtables/{base_uuid}/operations/` - getBaseActivityLog
- [x] `GET /api-gateway/api/v2/dtables/{base_uuid}/activities/` - listRowActivities

### Base Info (2/2)

- [x] `GET /api-gateway/api/v2/dtables/{base_uuid}/metadata/` - getMetadata
- [x] `GET /api-gateway/api/v2/dtables/{base_uuid}/related-users/` - listCollaborators

## User Account Operations (18/117)

### Email Accounts (0/6)

- [ ] `POST /api/v2.1/third-party-accounts/{base_uuid}/` - addEmailAccount
- [ ] `DELETE /api/v2.1/third-party-accounts/{base_uuid}/{3rd_party_account_id}/` - deleteEmailAccount
- [ ] `GET /api/v2.1/third-party-accounts/{base_uuid}/detail/` - getEmailAccount
- [ ] `GET /api/v2.1/dtable-message-status/` - getEmailSendingStatus
- [ ] `GET /api/v2.1/third-party-accounts/{base_uuid}/` - listEmailAccounts
- [ ] `PUT /api/v2.1/third-party-accounts/{base_uuid}/{3rd_party_account_id}/` - updateEmailAccount

### Groups & Workspaces (1/9)

- [x] `GET /api/v2.1/workspaces/` - listWorkspaces
- [ ] `POST /api/v2.1/groups/{group_id}/members/` - addGroupMember
- [ ] `POST /api/v2.1/dtable-external-link/dtable-copy/` - copyBaseFromExternalLink
- [ ] `POST /api/v2.1/dtable-copy/` - copyBaseFromWorkspace
- [ ] `GET /api/v2.1/groups/{group_id}/members/` - getGroupMembers
- [ ] `DELETE /api/v2.1/groups/{group_id}/members/{group_member}/` - removeGroupMember
- [ ] `GET /api/v2.1/search-group/` - searchGroup
- [ ] `GET /api/v2.1/groups/{group_id}/search-member/` - searchGroupMembers
- [ ] `PUT /api/v2.1/groups/{group_id}/members/{group_member}/` - updateGroupRole

### Notifications (0/3)

- [ ] `POST /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/notification-rules/` - addNotificationRule
- [ ] `DELETE /api/v2.1/notifications/` - markNotificationAsSeen
- [ ] `PUT /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/notification-rules/{notification_rule_id}/` - updateNotificationRule

### User (1/5)

- [x] `GET /api2/account/info/` - getAccountInfo
- [ ] `POST /api/v2.1/user-avatar/` - addUserAvatar
- [ ] `GET /api/v2.1/user-common-info/{user_id}/` - getPublicUserInfo
- [ ] `POST /api/v2.1/user-list/` - listPublicUserInfos
- [ ] `PUT /api/v2.1/user/contact-email/` - updateEmailAddress

### Import & Export (0/9)

- [ ] `POST /api/v2.1/workspace/{workspace_id}/synchronous-import/append-excel-csv-to-table/` - appendToTableFromFile
- [ ] `GET /dtable/external-links/{external_link_token}/download-zip/` - exportBaseFromExternalLink
- [ ] `GET /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/convert-big-data-view-to-excel/` - exportBigDataView
- [ ] `GET /api/v2.1/workspace/{workspace_id}/synchronous-export/export-table-to-excel/` - exportTable
- [ ] `GET /api/v2.1/workspace/{workspace_id}/synchronous-export/export-view-to-excel/` - exportView
- [ ] `POST /api/v2.1/workspace/{workspace_id}/import-dtable/` - importBasefromDTableFile
- [ ] `POST /api/v2.1/workspace/{workspace_id}/synchronous-import/import-excel-csv-to-base/` - importBasefromFile
- [ ] `POST /api/v2.1/workspace/{workspace_id}/synchronous-import/import-excel-csv-to-table/` - importTableFromFile
- [ ] `POST /api/v2.1/workspace/{workspace_id}/synchronous-import/update-table-via-excel-csv/` - updateFromFile

### Bases (4/15)

- [x] `POST /api/v2.1/dtables/` - createBase
- [x] `POST /api/v2.1/starred-dtables/` - favoriteBase
- [x] `GET /api/v2.1/starred-dtables/` - listFavorites
- [x] `DELETE /api/v2.1/starred-dtables/` - unfavoriteBase
- [ ] `PUT /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/password/` - basePassword
- [ ] `DELETE /api/v2.1/trash-dtables/` - clearTrash
- [ ] `POST /api/v2.1/workspace/{workspace_id}/folders/` - createFolder
- [ ] `DELETE /api/v2.1/workspace/{workspace_id}/folders/{folder_id}/` - deleteFolder
- [ ] `GET /api/v2.1/dtable/{base_uuid}/size/` - getBaseSize
- [ ] `GET /api/v2.1/groups/{group_id}/trash-dtables/` - listGroupTrashedBases
- [ ] `POST /api/v2.1/workspace/{workspace_id}/folder-item-moving/` - moveBaseIntoFolder
- [ ] `PUT /api/v2.1/groups/{group_id}/trash-dtables/{base_uuid}/` - restoreGroupTrashedBase
- [ ] `GET /api/v2.1/dtable/items-search/` - searchBaseOrApps
- [ ] `PUT /api/v2.1/workspace/{workspace_id}/dtable/` - updateBase
- [ ] `PUT /api/v2.1/workspace/{workspace_id}/folders/{folder_id}/` - updateFolder

### Apps (0/5)

- [ ] `PUT /api/v2.1/external-apps/{app_token}/status/` - changeAppStatus
- [ ] `POST /api/v2.1/universal-apps/{app_token}/app-users/batch/` - importUsersToApp
- [ ] `GET /api/v2.1/universal-apps/{app_token}/invite-links/` - listAppInviteLinks
- [ ] `GET /api/v2.1/universal-apps/` - listApps
- [ ] `GET /api/v2.1/universal-apps/{app_token}/app-users/` - listUniversalAppUsers

### Attachment (0/6)

- [ ] `GET /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/asset-exists/` - checkIfAssetExists
- [ ] `DELETE /api/v2.1/dtable-asset/{base_uuid}/batch-delete-assets/` - deleteBaseAssets
- [ ] `GET /api/v2.1/workspace/{workspace_id}/dtable-asset-upload-link/` - getBaseAttachmentUploadLink
- [ ] `GET /api/v2.1/dtable-asset/{base_uuid}/` - listBaseAssets
- [ ] `GET /api/v2.1/dtable-recent-asset/{base_uuid}/` - listRecentlyUploadedFiles
- [ ] `POST /api/v2.1/dtable-asset/{base_uuid}/rename/` - renameBaseAsset

### Automations (0/4)

- [ ] `POST /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/automation-rules/` - createAutomationRule
- [ ] `DELETE /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/automation-rules/{automation_rule_id}/` - deleteAutomationRule
- [ ] `GET /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/automation-rules/` - listAutomationRules
- [ ] `PUT /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/automation-rules/{automation_rule_id}/` - updateAutomationRule

### Sharing Links (0/3)

- [ ] `POST /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/external-links/` - createBaseExternalLink
- [ ] `POST /api/v2.1/dtables/invite-links/` - createInviteLink
- [ ] `POST /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/view-external-links/` - createViewExternalLink

### Forms (0/5)

- [ ] `POST /api/v2.1/forms/` - createForm
- [ ] `POST /api/v2.1/forms/{form_token}/duplicate/` - duplicateForm
- [ ] `GET /api/v2.1/forms/shared/` - listSharedForms
- [ ] `PUT /api/v2.1/forms/{form_token}/` - updateForm
- [ ] `POST /api/v2.1/forms/{form_token}/logos/` - uploadFormLogo

### Sharing (8/24)

- [x] `POST /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/group-shares/` - createGroupShare
- [x] `POST /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/share/` - createUserShare
- [x] `DELETE /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/group-shares/{group_id}/` - deleteGroupShare
- [x] `DELETE /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/share/` - deleteUserShare
- [x] `GET /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/group-shares/` - listGroupShares
- [x] `GET /api/v2.1/dtables/shared/` - listMyShares
- [x] `PUT /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/group-shares/{group_id}/` - updateGroupShare
- [x] `PUT /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/share/` - updateUserShare
- [ ] `POST /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/group-view-shares/` - createGroupViewShare
- [ ] `POST /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/user-view-shares/` - createUserViewShare
- [ ] `DELETE /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/group-view-shares/` - deleteGroupAllViewShare
- [ ] `DELETE /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/group-view-shares/{group_view_share_id}/` - deleteGroupViewShare
- [ ] `DELETE /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/user-view-shares/` - deleteUserAllViewShare
- [ ] `DELETE /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/user-view-shares/{user_view_share_id}/` - deleteUserViewShare
- [ ] `DELETE /api/v2.1/dtables/view-shares-user-shared/{user_view_share_id}/` - leaveSharedView
- [ ] `GET /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/related-users/` - listCollaboratorsAsUser
- [ ] `GET /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/group-view-shares/` - listGroupViewShares
- [ ] `GET /api/v2.1/dtables/group-shared/` - listMyGroupShares
- [ ] `GET /api/v2.1/dtables/view-shares-group-shared/` - listMyGroupViewShares
- [ ] `GET /api/v2.1/dtables/view-shares-user-shared/` - listMyUserViewShares
- [ ] `GET /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/share/` - listUserShares
- [ ] `GET /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/user-view-shares/` - listUserViewShares
- [ ] `PUT /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/group-view-shares/{group_view_share_id}/` - updateGroupViewShare
- [ ] `PUT /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/user-view-shares/{user_view_share_id}/` - updateUserViewShare

### Webhooks (4/4)

- [x] `POST /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/webhooks/` - createWebhook
- [x] `DELETE /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/webhooks/{webhook_id}/` - deleteWebhook
- [x] `GET /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/webhooks/` - listWebhooks
- [x] `PUT /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/webhooks/{webhook_id}/` - updateWebhook

### Common Dataset (0/9)

- [ ] `DELETE /api/v2.1/dtable/common-datasets/{dataset_id}/` - deleteCommonDataset
- [ ] `GET /api/v2.1/dtable/common-datasets/{dataset_id}/` - getCommonDataset
- [ ] `GET /api/v2.1/dtable/common-datasets/{dataset_id}/info/` - getCommonDatasetInfo
- [ ] `POST /api/v2.1/dtable/common-datasets/{dataset_id}/import/` - importCommonDataset
- [ ] `GET /api/v2.1/dtable/common-datasets/syncs/` - listSyncHistory
- [ ] `POST /api/v2.1/dtable/common-datasets/` - publishCommonDataset
- [ ] `PUT /api/v2.1/dtable/common-datasets/{dataset_id}/` - renameCommonDataset
- [ ] `POST /api/v2.1/dtable/common-datasets/{dataset_id}/sync/` - syncCommonDataset
- [ ] `PUT /api/v2.1/dtable/common-datasets/{dataset_id}/sync/` - updateCommonDatasetSync

### Activities & Logs (0/3)

- [ ] `GET /api/v2.1/dtable-activities/` - getBaseActivities
- [ ] `GET /api/v2.1/dtable-activities/detail/` - getBaseActivityDetails
- [ ] `GET /api/v2.1/dtables/{base_uuid}/big-data-operation-logs/` - getBigDataOperationLogs

### Snapshots (0/4)

- [ ] `GET /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/big-data-state/` - getBigDataStatus
- [ ] `GET /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/archive-backups/` - listBigDataBackups
- [ ] `GET /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/snapshots/` - listSnapshots
- [ ] `POST /api/v2.1/workspace/{workspace_id}/dtable/{base_name}/snapshots/{commit_id}/restore/` - restoreSnapshot

### Departments (0/1)

- [ ] `GET /api/v2.1/address-book/departments/{department_id}/members/` - listDeparmentMembers

### System Notifications (0/2)

- [ ] `GET /api/v2.1/sys-user-notifications/unseen/` - listSystemNotifications
- [ ] `PUT /api/v2.1/sys-user-notifications/{sys_notification_id}/seen/` - markSystemNotificationsAsSeen

## Team Admin Account Operations (4/48)

### Groups (1/9)

- [x] `PUT /api/v2.1/org/{org_id}/admin/groups/{group_id}/` - updateGroup
- [ ] `POST /api/v2.1/org/{org_id}/admin/groups/` - addGroup
- [ ] `POST /api/v2.1/org/{org_id}/admin/groups/{group_id}/members/` - addGroupMembers
- [ ] `GET /api/v2.1/org/{org_id}/admin/groups/{group_id}/` - getGroup
- [ ] `GET /api/v2.1/org/{org_id}/admin/groups/{group_id}/dtables/` - listGroupBases
- [ ] `GET /api/v2.1/org/{org_id}/admin/groups/{group_id}/members/` - listGroupMembers
- [ ] `PUT /api/v2.1/groups/move-group/` - orderGroups
- [ ] `DELETE /api/v2.1/org/{org_id}/admin/groups/{group_id}/members/{user_id}/` - removeGroupMembers
- [ ] `PUT /api/v2.1/org/{org_id}/admin/groups/{group_id}/members/{user_id}/` - updateGroupMemberRole

### Users (0/2)

- [ ] `POST /api/v2.1/org/{org_id}/admin/users/` - addUser
- [ ] `PUT /api/v2.1/org/{org_id}/admin/users/{user_id}/two-factor-auth/` - enforceTwofactor

### Bases (3/10)

- [x] `DELETE /api/v2.1/org/{org_id}/admin/dtables/{base_uuid}/api-tokens/{app_name}/` - deleteApiToken
- [x] `GET /api/v2.1/org/{org_id}/admin/dtables/{base_uuid}/` - getBase
- [x] `GET /api/v2.1/org/{org_id}/admin/dtables/{base_uuid}/api-tokens/` - listApiTokens
- [ ] `DELETE /api/v2.1/org/{org_id}/admin/trash-dtables/` - clearTeamTrashBin
- [ ] `GET /api/v2.1/org/{org_id}/admin/api-tokens/` - listApiTokensOfAllBases
- [ ] `GET /api/v2.1/org/{org_id}/admin/dtables/{base_uuid}/shares/` - listBaseSharings
- [ ] `GET /api/v2.1/org/{org_id}/admin/dtables/` - listBases
- [ ] `GET /api/v2.1/org/{org_id}/admin/trash-dtables/` - listTrashBases
- [ ] `PUT /api/v2.1/org/{org_id}/admin/trash-dtables/{base_uuid}/` - restoreBaseFromTrash
- [ ] `GET /api/v2.1/org/{org_id}/admin/search-dtables/` - searchBase

### Sharing Links (0/5)

- [ ] `DELETE /api/v2.1/org/{org_id}/admin/external-links/{external_link_token}/` - deleteExternalLink
- [ ] `DELETE /api/v2.1/org/{org_id}/admin/invite-links/{invite_link_token}/` - deleteInviteLink
- [ ] `GET /api/v2.1/org/{org_id}/admin/invite-links/` - listInviteLinks
- [ ] `GET /api/v2.1/org/{org_id}/admin/shares/` - listShares
- [ ] `PUT /api/v2.1/org/{org_id}/admin/invite-links/{invite_link_token}/` - updateInviteLink

### SAML (0/4)

- [ ] `DELETE /api/v2.1/org/{org_id}/admin/saml-config/` - deleteSamlConfig
- [ ] `GET /api/v2.1/org/{org_id}/admin/saml-config/` - getSamlConfig
- [ ] `PUT /api/v2.1/org/{org_id}/admin/saml-config/` - updateSamlConfig
- [ ] `PUT /api/v2.1/org/{org_id}/admin/verify-domain/` - verifySamlDomain

### Customizing (0/3)

- [ ] `DELETE /api/v2.1/org/{org_id}/admin/org-logo/` - deleteTeamLogo
- [ ] `GET /api/v2.1/org/{org_id}/admin/org-logo/` - getTeamLogo
- [ ] `POST /api/v2.1/org/{org_id}/admin/org-logo/` - updateTeamLogo

### Statistics (0/7)

- [ ] `GET /api/v2.1/org/{org_id}/admin/statistics/admin-logs/by-day/` - getAdminLogStatisticsByDay
- [ ] `GET /api/v2.1/org/{org_id}/admin/statistics/automation-logs/by-base/` - getAutomationLogStatisticsByBase
- [ ] `GET /api/v2.1/org/{org_id}/admin/statistics/automation-logs/by-day/` - getAutomationLogStatisticsByDay
- [ ] `GET /api/v2.1/org/{org_id}/admin/statistics/login-logs/by-day/` - getLoginLogStatisticsByDay
- [ ] `GET /api/v2.1/org/{org_id}/admin/statistics/python-runs/by-base/` - getPythonRunStatisticsByBase
- [ ] `GET /api/v2.1/org/{org_id}/admin/statistics/python-runs/by-day/` - getPythonRunStatisticsByDay
- [ ] `GET /api/v2.1/org/{org_id}/admin/statistics/ai/` - getUserOrBaseAIStatistics

### Info & Settings (0/3)

- [ ] `GET /api/v2.1/org/admin/info/` - getTeamInfo
- [ ] `GET /api/v2.1/org/admin/settings/` - getTeamSettings
- [ ] `PUT /api/v2.1/org/admin/settings/` - updateTeamSettings

### Activities & Logs (0/5)

- [ ] `GET /api/v2.1/org/{org_id}/admin/automation-logs/` - listAutomationLogs
- [ ] `GET /api/v2.1/org/{org_id}/admin/python-runs/` - listPythonRuns
- [ ] `GET /api/v2.1/org/{org_id}/admin/login-logs/` - listTeamLogins
- [ ] `GET /api/v2.1/org/{org_id}/admin/admin-logs/` - listTeamOperationLog
- [ ] `GET /api/v2.1/org/{org_id}/admin/login-logs/{user_id}/` - listUserLogins

## System Admin Account Operations (18/98)

### Departments (0/4)

- [ ] `POST /api/v2.1/admin/address-book/groups/` - addDepartment
- [ ] `DELETE /api/v2.1/admin/address-book/groups/{department_id}/` - deleteDepartment
- [ ] `GET /api/v2.1/admin/address-book/groups/{department_id}/` - getDepartments
- [ ] `GET /api/v2.1/admin/address-book/groups/{parent_department_id}/` - listDepartments

### Users (8/15)

- [x] `POST /api/v2.1/admin/users/` - addNewUser
- [x] `DELETE /api/v2.1/admin/users/{user_id}/` - deleteUser
- [x] `GET /api/v2.1/admin/users/{user_id}/` - getUser
- [x] `GET /api/v2.1/admin/admin-users/` - listAdminUsers
- [x] `GET /api/v2.1/admin/users/` - listUsers
- [x] `PUT /api/v2.1/admin/users/{user_id}/reset-password/` - resetUserPassword
- [x] `GET /api/v2.1/admin/search-user/` - searchUser
- [x] `PUT /api/v2.1/admin/users/{user_id}/` - updateUser
- [ ] `DELETE /api2/two-factor-auth/{user_id}/` - disableTwoFactor
- [ ] `PUT /api/v2.1/admin/users/{user_id}/two-factor-auth/` - enforceTwoFactor
- [ ] `POST /api/v2.1/admin/import-users/` - importUsers
- [ ] `GET /api/v2.1/admin/users/{user_id}/shared-dtables/` - listBasesSharedToUser
- [ ] `GET /api/v2.1/admin/users/{user_id}/storage/` - listUserStorageObjects
- [ ] `GET /api/v2.1/admin/search-user-by-org-id/` - searchUserByOrgId
- [ ] `PUT /api/v2.1/admin/admin-role/` - updateAdminRole

### System Notifications (0/3)

- [ ] `POST /api/v2.1/admin/sys-user-notifications/` - addNotificationToUser
- [ ] `DELETE /api/v2.1/admin/sys-user-notifications/{sys_notification_id}/` - deleteNotification
- [ ] `GET /api/v2.1/admin/sys-user-notifications/` - listNotifications

### Plugins (0/5)

- [ ] `POST /api/v2.1/admin/dtable-system-plugins/` - addPlugin
- [ ] `DELETE /api/v2.1/admin/dtable-system-plugins/{plugin_id}/` - deletePlugin
- [ ] `GET /api/v2.1/admin/dtable-system-plugins/` - listPlugins
- [ ] `GET /api/v2.1/admin/plugins-install-count/` - listPluginsInstallCount
- [ ] `PUT /api/v2.1/admin/dtable-system-plugins/{plugin_id}/` - updatePlugin

### Teams (0/13)

- [ ] `POST /api/v2.1/admin/organizations/` - addTeam
- [ ] `POST /api/v2.1/admin/organizations/{org_id}/users/` - addTeamUser
- [ ] `DELETE /api/v2.1/admin/organizations/{org_id}/` - deleteTeam
- [ ] `DELETE /api/v2.1/admin/organizations/{org_id}/groups/{group_id}/` - deleteTeamGroup
- [ ] `DELETE /api/v2.1/admin/organizations/{org_id}/users/{user_id}/` - deleteTeamUser
- [ ] `GET /api/v2.1/admin/organizations-basic-info/` - getOrganizationNames
- [ ] `GET /api/v2.1/admin/organizations/{org_id}/dtables/` - listTeamBases
- [ ] `GET /api/v2.1/admin/organizations/{org_id}/groups/` - listTeamGroups
- [ ] `GET /api/v2.1/admin/organizations/{org_id}/users/` - listTeamUsers
- [ ] `GET /api/v2.1/admin/organizations/` - listTeams
- [ ] `GET /api/v2.1/admin/organizations/{org_id}/` - searchTeam
- [ ] `PUT /api/v2.1/admin/organizations/{org_id}/` - updateTeam
- [ ] `PUT /api/v2.1/admin/organizations/{org_id}/users/{user_id}/` - updateTeamUser

### Groups (4/4)

- [x] `POST /api/v2.1/admin/groups/` - createGroup
- [x] `DELETE /api/v2.1/admin/groups/{group_id}/` - deleteGroup
- [x] `GET /api/v2.1/admin/groups/` - listGroups
- [x] `PUT /api/v2.1/admin/groups/{group_id}/` - transferGroup

### Automations (0/4)

- [ ] `DELETE /api/v2.1/admin/automation-rules/{automation_rule_id}/` - deleteAutomation
- [ ] `DELETE /api/v2.1/admin/invalid-automation-rules/` - deleteInvalidAutomations
- [ ] `GET /api/v2.1/admin/automation-rules/` - listAutomations
- [ ] `GET /api/v2.1/admin/invalid-automation-rules/` - listInvalidAutomations

### Bases (5/7)

- [x] `DELETE /api/v2.1/admin/dtable/{base_uuid}/` - deleteBase
- [x] `GET /api/v2.1/admin/dtables/` - listAllBases
- [x] `GET /api/v2.1/admin/trash-dtables/` - listTrashedBases
- [x] `GET /api/v2.1/admin/users/{user_id}/dtables/` - listUsersBases
- [x] `PUT /api/v2.1/admin/trash-dtables/{base_id}/` - restoreTrashedBase
- [ ] `PUT /api/v2.1/admin/dtable/{base_uuid}/unset-password/` - deleteBasePassword
- [ ] `GET /api/v2.1/admin/dtable-notifications/` - listBaseNotifications

### Sharing Links (0/5)

- [ ] `DELETE /api/v2.1/admin/external-links/{external_link_token}/` - deleteBaseExternalLink
- [ ] `DELETE /api/v2.1/admin/view-external-links/{view_external_link_token}/` - deleteViewExternalLink
- [ ] `GET /api/v2.1/admin/dtable/{base_id}/external-links/` - listBaseExternalLinks
- [ ] `GET /api/v2.1/admin/external-links/` - listExternalLinks
- [ ] `GET /api/v2.1/admin/view-external-links/` - listViewExternalLinks

### Forms (0/4)

- [ ] `DELETE /api/v2.1/admin/collection-tables/{collection_table_token}/` - deleteDataCollectionForms
- [ ] `DELETE /api/v2.1/admin/forms/{form_token}/` - deleteForm
- [ ] `GET /api/v2.1/admin/collection-tables/` - listDataCollectionForms
- [ ] `GET /api/v2.1/admin/forms/` - listForms

### Notifications (0/4)

- [ ] `DELETE /api/v2.1/admin/invalid-notification-rules/` - deleteInvalidNotifications
- [ ] `DELETE /api/v2.1/admin/notification-rules/{notification_rule_id}/` - deleteNotificationRule
- [ ] `GET /api/v2.1/admin/invalid-notification-rules/` - listInvalidNotifications
- [ ] `GET /api/v2.1/admin/notification-rules/` - listNotificationRules

### Common Dataset (0/5)

- [ ] `DELETE /api/v2.1/admin/common-dataset/sync/{sync_id}/` - deleteInvalidSync
- [ ] `DELETE /api/v2.1/admin/common-dataset/invalid-syncs/` - deleteInvalidSyncs
- [ ] `GET /api/v2.1/admin/common-datasets/` - listCommonDataset
- [ ] `GET /api/v2.1/admin/common-dataset/periodical-syncs/` - listCommonDatasetSyncs
- [ ] `GET /api/v2.1/admin/common-dataset/invalid-syncs/` - listInvalidSyncs

### Logs (0/11)

- [ ] `DELETE /api/v2.1/admin/virus-files/{virus_id}/` - deleteVirusFile
- [ ] `GET /api/v2.1/admin/abuse-reports/` - listAbuseReports
- [ ] `GET /api/v2.1/admin/audit-logs/` - listAuditLogs
- [ ] `GET /api/v2.1/admin/email-sending-logs/` - listEmailLogs
- [ ] `GET /api/v2.1/admin/file-access-logs/` - listFileAccessLogs
- [ ] `GET /api/v2.1/admin/group-member-audit/` - listGroupMemberAuditLogs
- [ ] `GET /api/v2.1/admin/logs/login-logs/` - listLoginLogs
- [ ] `GET /api/v2.1/admin/registration-logs/` - listRegistrationLogs
- [ ] `GET /api/v2.1/admin/virus-files/` - listVirusFiles
- [ ] `PUT /api/v2.1/admin/abuse-reports/{abuse_report_id}/` - updateAbuseReport
- [ ] `PUT /api/v2.1/admin/virus-files/{virus_id}/` - updateVirusFile

### Export (0/1)

- [ ] `GET /api/v2.1/admin/dtables/{base_uuid}/synchronous-export/export-dtable/` - exportBase

### Statistics (0/7)

- [ ] `GET /api/v2.1/admin/statistics/active-users/` - getActiveUsersPerDay
- [ ] `GET /api/v2.1/admin/statistics/auto-rules/` - getAutomationRules
- [ ] `GET /api/v2.1/admin/statistics/external-apps/` - getExternalApps
- [ ] `GET /api/v2.1/admin/statistics/ai/` - getOwnerOrTeamAIStatistics
- [ ] `GET /api/v2.1/admin/statistics/scripts-running/` - getScriptRunningCountByUser
- [ ] `GET /api/v2.1/admin/daily-active-users/` - listActiveUsersByDay
- [ ] `GET /api/v2.1/admin/scripts-tasks/` - listScriptTasks

### System Info & Customizing (1/5)

- [x] `GET /api/v2.1/admin/sysinfo/` - getSystemInformation
- [ ] `POST /api/v2.1/admin/favicon/` - updateFavicon
- [ ] `PUT /api/v2.1/admin/web-settings/` - updateGeneralSettings
- [ ] `POST /api/v2.1/admin/login-background-image/` - updateLoginBackgroundImage
- [ ] `POST /api/v2.1/admin/logo/` - updateLogo

### Maintenance (0/1)

- [ ] `PUT /api/v2.1/admin/dtable/{base_uuid}/repair/` - repairBase

## File Operations (3/9)

### Files & Images (3/4)

- [x] `GET /api/v2.1/dtable/app-download-link/` - getFileDownloadLink
- [x] `GET /api/v2.1/dtable/app-upload-link/` - getUploadLink
- [x] `POST /seafhttp/upload-api/{upload_link}?ret-json=1` - uploadFile
- [ ] `DELETE /api/v2.1/dtable/app-asset/` - deleteBaseAsset

### Files & Images (Custom Folder) (0/5)

- [ ] `DELETE /api/v2.1/dtable/custom/app-asset-file/` - deleteBaseCustomFolderAsset
- [ ] `GET /api/v2.1/dtable/custom/app-download-link/` - getCustomDownloadLink
- [ ] `GET /api/v2.1/dtable/custom/app-asset-file/` - getCustomFileMetadata
- [ ] `GET /api/v2.1/dtable/custom/app-asset-dir/` - getCustomFiles
- [ ] `GET /api/v2.1/dtable/custom/app-upload-link/` - getCustomUploadLink

## Ping And Info (6/6)

### Info (1/1)

- [x] `GET /server-info/` - getServerInfo

### Ping (5/5)

- [x] `GET /api-gateway/api/v2/ping/` - pingApiGateway
- [x] `GET /dtable-db/ping/` - pingDtableDbServer
- [x] `GET /dtable-server/ping/` - pingDtableServer
- [x] `GET /api2/ping/` - pingServer
- [x] `GET /api2/auth/ping/` - pingServerWithAuth

## Python-Scheduler (0/6)

### Statistics (0/5)

- [ ] `GET /admin/statistics/by-base/` - getStatisticsGroupedByBase
- [ ] `GET /admin/statistics/by-day/` - getStatisticsGroupedByDay
- [ ] `GET /admin/statistics/scripts-running/by-base/` - scriptRunsPerBase
- [ ] `GET /admin/statistics/scripts-running/by-org/` - scriptRunsPerTeam
- [ ] `GET /admin/statistics/scripts-running/by-user/` - scriptRunsPerUser

### Runs (0/1)

- [ ] `GET /admin/runs/` - listRuns
