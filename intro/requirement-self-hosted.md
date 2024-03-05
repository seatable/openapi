---
title: Try It! with your own Server
excerpt: Prerequisites to use api.seatable.io with your own self-hosted SeaTable server.
category: 65e6ef8514da74005d339fac
isReference: true
slug: requirement-self-hosted
---

<style>
.markdown-body {
	--markdown-title-marginTop: 2em;
}
a[href="https://seatable.io/registrierung/?lang=auto"] {
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

[Register now](https://seatable.io/registrierung/?lang=auto)

## Try It! with SeaTable Server

If you are running your own [SeaTable server](https://seatable.io/on-premises/?lang=auto), you will need to change your nginx configuration so that the **Try It!** function works with your server and that you can easily copy and paste the generated API requests without authorization errors. Please replace your existing nginx configuration at `/opt/seatable/seatable-data/seatable/conf/nginx.conf` with the following setup.

Of course you have to replace `{your.seatable.server}` with the public URL of your server and then reload the updated nginx configuration inside the SeaTable docker container with `nginx -s reload`. For more details about this command and the SeaTable docker container, check the [admin manual](https://manual.seatable.io).

```bash nginx configuration (4.0 and newer)
log_format seatableformat '\$http_x_forwarded_for \$remote_addr [\$time_local] "\$request" \$status \$body_bytes_sent "\$http_referer" "\$http_user_agent" \$upstream_response_time';

upstream dtable_servers {
    server 127.0.0.1:5000;
    keepalive 15;
}

server {
    listen 80;
    server_name {your.seatable.server};

    # rewrite to https
    location / {
        rewrite ^ https://$http_host$request_uri? permanent;
    }
    # for letsencrypt
    location ^~ /.well-known/acme-challenge/ {
        alias /var/www/challenges/;
        try_files $uri =404;
    }
}

server {
    server_name {your.seatable.server};
    listen 443 ssl;
    ssl_certificate /opt/ssl/{your.seatable.server}.crt;
    ssl_certificate_key /opt/ssl/{your.seatable.server}.key;

    # SSL Hardening
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers AES256+EECDH:AES256+EDH:!aNULL;
    ssl_prefer_server_ciphers on;
    ssl_ecdh_curve secp384r1;

    ssl_session_timeout  10m;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;

    # general proxy_settings
    proxy_set_header X-Forwarded-For $remote_addr;

    # CORS seetings to allow API from readme.com
    proxy_hide_header   'Access-Control-Allow-Origin';
    add_header 'Access-Control-Allow-Origin' '*' always;
    add_header 'Access-Control-Allow-Methods' 'GET,POST,PUT,DELETE,OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'Content-Type, Accept, authorization, token, deviceType' always;
    if ($request_method = 'OPTIONS') {
	    return 204;
    }

    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Host $server_name;
        proxy_read_timeout  1200s;
        client_max_body_size 0;
        access_log      /opt/nginx-logs/dtable-web.access.log seatableformat;
        error_log       /opt/nginx-logs/dtable-web.error.log;
    }

    location /seafhttp {
        rewrite ^/seafhttp(.*)$ $1 break;
        proxy_pass http://127.0.0.1:8082;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_request_buffering off;
        proxy_connect_timeout  36000s;
        proxy_read_timeout     36000s;
        proxy_send_timeout     36000s;
        send_timeout           36000s;
        client_max_body_size   0;
        access_log             /opt/nginx-logs/seafhttp.access.log seatableformat;
        error_log              /opt/nginx-logs/seafhttp.error.log;
    }

    location /media {
        root /opt/seatable/seatable-server-latest/dtable-web;
    }

    location /socket.io {
        proxy_pass http://dtable_servers;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_redirect   off;
        proxy_buffers    8 32k;
        proxy_buffer_size 64k;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_set_header X-NginX-Proxy true;
        access_log      /opt/nginx-logs/socket-io.access.log seatableformat;
        error_log       /opt/nginx-logs/socket-io.error.log;
    }

    location /dtable-server {
        rewrite ^/dtable-server/(.*)$ /$1 break;
        proxy_pass         http://dtable_servers;
        proxy_redirect     off;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Host  $server_name;
        proxy_set_header   X-Forwarded-Proto $scheme;
        client_max_body_size 50m;
        access_log         /opt/nginx-logs/dtable-server.access.log seatableformat;
        error_log          /opt/nginx-logs/dtable-server.error.log;
    }

    location /dtable-db/ {
        proxy_pass         http://127.0.0.1:7777/;
        proxy_redirect     off;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Host  $server_name;
        proxy_set_header   X-Forwarded-Proto $scheme;
        access_log         /opt/nginx-logs/dtable-db.access.log seatableformat;
        error_log          /opt/nginx-logs/dtable-db.error.log;
    }
}
```

```bash nginx configuration (before 4.0)
# rewrite "bearer token" to "Token token"
map "$http_authorization" $authorization {
    ~*^Bearer(\s*)(?<token>(.*))$ "Token $token";
    default $http_authorization;
}

log_format seatableformat '\$http_x_forwarded_for \$remote_addr [\$time_local] "\$request" \$status \$body_bytes_sent "\$http_referer" "\$http_user_agent" \$upstream_response_time';

upstream dtable_servers {
    server 127.0.0.1:5000;
    keepalive 15;
}

server {
    listen 80;
    server_name {your.seatable.server};

    # rewrite to https
    location / {
        rewrite ^ https://$http_host$request_uri? permanent;
    }
    # for letsencrypt
    location ^~ /.well-known/acme-challenge/ {
        alias /var/www/challenges/;
        try_files $uri =404;
    }
}

server {
    server_name {your.seatable.server};
    listen 443 ssl;
    ssl_certificate /opt/ssl/{your.seatable.server}.crt;
    ssl_certificate_key /opt/ssl/{your.seatable.server}.key;

    # SSL Hardening
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers AES256+EECDH:AES256+EDH:!aNULL;
    ssl_prefer_server_ciphers on;
    ssl_ecdh_curve secp384r1;

    ssl_session_timeout  10m;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;

    # general proxy_settings
    proxy_set_header X-Forwarded-For $remote_addr;

    # CORS seetings to allow API from readme.com
    proxy_hide_header   'Access-Control-Allow-Origin';
    add_header 'Access-Control-Allow-Origin' '*' always;
    add_header 'Access-Control-Allow-Methods' 'GET,POST,PUT,DELETE,OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'Content-Type, Accept, authorization, token, deviceType' always;
    if ($request_method = 'OPTIONS') {
	    return 204;
    }

    location / {
        proxy_set_header Authorization $authorization;
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Host $server_name;
        proxy_read_timeout  1200s;
        client_max_body_size 0;
        access_log      /opt/nginx-logs/dtable-web.access.log seatableformat;
        error_log       /opt/nginx-logs/dtable-web.error.log;
    }

    location /seafhttp {
        proxy_set_header Authorization $authorization;
        rewrite ^/seafhttp(.*)$ $1 break;
        proxy_pass http://127.0.0.1:8082;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_request_buffering off;
        proxy_connect_timeout  36000s;
        proxy_read_timeout     36000s;
        proxy_send_timeout     36000s;
        send_timeout           36000s;
        client_max_body_size   0;
        access_log             /opt/nginx-logs/seafhttp.access.log seatableformat;
        error_log              /opt/nginx-logs/seafhttp.error.log;
    }

    location /media {
        root /opt/seatable/seatable-server-latest/dtable-web;
    }

    location /socket.io {
        proxy_pass http://dtable_servers;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_redirect   off;
        proxy_buffers    8 32k;
        proxy_buffer_size 64k;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_set_header X-NginX-Proxy true;
        access_log      /opt/nginx-logs/socket-io.access.log seatableformat;
        error_log       /opt/nginx-logs/socket-io.error.log;
    }

    location /dtable-server {
        proxy_set_header Authorization $authorization;
        rewrite ^/dtable-server/(.*)$ /$1 break;
        proxy_pass         http://dtable_servers;
        proxy_redirect     off;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Host  $server_name;
        proxy_set_header   X-Forwarded-Proto $scheme;
        client_max_body_size 50m;
        access_log         /opt/nginx-logs/dtable-server.access.log seatableformat;
        error_log          /opt/nginx-logs/dtable-server.error.log;
    }

    location /dtable-db/ {
        proxy_set_header Authorization $authorization;
        proxy_pass         http://127.0.0.1:7777/;
        proxy_redirect     off;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Host  $server_name;
        proxy_set_header   X-Forwarded-Proto $scheme;
        access_log         /opt/nginx-logs/dtable-db.access.log seatableformat;
        error_log          /opt/nginx-logs/dtable-db.error.log;
    }
}
```

### Enable CORS to allow requests from api.seatable.io

CORS is the abbreviation for [Cross-origin resource sharing](https://en.wikipedia.org/wiki/Cross-origin_resource_sharing), which is a security mechanism to prevent request from another domain to your server. If you don't allow CORS request for api.seatable.io, the **Try It!** button will not work. After the click you will see a rotating circle on the button and error messages in your browser console.

![Try It! with CORS error](https://seatable.io/wp-content/uploads/2023/03/readme-com-cors-access-control.png)

To prevent this CORS must be allowed and therefore the following code is necessary in your nginx configuration.

```bash Enable CORS
# CORS seetings to allow API from readme.com
proxy_hide_header   'Access-Control-Allow-Origin';
add_header 'Access-Control-Allow-Origin' '*' always;
add_header 'Access-Control-Allow-Methods' 'GET,POST,PUT,DELETE,OPTIONS' always;
add_header 'Access-Control-Allow-Headers' 'Content-Type, Accept, authorization, token, deviceType' always;
if ($request_method = 'OPTIONS') {
    return 204;
}
```

> 📘 add_header does not inherit
>
> A common error with `add_header` is that these values are not inherited. I.e. in the `location ...` blocks no `add_header` may occur, because otherwise the previously set headers are not taken over.

## Rewrite of the authorization header (only necessary for SeaTable <4.0)

Before Version 4.0 SeaTable uses an authorization header that does not comply with the OpenAPI standard. This API reference generates API requests with an authorization header like `authorization: Bearer xxx` but SeaTable requires headers like `authorization: Token xxx`. The following part of the nginx configuration rewrites the header. With Version 4.0 SeaTable will also accept [Bearer Authentication](https://swagger.io/docs/specification/authentication/bearer-authentication/) and this part is not necessary any more.

```
map "$http_authorization" $authorization {
    ~*^Bearer(\s*)(?<token>(.*))$ "Token $token";
    default $http_authorization;
}
location / {
    proxy_set_header Authorization $authorization;
    ...
}
location /seafhttp {
    proxy_set_header Authorization $authorization;
    ...
}
location /dtable-server {
    proxy_set_header Authorization $authorization;
    ...
}
location /dtable-db/ {
    proxy_set_header Authorization $authorization;
    ...
}
```

###
