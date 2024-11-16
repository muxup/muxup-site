<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta property="og:title" content="Muxup"/>
<meta property="og:site_name" content="Muxup">
<meta property="og:description" content="Adventures in collaborative open source development"/>
<meta property="og:type" content="website"/>
<meta property="og:url" content="{{base_url}}"/>
<meta property="og:image" content="{{opengraph_image}}"/>
<meta property="twitter:card" content="summary_large_image">
<meta property="twitter:site" content="@muxup">
<meta property="twitter:creator" content="@asbradbury">
<title>Muxup - Adventures in collaborative open source development</title>
<link rel="icon" sizes="any" href="data:image/svg+xml,{{favicon_svg}}">
<style>
{{css}}/* GATED_CSS */
</style>
<link rel="alternate" type="application/atom+xml" title="Atom Feed" href="/feed.xml"/>
<link rel="canonical" href="{{base_url}}/"/>
</head>
<body>
<div id="home-container">
<div id="hero">
<h1><span id="home-logo"><a href="/">Muxup</a></span></h1>
<div class="subtitle">Adventures in collaborative open source development</div>
<p>
A space maintained by Alex Bradbury - projects, blog posts, and notes on things I've been working on.
See also: <a href="https://github.com/muxup">GitHub</a>
</div>
<div class="card-grid">
$ for pd in sorted_filtered_pages_for_cards
<a class="card" href="{{pd.permalink}}">
<h2 class="card-title"><span class="highlight-title">{{h(pd.title)}}</span></h2>
$ if pd.yyyyqq_dir
<p class="card-date">{{pd.yyyyqq_dir.upper()}}</p>
$ endif
<p class="card-description">{{h(pd.description)}}</p>
</a>
$ endfor
</div>
</div>
{{standard_footer}}
<script>
{{minified_home_js}}
</script>
</body>
</html>
