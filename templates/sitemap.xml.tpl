<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url>
<loc>{{base_url}}</loc>
<lastmod>{{front_page_lastmod}}</lastmod>
</url>
$ for pd in filtered_pages_data
<url>
<loc>{{base_url}}{{pd.permalink}}</loc>
<lastmod>{{pd.last_update()}}</lastmod>
</url>
$ endfor
</urlset>
