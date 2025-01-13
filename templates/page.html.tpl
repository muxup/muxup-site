<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta property="og:title" content="{{h(pd.title)}}"/>
<meta property="og:site_name" content="Muxup">
<meta property="og:description" content="{{h(pd.description)}}"/>
<meta property="og:type" content="article"/>
<meta property="og:url" content="{{base_url}}{{pd.permalink}}"/>
<meta property="og:image" content="{{opengraph_image}}"/>
<title>{{h(pd.title)}} - Muxup</title>
<link rel="icon" sizes="any" href="data:image/svg+xml,{{favicon_svg}}">
<meta name="description" content="{{h(pd.description)}}">
<style>
{{css}}</style>
<link rel="alternate" type="application/atom+xml" title="Atom Feed" href="/feed.xml"/>
<link rel="canonical" href="{{base_url}}{{pd.permalink}}"/>
</head>
<body>
<div id="article-container">
<div>
<div id="article-logo"><span id="logo-highlight"><a href="/">Muxup</a></span></div>
</div>
<h1 id="article-title"><span id="title-highlight">{{h(pd.title)}}</span></h1>
<div id="article-meta">{{article_meta}}</div>
{{pd.markdown_content_as_html}}
</div>
<footer class="footer">
<img id="footer-image" src="data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%3E%3C/svg%3E" width="50" height="50"/>
<p>Curated by Alex Bradbury | &copy; <a href="/">Muxup</a> contributors | <a href="/about">About</a> | <a href="https://github.com/muxup">GitHub</a></p>
</footer>
<script>
{{minified_article_js}}
</script>
</body>
</html>
