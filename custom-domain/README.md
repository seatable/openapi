# How to use a custom domain with readme.com

The following setup allows to reach api documentation via custom subdomain. A nginx webserver redirects all traffic to the readme.com page. The sitemap is generated every day and delivered by nginx.

## Project settings at readme.com

- PROJECT NAME: SeaTable API Reference
- MAIN URL: https://seatable.io
- Robots.txt: [x] Indexing by robots is allowed
- SITEMAP: [ ] The sitemap.xml is disabled
- CANONICAL URL: https://api.seatable.io

## Server configuration

### nginx configuration

This is the nginx configuration to redirect the traffic from a subdomain to readme.com.
It is important to add any header in the nginx configuration, otherwise the google crawling bots deny crawling the page.

```bash
server {
    listen 443 ssl;
    server_name api.seatable.io;

    ssl_certificate /etc/letsencrypt/live/api.seatable.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.seatable.io/privkey.pem;
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
        root /var/www/api.seatable.io/;
        access_log off;
    }

    location /robots.txt {
        root /var/www/api.seatable.io/;
        access_log off;
    }
}
```

### robots.txt

The `/var/www/api.seatable.io/robots.txt` looks like this:

```bash
User-agent: *
Allow: /
Disallow: /edit/
Disallow: /suggested-edits/
Disallow: /login
Disallow: /logout
Disallow: /v9
Disallow: /v8
Disallow: /v7
Disallow: /v6
Disallow: /v5
Disallow: /v4
Disallow: /v3
Disallow: /v2
Disallow: /v1
```

### Cronjob to create a sitemap.xml

The following script runs every day one via cronjob in the directory `/var/www/api.seatable.io` and generates a `sitemap.xml`.

```bash
#!/bin/bash

SOURCE_URL="https://api.seatable.io/reference/introduction"
OUTPUT_FILE_NAME="/var/www/api.seatable.io/sitemap.xml"

echo "Generate a new sitemap for ${SOURCE_URL}"
curl ${SOURCE_URL} | grep -o 'href="/reference/[^"]*">' | cut -c7- | rev | cut -c3- | rev > ./found_links.txt
sort /tmp/found_links.txt | uniq > /tmp/found_links_cleaned.txt

# Create the XML header
echo '<?xml version="1.0" encoding="UTF-8"?>' > ${OUTPUT_FILE_NAME}
echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' >> ${OUTPUT_FILE_NAME}

# Read each line from the input file and generate XML entries
while IFS= read -r line; do
    line=$(echo "$line" | sed 's/^\///')  # Remove leading /
    echo "  <url>" >> ${OUTPUT_FILE_NAME}
    echo "    <loc>https://api.seatable.io/$line</loc>" >> ${OUTPUT_FILE_NAME}
    echo "    <changefreq>daily</changefreq>" >> ${OUTPUT_FILE_NAME}
    echo "    <priority>0.3</priority>" >> ${OUTPUT_FILE_NAME}
    echo "  </url>" >> ${OUTPUT_FILE_NAME}
done < found_links_cleaned.txt

# Close the XML
echo '</urlset>' >> ${OUTPUT_FILE_NAME}

rm /tmp/found_links.txt
rm /tmp/found_links_cleaned.txt
```
