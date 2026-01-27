---
title: Try It! with your own Server
excerpt: Prerequisites to use api.seatable.com with your own self-hosted SeaTable server.
category: 6978dfd7217b10efe565eee6
isReference: true
slug: requirement-self-hosted
---

<style>
.markdown-body {
	--markdown-title-marginTop: 2em;
}
a[href="https://seatable.com/registration/"] {
    color: #ffffff !important;
    font-size: 1.2rem;
    font-weight: 600;
    text-decoration: none !important;
    border-radius: 8px;
    padding: 6px 20px;
    background: linear-gradient(239deg,#FF8000 78%,#ec2837 100%);
}
</style>

The **Try It!** button allows you to run any API requests directly from the browser and view an actual response from the SeaTable API.
This feature makes it super easy to explore and get to know the SeaTable API with all its parameters and schemas.

> 👍 No user data leaves your browser
>
> Everything what you do on this website, happens solely on your browser. Every API-Request is send directly from your browser to SeaTable Cloud. Therefore you don't have to worry. You can enter and use your real credentials and tokens.

## Try It! with SeaTable Cloud

There are no requirements needed to use **Try It!** with cloud.seatable.io. Of course you will need an account but the registration is free and should take only some seconds.
After the first login you can start right away to start with your first API requests.

[Register now](https://seatable.com/registration/)

## Try It! with SeaTable Server

If you are running your own [SeaTable server](https://seatable.com/on-premises/), the **Try It!** feature works seamlessly with your server, allowing you to easily copy and paste the generated API requests without encountering authorization errors.

### Technical background: Enable CORS to allow requests from api.seatable.com

This section is for those interested in the technical details behind why api.seatable.com can send requests to your SeaTable server. To enable this functionality, CORS (Cross-Origin Resource Sharing) must be configured to allow requests from api.seatable.com.

`CORS` is the abbreviation for [Cross-origin resource sharing](https://en.wikipedia.org/wiki/Cross-origin_resource_sharing), which is a security mechanism to prevent request from another domain to your server. If you don't allow CORS request for api.seatable.com, the **Try It!** button will not work. After the click you will see a rotating circle on the button and error messages in your browser console.

![Try It! with CORS error](https://seatable.com/openapi/readme-com-cors-access-control.png)

To prevent this CORS must be allowed and therefore the following code is necessary in your nginx configuration.

```bash Enable CORS
# CORS seetings to allow API from readme.com
proxy_hide_header   'Access-Control-Allow-Origin';
add_header 'Access-Control-Allow-Origin' '*' always;
add_header 'Access-Control-Allow-Methods' 'GET,POST,PUT,DELETE,OPTIONS' always;
add_header 'Access-Control-Allow-Headers' 'Content-Type, Accept, authorization, token, deviceType, x-seafile-otp' always;
if ($request_method = 'OPTIONS') {
    return 204;
}
```

> 📘 add_header does not inherit
>
> A common error with `add_header` is that these values are not inherited. I.e. in the `location ...` blocks no `add_header` may occur, because otherwise the previously set headers are not taken over.

