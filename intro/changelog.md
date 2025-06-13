---
title: Changelog
excerpt: This page lists changes made to the Web API and its documentation.
category: 67bd4bf716397e0037c123d0
isReference: true
slug: changelog
---

<style>
.markdown-body {
	--markdown-title-marginTop: 2em;
}
</style>

Listed below are all the changes to the SeaTable API. Each date corresponds to a new version of SeaTable Server Enterprise Edition. If you’re looking for changes beyond the API, see the SeaTable [Changelog](https://seatable.com/changelog) or check out the [SeaTable Blog](https://seatable.io/blog) for detailed release notes.

## Version 5.3 (16.06.2025)

> 🚧 Breaking change: API-Gateway
>
> In version 5.3, the `/dtable-server` and `/dtable-db` endpoints were removed and all functions were be transitioned to `/api-gateway` endpoints. Please update your custom integrations and scripts accordingly to ensure continued functionality. You can get more information from this [blog article](https://seatable.com/api-gateway-version-5-3/).

No further changes were made to the API documentation.

## Version 5.2 (25.02.2025)

> ❗ Important Update: API Endpoint Changes
>
> In version 5.2, the `/dtable-server` and `/dtable-db` endpoints will be deprecated and then removed in version 5.3. All functions will be transitioned to `/api-gateway` endpoints. Please update your custom integrations and scripts accordingly to ensure continued functionality. More information will be provided with the release notes of SeaTable version 5.2.

> 📘 New requests
>
> **Base Operations**
>
> - [Duplicate Table](/reference/duplicatetable) <span class="APIMethod APIMethod_fixedWidth APIMethod_post">post</span>
>
> **Account Operations - System Admin**
>
> - [List File Access Logs](/reference/listfileaccesslogs) <span class="APIMethod APIMethod_fixedWidth APIMethod_get">get</span>
>
> **Account Operations - Team Admin**
>
> - [List File Access Logs](/reference/listfileaccesslogs-1)

## Version 5.1 (08.11.2024)

[View API Documentation for v5.1](https://api.seatable.com/v5.1)

> 📘 New requests
>
> **Account Operations - System Admin**
>
> - [Repair Base](/reference/repairbase) <span class="APIMethod APIMethod_fixedWidth APIMethod_put">put</span>
> - [List Audit Logs](/reference/listauditlogs) <span class="APIMethod APIMethod_fixedWidth APIMethod_get">get</span>
>
> **Account Operations - User**
>
> - [List Big Data Backups](/reference/listbigdatabackups) <span class="APIMethod APIMethod_fixedWidth APIMethod_get">get</span>
> - [Get Big Data Status](/reference/getbigdatastatus) <span class="APIMethod APIMethod_fixedWidth APIMethod_get">get</span>
> - [List Big Data Operation Logs](/reference/getbigdataoperationlogs) <span class="APIMethod APIMethod_fixedWidth APIMethod_get">get</span>

## Version 5.0 (15.07.2024)

[View API Documentation for v5.0](https://api.seatable.com/v5.0)

We recommend using the new `/api-gateway/` endpoints. These endpoints are faster because they check if the base has remained unchanged since the last request, allowing for quicker responses.

> 🚧 Breaking changes
>
> - [Get Row](/reference/getrowdeprecated) and [List Rows](/reference/listrowsdeprecated): `Link` now returns an array containing `display_value` and `row_id` instead of a string with only the `display_value`. This change harmonizes the output with `Get Row` and `List Rows with SQL` endpoints.
> - [Get Row](/reference/getrowdeprecated) and [List Rows](/reference/listrowsdeprecated): `Link Formula` now returns the right output type depending of the result. Single numbers are returned as integers, multiple values as arrays. This change harmonizes the output of the `Get Row`, `List Rows` and `List Rows with SQL` endpoints.

> 👍 Other changes
>
> - [Get Row](/reference/getrowdeprecated): All column values are now consistently returned. If a value is not defined, `null` is returned instead of omitting the value.
> - [List Rows](/reference/listrowsdeprecated): All column values are now consistently returned. If a value is not defined, `null` is returned instead of omitting the value.
> - [Query SeaTable with SQL](/reference/querysql): Now supports `parameters` to protect against SQL injection.

For more details about the changes, please refer to [this post on the SeaTable Forum](https://forum.seatable.com/t/important-changes-to-api-and-seatable-cloud-with-version-5-0/4887).

## Version 4.4 (15.05.2024)

The SeaTable API Reference for version 4.4 is no longer accessible here. However, you can find it on [Github](https://github.com/seatable/openapi/tree/v4.4).

> 📘 New requests
>
> **Base Operations (from 4.4)**
>
> Starting with version 4.4, SeaTable introduced a new component to SeaTable Server: the API Gateway. It introduces several new API endpoints and improvements to existing ones, creating a more streamlined experience for all base operations. You can identify the new endpoints by their URLs, which include `/api-gateway/`. The old API endpoints for `dtable-server` and `dtable-db` are still valid and could be used.

> 🚧 Breaking changes
>
> - data collection table calls (user) were removed. This was done because data collection tables will be disabled in general with version 5.0. In SeaTable Cloud this feature was never available.
> - [Get Row](/reference/getrowdeprecated): `_mtime` and `_ctime` are not returned if these column types are defined in this base. This is to harmonize the output with `List Rows` and `List Rows with SQL`.

> 👍 Other changes
>
> - [List Rows](/reference/listrowsdeprecated): The options `order_by` and `direction` were removed to avoid conflict situations with a selected view.
> - API-Gateway calls now return the current api usage and limits via X-header.

## Version 4.3 (08.02.2024)

The SeaTable API Reference for version 4.3 is no longer accessible here. However, you can find it on [Github](https://github.com/seatable/openapi/tree/v4.3).

> 📘 New requests
>
> **Base Operations**
>
> - [Create Row Links in Big Data](/reference/createbigdatarowslinkdeprecated) <span class="APIMethod APIMethod_fixedWidth APIMethod_post">post</span> `/dtable-db/api/v1/base/{base_uuid}/links/`
> - [Delete Row Links in Big Data](/reference/deletebigdatarowlinksdeprecated) <span class="APIMethod APIMethod_fixedWidth APIMethod_delete">delete</span> `/dtable-db/api/v1/base/{base_uuid}/links/`
>
> **Account Operations - System Admin**
>
> - [Update Team User](/reference/updateteamuser) <span class="APIMethod APIMethod_fixedWidth APIMethod_put">put</span> `/api/v2.1/admin/organizations/{org_id}/users/{user_id}/`
>
> **Account Operations - Team Admin**
>
> - [List Team Logins](/reference/listteamlogins) <span class="APIMethod APIMethod_fixedWidth APIMethod_get">get</span> `/api/v2.1/org/{org_id}/admin/login-logs/`
> - [List User Logins](/reference/listuserlogins) <span class="APIMethod APIMethod_fixedWidth APIMethod_get">get</span> `/api/v2.1/org/{org_id}/admin/login-logs/{user_id}`
> - [Get SAML Config](/reference/getsamlconfig) <span class="APIMethod APIMethod_fixedWidth APIMethod_get">get</span> `/api/v2.1/org/{org_id}/admin/saml-config/`
> - [Update SAML Config](/reference/updatesamlconfig) <span class="APIMethod APIMethod_fixedWidth APIMethod_put">put</span> `/api/v2.1/org/{org_id}/admin/saml-config/`
> - [Verify SAML Domain](/reference/verifysamldomain) <span class="APIMethod APIMethod_fixedWidth APIMethod_put">put</span> `/api/v2.1/org/{org_id}/admin/verify-domain/`
>
> **Account Operations - User**
>
> - [Search User](/reference/searchuser-1) <span class="APIMethod APIMethod_fixedWidth APIMethod_get">get</span> `/api2/search-user/?q={search_query}`

> 👍 Other changes
>
> - New option to export the base with or without assets in `GET /api/v2.1/admin/dtables/{base_uuid}/synchronous-export/export-dtable/`.

## Version 4.2 (22.11.2023)

The SeaTable API Reference for version 4.2 is no longer accessible here. However, you can find it on [Github](https://github.com/seatable/openapi/tree/v4.2).

> 📘 New requests
>
> - New Category: Python Scheduler
> - Export base: `GET /api/v2.1/admin/dtables/{base_uuid}/synchronous-export/export-dtable/`
> - Search base/apps of a user: `GET /api/v2.1/dtable/items-search/`
> - Activate/Deactivate app: `PUT /api/v2.1/external-apps/{app_token}/status/`

> 🚧 Breaking changes
>
> None

> 👍 Other changes
>
> - Deprecated base export calls for sytem admins were removed from documentation.

## Version 4.1 (23.08.2023)

The SeaTable API Reference for version 4.1 is no longer accessible here. However, you can find it on [Github](https://github.com/seatable/openapi/tree/v4.1).

> 📘 New requests
>
> - Add user to multiple groups: `POST /api/v2.1/admin/users/{username}/groups/`

> 👍 Other changes
>
> - Add Row and Update Row: unknown single select or multiple-select options will be created
> - Improved data type and structure checks for `/rows/` endpoint
> - `row_id` cannot be changed anymore with Update Row
> - Fixed permission issue with endpoint `/api/v2.1/org/<org_id>/admin/groups/<group_id>/members/`
> - Filter validation for List Rows (with SQL)

> 🚧 Breaking changes
>
> None

## Version 4.0 (27.06.2023)

The SeaTable API Reference for version 4.0 is no longer accessible here. However, you can find it on [Github](https://github.com/seatable/openapi/tree/v4.0).

> 📘 New requests
>
> - Search User by Org-ID: `GET api/v2.1/admin/search-user-by-org-id/`
> - List Plugins Install Count: `GET api/v2.1/admin/plugins-install-count/`
> - List Org-Admin operations logs: `GET api/v2.1/org/{org_id}/admin/admin-logs/`
> - Update Team Logo: `POST api/v2.1/org/{org_id}/admin/org-logo/`
> - Get Team Logo: `GET api/v2.1/org/{org_id}/admin/org-logo/`
> - Delete Team Logo: `DELETE api/v2.1/org/{org_id}/admin/org-logo/`
> - Export Big Data View to Excel: `GET api/v2.1/workspace/{workspace_id}/dtable/{base_name}/convert-big-data-view-to-excel/`
> - Append Excel csv `POST api/v2.1/workspace/{workspace_id}/synchronous-import/append-excel-csv-to-table/`
> - List Universal Apps `GET api/v2.1/universal-apps/`
> - Batch import user to Universal App `POST api/v2.1/universal-apps/{app_token}/app-users/batch/`
> - List Universal App Users `GET api/v2.1/universal-apps/{app_token}/app-users/`
> - List Universal App Invite Links `GET api/v2.1/universal-apps/{app_token}/invite-links/`
> - Move Rows to Big Data `POST /api/v1/dtables/{base_uuid}/archive-view/`
> - Get Folder Content (Custom Folder)
> - Get File Metadata (Custom Folder)
> - Get Upload Link (Custom Folder)
> - Get Download Link (Custom Folder)

> 👍 Other changes
>
> - Added support for bearer authentication

> 🚧 Breaking changes
>
> - Get Base-Token with Invite-Link `GET api/v2.1/dtable/share-link-access-token/` was removed

## Version 3.5 (12.04.2023)

The SeaTable API Reference for version 3.5 is no longer available.

> 🚧 Breaking changes
>
> - Import from CSV `POST dtable-server/api/v1/dtables/{base_uuid}/import-csv/` was replaced with this [new call](/reference/importbasefromfile)
> - Append from CSV `POST dtable-server/api/v1/dtables/{base_uuid}/append-csv/` was replaced with this [new call](/reference/appendtotablefromfile)
> - Create Row Comment `POST dtable-server/api/v1/dtables/{base_uuid}/comments/` was removed
> - Update Row Comment `PUT dtable-server/api/v1/dtables/{base_uuid}/comments/` was removed
