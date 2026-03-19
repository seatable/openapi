# How to use a custom domain with readme.com

The following setup allows to reach api documentation via custom subdomain. A nginx webserver redirects all traffic to the readme.com page. Static files (`robots.txt`, `sitemap.xml`, `llms.txt`, `llms-full.txt`) are generated from the OpenAPI specs via GitHub Actions and deployed to the server via rsync.

## Project settings at readme.com

- PROJECT NAME: SeaTable API Reference
- MAIN URL: https://seatable.com
- Robots.txt: [x] Indexing by robots is allowed
- SITEMAP: [ ] The sitemap.xml is disabled
- CANONICAL URL: https://api.seatable.com

## Static file generation

The `generate.py` script reads all OpenAPI spec files and intro pages to produce:

- **sitemap.xml** — all reference pages derived from operationIds and intro page slugs
- **llms.txt** — compact API overview for LLM consumption ([llms.txt standard](https://llmstxt.org/))
- **llms-full.txt** — complete API reference with all endpoints, parameters, and descriptions

Run locally:

```bash
pip install pyyaml
python3 custom-domain/generate.py
```

Output goes to `custom-domain/output/`.

## Deployment

The GitHub Actions workflow `.github/workflows/deploy-static.yml` runs on every push to a `v*` branch:

1. Generates `sitemap.xml`, `llms.txt`, `llms-full.txt` from the specs
2. Copies `robots.txt` to the output directory
3. Deploys all files to the server via rsync

Required GitHub secrets: `SSH_PRIVATE_KEY`, `SSH_HOST`, `SSH_USER`.
The server must have `rrsync` configured with target `/opt/api.seatable.com/`.

## Server configuration

### nginx configuration

Nginx runs as a Docker container. The static files reside under `/opt/api.seatable.com/` on the host and are mounted at the same path inside the container.

It is important to add any header in the nginx configuration, otherwise the google crawling bots deny crawling the page.

```bash
server {
    listen 443 ssl;
    server_name api.seatable.com;

    ssl_certificate /etc/letsencrypt/live/api.seatable.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.seatable.com/privkey.pem;
    ssl_session_timeout 5m;

    ssl_protocols TLSv1.2;
    ssl_ciphers AES256+EECDH:AES256+EDH:!aNULL;
    ssl_prefer_server_ciphers on;

    ssl_dhparam /etc/nginx/dhparam.pem;
    ssl_ecdh_curve secp384r1;

    location / {
      resolver 8.8.8.8;
      proxy_pass https://seatable.readme.io;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header Host "seatable.readme.io";
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_ssl_server_name on;
      proxy_ssl_name seatable.readme.io;
      add_header "contact" "seatable.io";
      proxy_set_header User-Agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0";
    }

    location /sitemap.xml {
        root /opt/api.seatable.com/;
        access_log off;
    }

    location /robots.txt {
        root /opt/api.seatable.com/;
        access_log off;
    }

    location /llms.txt {
        root /opt/api.seatable.com/;
        access_log off;
    }

    location /llms-full.txt {
        root /opt/api.seatable.com/;
        access_log off;
    }
}
```
