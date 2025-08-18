---
title: Limits
excerpt: Get an overview of all rate and size limits of the SeaTable API.
category: 68a31677008af4fb2f94f547
isReference: true
slug: limits
---

<style>
.markdown-body {
	--markdown-title-marginTop: 2em;
}
</style>

To ensure a consistently good user experience and protect the server, SeaTable limits the frequency of API calls (rate limit). Additionally, SeaTable limits the number of rows that can be modified with a single request (size limit).


## Rate Limits

All SeaTable API endpoints, except `/ping` and `/server-info`, are subject to rate limits. The concrete limits can be found in the following tables. The calls are counted either per base, or if not available, per IP address.

Once the limit is reached, further requests are declined and SeaTable returns the HTTP response status **429** without any further output.

The `/api-gateway` endpoints return the current API usage through `x-ratelimit` headers. These headers provide the minute limit, the current usage, and the next reset time as a Unix timestamp in seconds. Below is an example of the returned headers:

```
x-ratelimit-limit: 500
x-ratelimit-remaining: 493
x-ratelimit-reset: 1720710405
```

> ❗ SeaTable Cloud: Monthly API limits
>
> Due to excessive use of SeaTable Cloud's API by some users, SeaTable Cloud introduced monthly API limits in the summer 2025. (In this [blog post](https://seatable.com/api-gateway-version-5-3/), you find background information.) >
> 
> The monthly API limits are a function of the subscription and the number of users in the team. The limit is automatically reset at the end of each month. 
> 
> If you have exhausted your API limit for the month, you can upgrade your subscription to SeaTable Cloud and/or add more users to your paid subscription. The extra API calls are available momentarily after the upgrade. For more information on the specific limits, see the [pricing page](https://seatable.com/de/preise/).

### General rate limits

| Endpoints                                       | SeaTable Cloud | SeaTable Dedicated and Server |
| :---------------------------------------------- | :------------- | :---------------------------- |
| All account operations<br/>`/api/v2.1/*`        | 1000/min       | 3000/min                      |
| All base operations<br/>`/api-gateway/api/v2/*` | 200/min        | 500/min                       |

### Authentication rate limits

| Endpoints                                | SeaTable Cloud | SeaTable Dedicated and Server |
| :--------------------------------------- | :------------- | :---------------------------- |
| Get Account-Token<br/>`/api2/auth-token` | 60/min         | unlimited                     |


### How to avoid the rate limits

To find out if you are rate-limited, look for the response status code `HTTP 429 Too Many Requests`. This response status code indicates that you sent too many requests in a given amount of time and need to make adjustments.

If this is the case, you should start thinking about how to reduce the number of calls. Here are some common approaches to prevent the status code 429.

- Check your code for unnecessary requests.
- Slow down the speed or the frequency of your cronjob.
- Use caching technics or use a queue for pending requests.
- Only request new data, if something changed.
- Use SeaTable Webhooks to be informed about changes in your base instead of asking continuously for changes via the API.

### Customization of rate limits

If you are a SeaTable Dedicated customer or you run your own SeaTable Server instance (Enterprise and Developer Edition), you can modify the default limits. The limits are set in configuration files. Beginning with SeaTable Server v5.3, the limits are defined in one single configuration file. In prior versions, updating rate limits involved modifying multiple configuration files:

- [dtable-api-gateway.conf](https://admin.seatable.com/configuration/dtable-api-gateway-conf) (**from** version 5.3)
- [dtable_server_config.json](https://admin.seatable.com/configuration/dtable-server-config/) - (before version 5.3)
- [dtable-db.conf](https://admin.seatable.com/configuration/dtable-db-conf/) (before version 5.3)
- [dtable_web_settings.py](https://admin.seatable.com/configuration/dtable-web-settings/) (before version 5.3)

For more information about the configuration files, see the [SeaTable Admin Manual](https://admin.seatable.com).

## Size Limits

Besides the rate limits, there are size limits for how many rows a **single call** can manipulate. Of course, it is possible to execute multiple calls in a row as long as you stay below the rate limits.

| Action and Endpoints                                                                                                                      | Max. number of rows |
| :---------------------------------------------------------------------------------------------------------------------------------------- | :------------------ |
| [List rows (with SQL)](https://api.seatable.com/reference/querysql)<br/>`POST /api-gateway/api/v2/dtables/{...}/sql/`                     | 10.000              |
| [Insert, Update or Delete Rows (with SQL)](https://api.seatable.com/reference/querysql)<br/>`POST /api-gateway/api/v2/dtables/{...}/sql/` | unlimited           |
| [List rows](https://api.seatable.com/reference/listrows)<br/>`GET /api-gateway/api/v2/dtables/{...}/rows/`                                | 1.000               |
| [Append rows](https://api.seatable.com/reference/appendrows)<br/>`POST /api-gateway/api/v2/dtables/{...}/rows/`                           | 1.000               |
| [Update rows](https://api.seatable.com/reference/updaterows)<br/>`PUT /api-gateway/api/v2/dtables/{...}/rows/`                            | 1.000               |
| [Delete rows](https://api.seatable.com/reference/deleterows)<br/>`DELETE /api-gateway/api/v2/dtables/{base_uuid}/rows/`                   | 10.000              |
