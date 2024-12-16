---
title: Limits
excerpt: Get an overview of all rate and size limits of the SeaTable API.
category: 66e2a322281410004601ba34
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

> 🚧 Rate limits may change
>
> Currently, the same limits apply to all SeaTable Cloud customers. In the future, SeaTable might adjust the rate limits to balance for demand and reliability. SeaTable may also introduce distinct rate limits for teams with different pricing plans.

> ❗ Important Update: API Endpoint Changes
>
> In version 5.2, the `/dtable-server` and `/dtable-db` endpoints will be deprecated and then removed in version 6.0. All functions will be transitioned to `/api-gateway` endpoints. Please update your custom integrations and scripts accordingly to ensure continued functionality. More information will be provided with the release notes of SeaTable version 5.2.

### Retrieve current rate limit usage

The new `/api-gateway` endpoints return the current API rate limit usage through `x-ratelimit` headers. These headers provide the minute limit, the current usage, and the next reset time as a Unix timestamp in seconds. Below is an example of the returned headers:

```
x-ratelimit-limit: 500
x-ratelimit-remaining: 493
x-ratelimit-reset: 1720710405
```

### General rate limits

| Endpoints                                       | SeaTable Cloud | SeaTable Dedicated and Server |
| :---------------------------------------------- | :------------- | :---------------------------- |
| All account operations<br/>`/api/v2.1/*`        | 1000/min       | 3000/min                      |
| All base operations<br/>`/api-gateway/api/v2/*` | 200/min        | 500/min                       |

### Authentication rate limits

| Endpoints                                | SeaTable Cloud | SeaTable Dedicated and Server |
| :--------------------------------------- | :------------- | :---------------------------- |
| Get Account-Token<br/>`/api2/auth-token` | 60/min         | unlimited                     |

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

- [dtable-api-gateway.conf](https://admin.seatable.io/configuration/dtable-api-gateway-conf)
- [dtable_server_config.json](https://admin.seatable.io/configuration/dtable-server-config/) - deprecated
- [dtable-db.conf](https://admin.seatable.io/configuration/dtable-db-conf/) - deprecated
- [dtable_web_settings.py](https://admin.seatable.io/configuration/dtable-web-settings/) - deprecated

## Size limits

Besides the rate limits, there are size limits for how many rows you can manipulate with a **single call**. Of course, it is possible to execute multiple calls in a row as long as you stay below the rate limits.

| Action and Endpoints                                                                                                                     | Max. number of rows |
| :--------------------------------------------------------------------------------------------------------------------------------------- | :------------------ |
| [List rows (with SQL)](https://api.seatable.io/reference/querysql)<br/>`POST /api-gateway/api/v2/dtables/{...}/sql/`                     | 10.000              |
| [Insert, Update or Delete Rows (with SQL)](https://api.seatable.io/reference/querysql)<br/>`POST /api-gateway/api/v2/dtables/{...}/sql/` | unlimited           |
| [List rows](https://api.seatable.io/reference/listrows)<br/>`GET /api-gateway/api/v2/dtables/{...}/rows/`                                | 1.000               |
| [Append rows](https://api.seatable.io/reference/appendrows)<br/>`POST /api-gateway/api/v2/dtables/{...}/rows/`                           | 1.000               |
| [Update rows](https://api.seatable.io/reference/updaterows)<br/>`PUT /api-gateway/api/v2/dtables/{...}/rows/`                            | 1.000               |
| [Delete rows](https://api.seatable.io/reference/deleterows)<br/>`DELETE /api-gateway/api/v2/dtables/{base_uuid}/rows/`                   | 10.000              |
