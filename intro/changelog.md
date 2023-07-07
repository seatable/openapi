---
title: Changelog
excerpt: This page lists changes made to the Web API and its documentation.
category: 64464593226b5605dde1b0e2
isReference: true
slug: changelog
---

<style>
.markdown-body {
	--markdown-title-marginTop: 2em;
}
</style>

Listed below are all the changes to the SeaTable API. Each date corresponds with a new version of the SeaTable Server. If you’re looking for non-API related changes, see the [changelog](https://seatable.io/docs/changelog) or the latest product releases at the [SeaTable Blog](https://seatable.io/blog).

## Version 4.0 (27.06.2023)

> 📘 New requests
> 
> * Search User by Org-ID: `GET api/v2.1/admin/search-user-by-org-id/`.
> * List Plugins Install Count: `GET api/v2.1/admin/plugins-install-count/`.
> * List Org-Admin operations logs: `GET api/v2.1/org/{org_id}/admin/admin-logs/`.
> * Update Team Logo: `POST api/v2.1/org/{org_id}/admin/org-logo/`.
> * Get Team Logo: `GET api/v2.1/org/{org_id}/admin/org-logo/`.
> * Delete Team Logo: `DELETE api/v2.1/org/{org_id}/admin/org-logo/`.
> * Export Big Data View to Excel: `GET api/v2.1/workspace/{workspace_id}/dtable/{base_name}/convert-big-data-view-to-excel/`.
> * Append Excel csv `POST api/v2.1/workspace/{workspace_id}/synchronous-import/append-excel-csv-to-table/`.
> * List Universal Apps `GET api/v2.1/universal-apps/`.
> * Batch import user to Universal App `POST api/v2.1/universal-apps/{app_token}/app-users/batch/`.
> * List Universal App Users `GET api/v2.1/universal-apps/{app_token}/app-users/`.
> * List Universal App Invite Links `GET api/v2.1/universal-apps/{app_token}/invite-links/`.
> * Move Rows to Big Data `POST /api/v1/dtables/{base_uuid}/archive-view/`.
> * Get Folder Content (Custom Folder)
> * Get File Metadata (Custom Folder)
> * Get Upload Link (Custom Folder)
> * Get Download Link (Custom Folder)

> 🚧 Breaking changes
>
> * Get Base-Token with Invite-Link `GET api/v2.1/dtable/share-link-access-token/` was removed.

## Version 3.5 (12.04.2023)

The SeaTable API Reference for the version 3.5 is available at https://seatable.readme.io/v3.5/reference/introduction.

> 🚧 Breaking changes
>
> * Import from CSV `POST dtable-server/api/v1/dtables/{base_uuid}/import-csv/` was replaced with this [new call](/reference/import-base-from-xlsx-or-csv)
> * Append from CSV `POST dtable-server/api/v1/dtables/{base_uuid}/append-csv/` was replaced with this [new call](/reference/import-base-from-xlsx-or-csv).
> * Create Row Comment `POST dtable-server/api/v1/dtables/{base_uuid}/comments/` was removed. 
> * Update Row Comment `PUT dtable-server/api/v1/dtables/{base_uuid}/comments/` was removed.