---
title: Limits
excerpt: Get an overview of all rate and size limits of the SeaTable API.
category: 65e6ef8514da74005d339fac
isReference: true
slug: limits
---

<style>
.markdown-body {
	--markdown-title-marginTop: 2em;
}
</style>

To ensure a consistent developer experience for all API users, the SeaTable-API is rate limited and denies further API requests as soon as the rate limit is reached. Furthermore, the amount of data dealing with one request is limited, too.

## Rate limits

All SeaTable API endpoints, except `/ping` and `/server-info` have a rate limit. The concrete limits can be found in the following tables. The accesses are counted either per base, or if not available, per IP address.

Meaning that if you reach the rate limit for one base, you still could make requests for other bases. If you hit the rate limit, the request will return the HTTP response status **429** without any further output.

The access counter is not reset at a specific time, but the relevant period is always checked at the time of access.

> 🚧 Rate limits may change
>
> Currently, the same limits apply to all SeaTable Cloud customers. In the future, SeaTable might adjust the rate limits to balance for demand and reliability. SeaTable may also introduce distinct rate limits for teams with different pricing plans.

### General rate limits

| Endpoints                                              | SeaTable Cloud       | SeaTable Dedicated and Server |
| :----------------------------------------------------- | :------------------- | :---------------------------- |
| All web operations<br/>`/api/v2.1/*`                   | 300/min              | unlimited                     |
| All base operations<br/>`/dtable-server/api/v1/*`      | 300/min<br/>5000/day | 600/min<br/>5000/day          |
| All dtable-db operations<br/>`/dtable-db/api/v1/*`     | 300/min<br/>5000/day | unlimited                     |
| All api-gateway operations<br/>`/api-gateway/api/v2/*` | 300/min<br/>5000/day | unlimited                     |

### Authentication rate limits

| Endpoints                                               | SeaTable Cloud | SeaTable Dedicated and Server |
| :------------------------------------------------------ | :------------- | :---------------------------- |
| Get Account-Token<br/>`/api2/auth-token`                | 60/min         | unlimited                     |
| Base Base-Token<br/>`/api/v2.1/dtable/app-access/token` | 60/min         | unlimited                     |

### Base operations: special limits for data retrieval

Retrieving records from a base is by far the most resource-intensive process, which is why it is subject to stricter limits.

| Endpoints                                                                                             | SeaTable Cloud      | SeaTable Dedicated and Server |
| :---------------------------------------------------------------------------------------------------- | :------------------ | :---------------------------- |
| `GET /dtable-server/api/v1/dtables/{...}/rows/`<br/>`POST /dtable-server/api/v1/{...}/filtered-rows/` | 60/min<br/>600/hour | 100/min<br/>6000/hour         |

## How to avoid the rate limits

To find out if you are rate-limited, look for the response status code `HTTP 429 Too Many Requests`. This response status code indicates that you sent too many requests in a given amount of time and need to make adjustments.

If this is the case, you should start thinking about how to reduce the number of calls. Here are some common approaches to prevent the status code 429.

- Check your code for unnecessary requests.
- Slow down the speed or the frequency of your cronjob.
- Use caching technics or use a queue for pending requests.
- Only request new data, if something changed.
- Use SeaTable Webhooks to be informed about changes in your base instead of asking continuously for changes via the API.

## Customization of limits

SeaTable Dedicated customers and operators of their own SeaTable Server (Enterprise or Developer Edition) can adjust SeaTable's default limits according to their needs. These are the corresponding configuration files in the [SeaTable Admin Manual](https://admin.seatable.io):

- [dtable_server_config.json](https://admin.seatable.io/configuration/dtable-server-config/)
- [dtable_web_settings.py](https://admin.seatable.io/configuration/dtable-web-settings/)
- [dtable-db.conf](https://admin.seatable.io/configuration/dtable-db-conf/)

## Size limits

Besides the rate limits, there are size limits for how many rows you can manipulate with a **single call**. Of course, it is possible to execute multiple calls in a row as long as you stay below the rate limits.

| Action and Endpoints                                                                                                                            | Max. number of rows |
| :---------------------------------------------------------------------------------------------------------------------------------------------- | :------------------ |
| [List rows (with SQL)](https://api.seatable.io/reference/querysqldeprecated)<br/>`POST /dtable-db/api/v1/query/{...}/`                          | 10.000              |
| [Insert, Update or Delete Rows (with SQL)](https://api.seatable.io/reference/querysqldeprecated)<br/>`POST /dtable-db/api/v1/query/{...}/`      | unlimited           |
| [List rows](https://api.seatable.io/reference/listrowsdeprecated)<br/>`GET /dtable-server/api/v1/dtables/{...}/rows/`                           | 1.000               |
| [Append rows](https://api.seatable.io/reference/appendrowsdeprecated)<br/>`POST /dtable-server/api/v1/dtables/{...}/batch-append-rows/`         | 1.000               |
| [Update rows](https://api.seatable.io/reference/updaterowsdeprecated)<br/>`PUT /dtable-server/api/v1/dtables/{...}/batch-update-rows/`          | 1.000               |
| [Delete rows](https://api.seatable.io/reference/deleterowsdeprecated)<br/>`DELETE /dtable-server/api/v1/dtables/{base_uuid}/batch-delete-rows/` | 10.000              |
