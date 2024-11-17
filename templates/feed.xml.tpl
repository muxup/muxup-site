<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="en">
<title>Muxup</title>
<subtitle>Adventures in collaborative open source development</subtitle>
<link href="{{base_url}}/feed.xml" rel="self" type="application/atom+xml"/>
<link href="{{base_url}}"/>
<updated>{{filtered_pages_data[0].last_update(False)}}T12:00:00Z</updated>
<id>{{base_url}}/feed.xml</id>
$ for pd in filtered_pages_data[:10]
<entry>
<title>{{h(pd.title)}}</title>
<published>{{pd.published_date}}T12:00:00Z</published>
<updated>{{pd.last_update(False)}}T12:00:00Z</updated>
<link rel="alternate" href="{{base_url}}{{pd.permalink}}"/>
<id>{{base_url}}{{pd.permalink}}</id>
<content type="html">
{{h(replace_rel_with_abs_links(pd.markdown_content_as_html)).rstrip()}}
</content>
</entry>
$ endfor
</feed>
