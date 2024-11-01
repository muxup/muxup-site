#!/usr/bin/env python3

# Copyright Muxup contributors.
# Distributed under the terms of the MIT license, see LICENSE for details.
# SPDX-License-Identifier: MIT

import argparse
import datetime
import html
import json
import mimetypes
import os
import pathlib
import re
import shutil
import subprocess
import threading
import tomllib
import typing
import urllib.parse
from contextlib import contextmanager
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Iterator, Tuple, TypeVar

import mistletoe
import mistletoe.utils
import pygments.style
import pygments.token
import pygments.util
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name as get_lexer

# Data definitions
base_url = "https://muxup.com"
gated_css_rules = {
    "<h3": """\
h3 {
  font-size:2.074rem
}""",
    "<h4": """\
h4 {
  font-size:1.728rem
}""",
    "<h5": """\
h5 {
  font-size:1.44rem
}""",
    "<h6": """\
h6 {
  font-size:1.2rem
}""",
    "<small": """\
small {
  font-size:.833rem
}""",
    "<mark": """\
mark {
  background:#fff474
}""",
    "<blockquote": """\
blockquote {
  margin:1rem 0;
  padding:0 0.8rem;
  border-inline-start:4px solid #dadee4;
}""",
    "<hr": """\
hr {
  border:none;
  border-top:4px solid #f1f3f5;
}""",
    "<code": """\
code {
  background:#f5f5f5;
  padding:.125rem .25rem;
  font-size:.833rem
}""",
    "<pre": """\
pre > code {
  padding:0;
  background:#fff;
}
pre {
  word-wrap:break-word;
  overflow-x:auto;
  padding:.5rem 1rem;
  margin:1rem -1rem;
  border-radius:.4rem;
  border:1px solid #d2d2d2;
}""",
    "<table": """\
table {
  border-spacing:.75rem 0;
  text-align:left;
  width:100%;
  margin:0 0 1.5rem 0;
}
td, th {
  border-bottom:.05rem solid #dadee4;
  padding:.6rem 0;
}""",
    "<kbd": """\
kbd {
  background:#212529;
  border-radius:.2rem;
  color:#fff;
  font-size:.85em;
  font-weight:700;
  line-height:1;
  padding:2px 4px;
  white-space:nowrap;
}""",
    "<details": """\
details {
 font-size:.833rem;
}
details summary {
  margin:.75rem 0 .5rem 0;
  font-weight:600;
  cursor:pointer;
  font-size:1.2rem;
  line-height:1.25;
  letter-spacing:-.025em;
  list-style:none;
}
details summary > * {
  display:inline;
}
summary::-webkit-details-marker {
  display:none;
}
summary::after {
  content: " »";
}
details[open] summary::after {
  content: " «";
}
""",
}

favicon_svg = (
    """\
<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>\
<text y='80' font-size='110'>▨</text>\
</svg>\
""".replace(
        '"', "%22"
    )
    .replace("<", "%3C")
    .replace("/", "%2F")
    .replace(">", "%3E")
    .replace("#", "%23")
    .replace(" ", "%20")
)

standard_footer = """\
<footer class="footer">
<img id="footer-image" src="data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%3E%3C/svg%3E" width="50" height="50"/>
<p>Curated by Alex Bradbury | &copy; <a href="/">Muxup</a> contributors | <a href="/about">About</a> | <a href="https://github.com/muxup">GitHub</a></p>
</footer>\
"""


# Helpers
def page_path_to_permalink(path: pathlib.Path) -> str:
    return "/" + str(path.relative_to(pages_path).with_suffix(""))


@dataclass
class PageData:
    src_path: pathlib.Path
    title: str
    description: str
    published_date: str
    permalink: str
    markdown_content: str
    markdown_content_as_html: str
    hidden: bool
    extra_css: str
    yyyyqq_dir: str | None
    last_major_update: str | None
    last_minor_update: str | None

    def last_update(self, include_minor: bool = True) -> str:
        if include_minor:
            return max(
                self.published_date,
                self.last_major_update or "",
                self.last_minor_update or "",
            )
        return max(self.published_date, self.last_major_update or "")


def parse_frontmatter(file: pathlib.Path) -> Tuple[dict[str, Any], str]:
    content = file.read_text(encoding="utf-8")
    if not content.startswith("+++\n"):
        raise SystemExit(f"{file} doesn't start with valid frontmatter")
    content = content.removeprefix("+++\n")
    toml_str, content = content.split("\n+++\n", 2)
    if content is None:
        raise SystemExit(f"{file} doesn't start with valid frontmatter")
    try:
        toml_dict = tomllib.loads(toml_str)
    except tomllib.TOMLDecodeError as err:
        err.args = err.args + (f"{file} doesn't start with valid frontmatter",)
        raise
    return toml_dict, content


# Responsible for:
# * Loading file and parsing frontmatter
# * Rendering markdown content as html
# * Creating a PageData instance and filling in the necessary fields in a
#   normalised form.
def parse_page(file: pathlib.Path) -> PageData:
    metadata, markdown_content = parse_frontmatter(file)
    T = TypeVar("T")

    def fm_get(key: str, ty: type[T]) -> T:
        if key not in metadata:
            raise SystemExit(f"Post {file} missing required frontmatter field '{key}'.")
        val = metadata[key]
        if not isinstance(val, ty):
            raise SystemExit(
                f"Post {file} has unexpected type in frontmatter field '{key}', expected {ty}."
            )
        return val

    def fm_get_opt(key: str, ty: type[T]) -> T | None:
        if key not in metadata:
            return None
        return fm_get(key, ty)

    description = fm_get("description", str)
    published_date = fm_get("published", datetime.date).strftime("%Y-%m-%d")
    permalink = page_path_to_permalink(file)
    hidden = fm_get_opt("hidden", bool) or False
    extra_css = fm_get_opt("extra_css", str) or ""
    path_part = file.parts[1]
    yyyyqq_dir = None
    if (
        len(path_part) == 6
        and path_part[:4].isdigit()
        and path_part[4] == "q"
        and path_part[5].isdigit()
    ):
        yyyyqq_dir = path_part
    (
        markdown_content_as_html,
        title,
        last_major_update,
        last_minor_update,
    ) = render_markdown(markdown_content, file, published_date, yyyyqq_dir)
    return PageData(
        src_path=file,
        yyyyqq_dir=yyyyqq_dir,
        title=title,
        description=description,
        published_date=published_date,
        permalink=permalink,
        markdown_content=markdown_content,
        markdown_content_as_html=markdown_content_as_html,
        hidden=hidden,
        extra_css=extra_css,
        last_major_update=last_major_update,
        last_minor_update=last_minor_update,
    )


def strip_anchor(target: str) -> str:
    return target.split("#")[0]


def check_link_target(target: str, src_file: pathlib.Path) -> None:
    if target.startswith("http://") or target.startswith("https://"):
        return
    if target.startswith("//"):
        raise SystemExit(
            f"Post {src_file} has '//' protocol-relative link '{target}'. Potential typo?"
        )
    if target in ["/", "/feed.xml", "/sitemap.xml", "/robots.txt"]:
        return
    if not target.startswith("/"):
        raise SystemExit(f"Post {src_file} contains relative link '{target}'.")
    if not pathlib.Path(target[1:]).is_file():
        raise SystemExit(f"Post {src_file} links to {target}, which doesn't exit.")
    return


class MuxupRenderer(mistletoe.HTMLRenderer):  # type:ignore
    formatter = HtmlFormatter(style="xcode", noclasses=True, wrapcode=True)

    def __init__(self, *extras):  # type:ignore
        super().__init__(*extras)
        self.heading_slugs = set()

    def render_block_code(self, token: mistletoe.block_token.BlockCode) -> str:
        code = token.children[0].content
        if token.language:
            try:
                lexer = get_lexer(token.language)
            except pygments.util.ClassNotFound:
                lexer = None
            if lexer:
                return highlight(code, lexer, self.formatter)  # type:ignore
        return super().render_block_code(token)  # type:ignore

    def render_heading(self, token: mistletoe.block_token.Heading) -> str:
        template = '<h{level} id="{linkid}"><a href="#{linkid}" class="anchor" aria-hidden="true" tabindex="-1"></a>{inner}</h{level}>'
        inner = self.render_inner(token)
        linkid = re.sub(r"[^a-z0-9-_]", "", inner.lower().replace(" ", "-"))
        unique_linkid = linkid
        i = 1
        while unique_linkid in self.heading_slugs:
            unique_linkid = f"{linkid}-{i}"
            i += 1
        self.heading_slugs.add(unique_linkid)
        return template.format(level=token.level, inner=inner, linkid=unique_linkid)


# Renders markdown to html, applying any necessary checks and transformations
# at the AST level. Also extracts the title (first heading). Returns a tuple
# of (rendered_markdown, title).
def render_markdown(
    content: str, src_file: pathlib.Path, published_date: str, yyyyqq_dir: str | None
) -> tuple[str, str, str | None, str | None]:
    def err(desc: str) -> None:
        raise SystemExit(f"ERROR: {src_file} {desc}")

    def extract_and_remove_article_title(doc: mistletoe.Document) -> str:
        if not doc.children:
            err("document is empty")
        if not isinstance(doc.children[0], mistletoe.block_token.Heading):
            err("document doesn't start with heading")
        if doc.children[0].level != 1:
            err("first heading isn't a top-level ('# Foo') heading")
        h1 = doc.children[0]
        if not h1.children:
            err("title is empty")
        if len(h1.children) > 1 or not isinstance(
            h1.children[0], mistletoe.span_token.RawText
        ):
            err("title isn't plain text")
        title = h1.children[0].content
        del doc.children[0]
        return str(title)

    def check_and_rewrite_links(doc: mistletoe.Document) -> None:
        # Rewrite any /pages/foo.md links to appropriate permalinks.
        for t in mistletoe.utils.traverse(doc, klass=mistletoe.span_token.Link):
            # TODO: check anchor links, including within the current document.
            stripped_target = strip_anchor(t.node.target)
            check_link_target(stripped_target, src_file)
            if stripped_target.startswith("/pages/"):
                t.node.target = page_path_to_permalink(
                    pathlib.Path(stripped_target[1:])
                )

    def process_changelog(
        doc: mistletoe.Document, renderer: MuxupRenderer
    ) -> tuple[str | None, str | None]:
        # Extract changelog info if present.
        changelog_heading = None
        last_major_update = None
        last_minor_update = None
        for t in mistletoe.utils.traverse(doc, klass=mistletoe.block_token.Heading):
            if changelog_heading:
                err("changelog wasn't last heading")
            # TODO: error if changelog heading isn't the last
            if renderer.render_inner(t.node).lower() == "article changelog":
                if t.node.level != 2:
                    err("changelog not a '## Level 2 heading'")
                changelog_heading = t.node
        if not changelog_heading:
            return (last_major_update, last_minor_update)
        changelog_idx = doc.children.index(changelog_heading)
        if len(doc.children) < changelog_idx + 1:
            err("changelog heading has no content")
        if not isinstance(doc.children[changelog_idx + 1], mistletoe.block_token.List):
            err("changelog doesn't have list as first child")
        changelog_list = doc.children[changelog_idx + 1]
        last_li_date = None
        for li in changelog_list.children:
            li_str = renderer.render_inner(li)
            li_date = li_str[3:13]
            if li_date < published_date:
                err("changelog entry predates published date")
            if last_li_date and li_date > last_li_date:
                err("changelog entries out of order")
            last_li_date = li_date
            try:
                datetime.date.fromisoformat(li_date)
            except ValueError:
                err("changelog entry not in expected format")
            if li_str[13:].startswith(": (minor)"):
                last_minor_update = max(last_minor_update or "", li_date)
                li_text_child = li.children[0].children[0]
                li_text_child.content = (
                    li_text_child.content[:11] + li_text_child.content[19:]
                )
            else:
                last_major_update = max(last_major_update or "", li_date)
        changelog_list.children.append(
            mistletoe.Document(f"* {published_date}: Initial publication date.")
            .children[0]
            .children[0]
        )
        doc.children[changelog_idx] = mistletoe.block_token.HTMLBlock(
            '<hr style="margin-top:1.75rem"/><details id="article-changelog"><summary><a href="#article-changelog" class="anchor" aria-hidden="true" tabindex="-1"></a>Article changelog</summary>'
        )
        doc.children.insert(
            changelog_idx + 2, mistletoe.block_token.HTMLBlock("</details>")
        )
        # Add list item for creation of the article.
        return (last_major_update, last_minor_update)

    with MuxupRenderer() as renderer:  # type:ignore
        doc = mistletoe.Document(content)
        title = extract_and_remove_article_title(doc)
        check_and_rewrite_links(doc)
        last_major_update, last_minor_update = process_changelog(doc, renderer)
        markdown_content_as_html = renderer.render(doc)
        if not (yyyyqq_dir or last_major_update or last_minor_update):
            markdown_content_as_html = f"""\
{markdown_content_as_html}
<hr style="margin-top:1.75rem"/><details id="article-changelog"><summary><a href="#article-changelog" class="anchor" aria-hidden="true" tabindex="-1"></a>Article changelog</summary>
<ul>
<li>{published_date}: Initial publication date.</li>
</ul>
</details>"""

        return (markdown_content_as_html, title, last_major_update, last_minor_update)


def generate_gated_css(html_content: str, rules: dict[str, str]) -> str:
    res = []
    for substr, css in rules.items():
        if substr in html_content:
            res.append(css)
    return remove_leading_whitespace("\n".join(res))


def quarter_for_date(d: datetime.date) -> int:
    if d.month <= 3:
        return 1
    elif d.month <= 6:
        return 2
    elif d.month <= 9:
        return 3
    else:
        return 4


def generate_article_meta(pd: PageData) -> str:
    ret = []
    if pd.yyyyqq_dir:
        ret.append(f'<span title="{pd.published_date}">{pd.yyyyqq_dir.upper()}</span>.')
    if pd.last_major_update or pd.last_minor_update:
        update = datetime.date.fromisoformat(pd.last_update())
        today = datetime.date.today()
        days_since = (today - update).days
        if days_since < 30:
            update_formatted = update.strftime("%d %b %Y")
        elif days_since < 90:
            update_formatted = update.strftime("%b %Y")
        else:
            update_formatted = f"{update.year}Q{quarter_for_date(update)}"
        ret.append(
            f'Last update <span title="{pd.last_update()}">{update_formatted}</span>.'
        )
    if not pd.yyyyqq_dir or pd.last_major_update or pd.last_minor_update:
        ret.append(
            """\
<a href="#article-changelog"\
 onclick="document.querySelector('#article-changelog').setAttribute('open', true)">\
History↓</a>"""
        )
    return (" ").join(ret)


def remove_leading_whitespace(string: str) -> str:
    return re.sub(r"(?m)^\s+", "", string)


written_dest_files = set()


@contextmanager
def atomic_write(path: pathlib.Path, binary: bool = False) -> Iterator[typing.IO[Any]]:
    written_dest_files.add(path)
    tmp_path = path.with_name(path.name + "~")
    with open(
        tmp_path, "wb" if binary else "w", encoding=None if binary else "utf-8"
    ) as f:
        yield f
    os.rename(tmp_path, path)


# Core logic

os.chdir(pathlib.Path(__file__).parent)
parser = argparse.ArgumentParser(description="muxup.com static site generator")
parser.add_argument(
    "--serve",
    action="store_true",
    default=False,
    help="serve with simple-reload JS injected, rebuilding upon edit",
)
args = parser.parse_args()

print("Starting rebuild")

dest_path = pathlib.Path("dist")
if not dest_path.exists():
    dest_path.mkdir()

preexisting_dest_files = set()
for dirpath, dirnames, filenames in os.walk(dest_path):
    for fn in filenames:
        preexisting_dest_files.add(pathlib.Path(dirpath) / fn)
    for dn in dirnames:
        child_path = pathlib.Path(dirpath) / dn
        if child_path.is_symlink():
            preexisting_dest_files.add(pathlib.Path(dirpath) / dn)


footer_data_path = pathlib.Path("footer_drawings.json")
footer_data = json.loads(footer_data_path.read_text(encoding="utf-8"))
num_footer_images = len(footer_data)

common_css_frag = remove_leading_whitespace(
    pathlib.Path("fragments/common.css").read_text(encoding="utf-8")
)
article_css_frag = remove_leading_whitespace(
    pathlib.Path("fragments/article.css").read_text(encoding="utf-8")
)
common_js_frag = (
    pathlib.Path("fragments/common.js")
    .read_text(encoding="utf-8")
    .replace("NUM_FOOTER_IMAGES", str(num_footer_images))
)
article_js_frag = pathlib.Path("fragments/article.js").read_text(encoding="utf-8")
minified_article_js = subprocess.run(
    ["terser", "--mangle-props", "--toplevel"],
    input=common_js_frag + article_js_frag,
    capture_output=True,
    check=True,
    encoding="utf-8",
).stdout

# Read all pages leaf pages, parse frontmatter, and generate HTML.
pages_data: list[PageData] = []
pages_path = pathlib.Path("pages")
for file in sorted(pages_path.rglob("*.md")):
    pd = parse_page(file)
    pages_data.append(pd)
    gated_css_frag = generate_gated_css(pd.markdown_content_as_html, gated_css_rules)
    out_path = dest_path / file.relative_to(pages_path).with_suffix(".html")
    if not out_path.parent.exists():
        out_path.parent.mkdir(parents=True)
    with atomic_write(out_path) as o:
        o.write(
            f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta property="og:title" content="{html.escape(pd.title)}"/>
<meta property="og:site_name" content="Muxup">
<meta property="og:description" content="{html.escape(pd.description)}"/>
<meta property="og:type" content="article"/>
<meta property="og:url" content="{base_url}{pd.permalink}"/>
<meta property="og:image" content="https://v1.screenshot.11ty.dev/{urllib.parse.quote_plus(base_url+pd.permalink)}/opengraph/ar/bigger"/>
<meta property="twitter:card" content="summary_large_image">
<meta property="twitter:site" content="@muxup">
<meta property="twitter:creator" content="@asbradbury">
<title>{html.escape(pd.title)} - Muxup</title>
<link rel="icon" sizes="any" href="data:image/svg+xml,{favicon_svg}">
<meta name="description" content="{html.escape(pd.description)}">
<style>
{common_css_frag}{article_css_frag}{gated_css_frag}
{remove_leading_whitespace(pd.extra_css)}</style>
<link rel="alternate" type="application/atom+xml" title="Atom Feed" href="/feed.xml"/>
<link rel="canonical" href="{base_url}{pd.permalink}"/>
</head>
<body>
<div id="article-container">
<div>
<div id="article-logo"><span id="logo-highlight"><a href="/">Muxup</a></span></div>
</div>
<h1 id="article-title"><span id="title-highlight">{html.escape(pd.title)}</span></h1>
<div id="article-meta">{generate_article_meta(pd)}</div>
{pd.markdown_content_as_html}
</div>
{standard_footer}
<script>
{minified_article_js}
</script>
</body>
</html>
"""
        )

# Generate front page.
home_css_frag = pathlib.Path("fragments/home.css").read_text(encoding="utf-8")
home_js_frag = pathlib.Path("fragments/home.js").read_text(encoding="utf-8")
minified_home_js = subprocess.run(
    ["terser", "--mangle-props", "--toplevel"],
    input=common_js_frag + home_js_frag,
    capture_output=True,
    check=True,
    encoding="utf-8",
).stdout
out_path = dest_path / "index.html"
home_html = []
home_html.append(
    f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta property="og:title" content="Muxup"/>
<meta property="og:site_name" content="Muxup">
<meta property="og:description" content="Adventures in collaborative open source development"/>
<meta property="og:type" content="website"/>
<meta property="og:url" content="{base_url}"/>
<meta property="og:image" content="https://v1.screenshot.11ty.dev/{urllib.parse.quote_plus(base_url)}/opengraph/ar/bigger/_{len(pages_data)}"/>
<meta property="twitter:card" content="summary_large_image">
<meta property="twitter:site" content="@muxup">
<meta property="twitter:creator" content="@asbradbury">
<title>Muxup - Adventures in collaborative open source development</title>
<link rel="icon" sizes="any" href="data:image/svg+xml,{favicon_svg}">
<style>
{common_css_frag}{home_css_frag}/* GATED_CSS */
</style>
<link rel="alternate" type="application/atom+xml" title="Atom Feed" href="/feed.xml"/>
<link rel="canonical" href="{base_url}/"/>
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
"""
)
pages_data.sort(key=lambda pd: (pd.last_update(False), pd.permalink), reverse=True)
for pd in filter(lambda pd: not pd.hidden, pages_data):
    home_html.append(
        f"""\
<a class="card" href="{pd.permalink}">
<h2 class="card-title"><span class="highlight-title">{html.escape(pd.title)}</span></h2>
"""
    )
    if pd.yyyyqq_dir:
        home_html.append(f'<p class="card-date">{pd.yyyyqq_dir.upper()}</p>')
    home_html.append(
        f"""\
<p class="card-description">{html.escape(pd.description)}</p>
</a>
"""
    )
home_html.append(
    f"""\
</div>
</div>
{standard_footer}
<script>
{minified_home_js}
</script>
</body>
</html>
"""
)
home_html_str = "".join(home_html)
home_html_str = home_html_str.replace(
    "/* GATED_CSS */", generate_gated_css(home_html_str, gated_css_rules)
)
with atomic_write(out_path) as o:
    o.write(home_html_str)

# Generate robots.txt
out_path = dest_path / "robots.txt"
with atomic_write(out_path) as o:
    o.write(
        f"""\
User-agent: *
Disallow:
Allow: /
Sitemap: {base_url}/sitemap.xml
"""
    )

# Generate sitemap.xml
# Simple iteration over frontmatter in order of last_updated again (but
# unlike front page, by last minor update)
out_path = dest_path / "sitemap.xml"
with atomic_write(out_path) as o:
    o.write(
        """\
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""
    )
    front_page_lastmod = max(pd.last_update(False) for pd in pages_data)
    o.write(
        f"""\
<url>
<loc>{base_url}</loc>
<lastmod>{front_page_lastmod}</lastmod>
</url>
"""
    )
    pages_data.sort(key=lambda pd: (pd.last_update(), pd.permalink), reverse=True)
    for pd in pages_data:
        o.write(
            f"""\
<url>
<loc>{base_url}{pd.permalink}</loc>
<lastmod>{pd.last_update()}</lastmod>
</url>
"""
        )
    o.write("</urlset>\n")

# Generate feed.xml
out_path = dest_path / "feed.xml"
with atomic_write(out_path) as o:
    pages_data.sort(key=lambda pd: (pd.last_update(False), pd.permalink), reverse=True)
    filtered_pages_data = list(filter(lambda pd: not pd.hidden, pages_data))
    o.write(
        f"""\
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="en">
<title>Muxup</title>
<subtitle>Adventures in collaborative open source development</subtitle>
<link href="{base_url}/feed.xml" rel="self" type="application/atom+xml"/>
<link href="{base_url}"/>
<updated>{filtered_pages_data[0].last_update(False)}T12:00:00Z</updated>
<id>{base_url}/feed.xml</id>
"""
    )
    for pd in filtered_pages_data[:10]:
        o.write(
            f"""\
<entry>
<title>{html.escape(pd.title)}</title>
<published>{pd.published_date}T12:00:00Z</published>
<updated>{pd.last_update(False)}T12:00:00Z</updated>
<link rel="alternate" href="{base_url}{pd.permalink}"/>
<id>{base_url}{pd.permalink}</id>
<content type="html">
"""
        )
        o.write(
            html.escape(
                pd.markdown_content_as_html.replace(
                    "href=/", f"href={base_url}/"
                ).replace("src=/", "src={base_url}/")
            )
        )
        o.write(
            """\
</content>
</entry>
"""
        )
    o.write("</feed>\n")

refresh_js = pathlib.Path("fragments/simple-reload.js").read_text(encoding="utf-8")

tmp_static_path = dest_path / "static~"
tmp_static_path.symlink_to("../static")
static_path = dest_path / "static"
tmp_static_path.rename(static_path)
written_dest_files.add(static_path)


files_to_delete = preexisting_dest_files - written_dest_files
for path in files_to_delete:
    print(f"Removing {path} as it wasn't regenerated")
    path.unlink()
for dirpath, dirnames, filenames in os.walk(dest_path, topdown=False):
    for dn in dirnames:
        path = pathlib.Path(dirpath) / dn
        if any(os.scandir(path)):
            continue
        print(f"Removing empty path {path}")
        os.rmdir(pathlib.Path(dirpath) / dn)

print("Rebuild finished")


class MuxupHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path_str = urllib.parse.unquote(urllib.parse.urlparse(self.path).path)[1:]
        if path_str == "":
            path_str = "index.html"
        path = dest_path / path_str
        if not path.is_file() and path.suffix != ".html":
            fallback_path = path.with_name(path.name + ".html")
            if not fallback_path.is_file():
                self.send_error(HTTPStatus.NOT_FOUND, "File not found")
                return
            path = fallback_path
        if ".." in path.parts or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return
        self.send_response(200)
        self.send_header(
            "Content-type", mimetypes.guess_type(path)[0] or "application/octet-stream"
        )
        self.end_headers()
        print(path.suffix)
        if path.suffix in [".html", ".htm"]:
            text = path.read_text()
            text = text.replace(
                "<head>", f'<head><script type="module">{refresh_js}</script>', 1
            )
            self.wfile.write(text.encode())
        else:
            with path.open("rb") as f:
                shutil.copyfileobj(f, self.wfile)


def rebuild_loop() -> None:
    while True:
        paths = (
            list(pathlib.Path("fragments").rglob("*"))
            + list(pages_path.rglob("*"))
            + list(pathlib.Path("static").rglob("*"))
            + [pathlib.Path("build.py")]
        )
        filenames = [str(p) for p in paths if p.is_file()]
        subprocess.run(
            ["entr", "-d", "-p", "./build.py"],
            input="\n".join(filenames),
            encoding="utf-8",
        )


if args.serve:
    print("Launching watcher")
    threading.Thread(target=rebuild_loop, daemon=True).start()
    print("Starting server. See http://localhost:5500")
    try:
        HTTPServer(("localhost", 5500), MuxupHTTPRequestHandler).serve_forever()
    except KeyboardInterrupt:
        print("Ctrl-C received, shutting down server")
        raise SystemExit
