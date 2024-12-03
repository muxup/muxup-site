+++
published = 2022-09-10
description = "Notes on how the Muxup website is built"
+++
# Muxup implementation notes

This article contains a few notes on various implementation decisions made
when creating [the Muxup website](https://muxup.com). They're intended primarily as a
reference for myself, but some parts may be of wider interest. See
[about](/pages/about.md) for more information about things like site
structure.

## Site generation

I ended up writing my own script for generating the site pages from a tree of
Markdown files. [Zola](https://www.getzola.org/) seems like an excellent
option, but as I had a very specific idea on how I wanted pages to be
represented in source form and the format and structure of the output, writing
my own was the easier option (see
[gen](https://github.com/muxup/muxup-site/blob/main/gen)). Plus,
yak-shaving is fun.

I opted to use [mistletoe](https://github.com/miyuchina/mistletoe) for
Markdown parsing. I found [a](https://github.com/miyuchina/mistletoe/pull/157)
[few](https://github.com/miyuchina/mistletoe/pull/158)
[bugs](https://github.com/miyuchina/mistletoe/pull/159) in the `traverse`
helper function when implementing some transformations on the generated AST,
but upstream was very responsive about reviewing and merging my PRs. The main
wart I've found is that [parsing and rendering aren't fully
separated](https://github.com/miyuchina/mistletoe/issues/56), although this
doesn't pose any real practical concern for my use case and will hopefully be
fixed in the future. [mistune](https://github.com/lepture/mistune) also seemed
promising, but has [some conformance
issues](https://github.com/lepture/mistune/issues/296).

One goal was to keep everything possible in standard Markdown format. This
means, for instance, avoiding custom frontmatter entries or link formats if
the same information could be extracted from the file). Therefore:
* There is no `title` frontmatter entry - the title is extracted by grabbing
  the first level 1 heading from the Markdown AST (and erroring if it isn't
  present).
* All internal links are written as `[foo](/relative/to/root/foo.md)`. The
  generator will error if the file can't be found, and will otherwise
  translate the target to refer to the appropriate permalink.
  * This has the additional advantage that links are still usable if viewing
    the Markdown on GitHub, which can be handy if reviewing a previous
    revision of an article.
* Article changelogs are just a standard Markdown list under the "Article
  changelog" heading, which is checked and transformed at the Markdown AST
  level in order to produce the desired output (emitting the list using a
  `<details>` and `<summary>`).

All CSS was written through the usual mix of experimentation (see
[simple-reload](/pages/simple-reload.md) for the page reloading solution I
used to aid iterative development) and learning from the CSS used by other
sites.

## Randomly generated title highlights

The main visual element throughout the site is the randomised, roughly drawn
highlight used for the site name and article headings. This takes some
inspiration from the [RoughNotation library](https://roughnotation.com/) (see
also the [author's description of the algorithms
used](https://shihn.ca/posts/2020/roughjs-algorithms/)), but uses my own
implementation that's much more tightly linked to my use case.

The core logic for drawing these highlights is based around drawing the SVG
path:
* Determine the position and size of the text element to be highlight (keeping
  in mind it might be described by multiple rectangles if split across several
  lines).
* For each rectangle, draw a bezier curve starting from the middle of the left
  hand side through to the right hand side, with its two control points at
  between 20-40% and 40-80% of the width.
* Apply randomised offsets in the x and y directions for every point.
  * The range of the randomised offsets should depend on length of the text.
    Generally speaking, a smaller offsets should be used for a shorter piece
    of text.

This logic is implemented in 
[`preparePath`](https://github.com/muxup/muxup-site/blob/main/fragments/common.js)
and reproduced below (with the knowledge the `offset(delta)` is a helper to
return a random number between `delta` and `-delta`, hopefully it's clear how
this relates to the logic described above):

```js
function preparePath(hlInfo) {
  const parentRect = hlInfo.svg.getBoundingClientRect();
  const rects = hlInfo.hlEl.getClientRects();
  let pathD = "";
  for (const rect of rects) {
    const x = rect.x - parentRect.x, y = rect.y - parentRect.y,
          w = rect.width, h = rect.height;
    const mid_y = y + h / 2;
    let maxOff = w < 75 ? 3 : w < 300 ? 6 : 8;
    const divergePoint = .2 + .2 * Math.random();
    pathD = `${pathD}
      M${x+offset(maxOff)} ${mid_y+offset(maxOff)}
      C${x+w*divergePoint+offset(maxOff)} ${mid_y+offset(maxOff)},
       ${x+2*w*divergePoint+offset(maxOff)} ${mid_y+offset(maxOff)}
       ${x+w+offset(maxOff)} ${mid_y+offset(maxOff)}`;
  }
  hlInfo.nextPathD = pathD;
  hlInfo.strokeWidth = 0.85*rects[0].height;
}
```

I took some care to avoid [forced
layout/reflow](https://gist.github.com/paulirish/5d52fb081b3570c81e3a) by
batching together reads and writes of the DOM into separate phases when
drawing the initial set of highlights for the page, which is why this function
is generates the path but doesn't modify the SVG directly. Separate logic adds
handlers to links that are highlighted continuously redraw the highlight (I
liked the visual effect).

## Minification and optimisation

I primarily targeted the low-hanging fruit here, and avoided adding in too
many dependencies (e.g. separate HTML and CSS minifiers) during the build.
muxup.com is a very lightweight site - the main extravagance I've allowed
myself is the use of a webfont (Nunito) but that only weighs in at ~36KiB (the
[variable
width](https://github.com/googlefonts/nunito/tree/main/fonts/variable) version
converted to woff2 and subsetted using `pyftsubset` from
[fontTools](https://github.com/fonttools/fonttools)). As the CSS and JS
payload is so small, it's inlined into each page.

The required JS for the article pages and the home page is assembled and then
minified using [terser](https://github.com/terser/terser). This reduces the
size of the JS required for the page you're reading from 5077 bytes to 2620
bytes uncompressed (1450 bytes to 991 bytes if compressing the result with
Brotli, though in practice the impact will be a bit different when compressing
the JS together with the rest of the page + CSS). When first published, the
page you are reading (including inlined CSS and JS) was ~27.7KiB uncompressed
(7.7KiB Brotli compressed), which compares to 14.4KiB for its source Markdown
(4.9KiB Brotli compressed).

Each page contains an embedded stylesheet with a conservative approximation of
the minimal CSS needed. The total amount of CSS is small enough that it's easy
to manually split between the CSS that is common across the site, the CSS only
needed for the home page, the CSS common to all articles, and then other CSS
rules that may or may not be needed depending on the page content. For the
latter case, CSS snippets to include are gated on matching a given string
(e.g. `<kbd` for use of the `<kbd>` tag). For my particular use case, this is
more straight forward and faster than e.g. relying on
[PurgeCSS](https://purgecss.com/) as part of the build process.

The final trick on the frontend is prefetching. Upon hovering on an internal
link, it will be fetched (see the logic at the end of
[common.js](https://github.com/muxup/muxup-site/blob/main/fragments/common.js)
for the implementation approach), meaning that in the common case any link you
click will already have been loaded and cached. More complex approaches could
be used to e.g. hook the mouse click event and directly update the DOM
using the retrieved data. But this would require work to provide UI feedback
during the load and the incremental benefit over prefetching to prime the
cache seems small.

## Serving using Caddy

I had a few goals in setting up [Caddy](https://caddyserver.com/) to serve
this site:
* Enable new and shiny things like HTTP3 and serving Brotli compressed
  content.
  * Both are very widely supported on the browser side (and Brotli really
    isn't "new" any more), but require non-standard modules or custom builds
    on Nginx.
* Redirect `wwww.muxup.com/*` URLs to `muxup.com/*`.
* HTTP request methods other than `GET` or `HEAD` should return error 405.
* Set appropriate [Cache-Control
  headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control)
  in order to avoid unnecessary re-fetching content. Set shorter lifetimes for
  served .html and 308 redirects vs other assets. Leave 404 responses with
  no Cache-Control header.
* Avoid serving the same content at multiple URLs (unless explicitly asked
  for) and don't expose the internal filenames of content served via a
  different canonical URL. Also, prefer URLs without a trailing slash, but
  ensure not to issue a redirect if the target file doesn't exist. This
  means (for example):
    * `muxup.com/about/` should redirect to `muxup.com/about`
    * `muxup.com/2022q3////muxup-implementation-notes` should 404 or redirect.
    * `muxup.com/about/./././` should 404 or redirect
    * `muxup.com/index.html` should 404.
    * `muxup.com/index.html.br` (referring to the precompressed brotli file)
      should 404.
    * `muxup.com/non-existing-path/` should 404.
  * If there is a directory `foo` and a `foo.html` at the same level, serve
    `foo.html` for `GET /foo` (and redirect to it for `GET /foo/`).
* Never try to serve `*/index.html` or similar (except in the special case of
  `GET /`).

Perhaps because my requirements were so specific, this turned out to be a
little more involved than I expected. If seeking to understand the `Caddyfile`
format and Caddy configuration in general, I'd strongly recommend getting a
good understanding of the key ideas by reading [Caddyfile
concepts](https://caddyserver.com/docs/caddyfile/concepts), understanding [the
order in which directives are handled by
default](https://caddyserver.com/docs/caddyfile/directives#directive-order)
and how you might control the execution order of directives using the
[route](https://caddyserver.com/docs/caddyfile/directives/route) directive or
use the [handle](https://caddyserver.com/docs/caddyfile/directives/handle)
directive to specify groups of directives in a mutually exclusive fashion
based on different matchers. The [Composing in the
Caddyfile](https://caddy.community/t/composing-in-the-caddyfile/8291) article
provides a good discussion of these options).

Ultimately, I [wrote a quick test
script](https://github.com/muxup/muxup-site/blob/main/utils/server_test.sh)
for the desired properties and came up with the following Caddyfile that meets
almost all goals:

```
{
	servers {
		protocol {
			experimental_http3
		}
	}
	email asb@asbradbury.org
}

(muxup_file_server) {
	file_server {
		index ""
		precompressed br
		disable_canonical_uris
	}
}
www.muxup.com {
	redir https://muxup.com{uri} 308
	header Cache-Control "max-age=2592000, stale-while-revalidate=2592000"
}
muxup.com {
	root * /var/www/muxup.com/htdocs
	encode gzip
	log {
		output file /var/log/caddy/muxup.com.access.log
	}
	header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"

	vars short_cache_control "max-age=3600"
	vars long_cache_control "max-age=2592000, stale-while-revalidate=2592000"

	@method_isnt_GET_or_HEAD not method GET HEAD
	@path_is_suffixed_with_html_or_br path *.html *.html/ *.br *.br/
	@path_or_html_suffixed_path_exists file {path}.html {path}
	@html_suffixed_path_exists file {path}.html
	@path_or_html_suffixed_path_doesnt_exist not file {path}.html {path}
	@path_is_root path /
	@path_has_trailing_slash path_regexp ^/(.*)/$

	handle @method_isnt_GET_or_HEAD {
		error 405
	}
	handle @path_is_suffixed_with_html_or_br {
		error 404
	}
	handle @path_has_trailing_slash {
		route {
			uri strip_suffix /
			header @path_or_html_suffixed_path_exists Cache-Control "{vars.long_cache_control}"
			redir @path_or_html_suffixed_path_exists {path} 308
			error @path_or_html_suffixed_path_doesnt_exist 404
		}
	}
	handle @path_is_root {
		rewrite index.html
		header Cache-Control "{vars.short_cache_control}"
		import muxup_file_server
	}
	handle @html_suffixed_path_exists {
		rewrite {path}.html
		header Cache-Control "{vars.short_cache_control}"
		import muxup_file_server
	}
	handle * {
		header Cache-Control "{vars.long_cache_control}"
		import muxup_file_server
	}
	handle_errors {
		header -Cache-Control
		respond "{err.status_code} {err.status_text}"
	}
}
```

A few notes on the above:
* It isn't currently possible to match URLs with `//` due to the
  canonicalisation Caddy performs, but 2.6.0 including
  [PR #4948](https://github.com/caddyserver/caddy/pull/4948) hopefully
  provides a solution. Hopefully to allow matching `/./` too.
* HTTP3 should [enabled by
  default](https://github.com/caddyserver/caddy/pull/4707) in Caddy 2.6.0.
* Surprisingly, you need to explicitly opt in to enabling gzip compression
  (see [this discussion](https://news.ycombinator.com/item?id=32769612) with
  the author of Caddy about that choice).
* The combination of `try_files` and `file_server` provides a large chunk of
  the basics, but something like the above handlers is needed to get the
  precise desired behaviour for things like redirects, `*.html` and `*.br`
  etc.
* `route` is needed within `handle @path_has_trailing_slash` because the
  default execution order of directives has `uri` occurring some time after
  `redir` and `error`.
* Caddy doesn't support dynamically brotli compressing responses, so the
  `precompressed br` option of `file_server` is used to serve pre-compressed
  files (as prepared during deployment)
* I've [asked for
  advice](https://caddy.community/t/suggestions-for-simplifying-my-caddyfile/17135)
  on improving the above Caddyfile on the Caddy Discourse.

## Analytics

The simplest possible solution - don't have any.

## Footer images

Last but by no means least, is the randomly selected doodle at the bottom of
each page. I select images from the [Quick, Draw!
dataset](https://github.com/googlecreativelab/quickdraw-dataset) and export
them to SVG to be randomly selected on each page load. A rather [scrappy
script](https://github.com/muxup/muxup-site/blob/main/utils/footer_image_helper.py)
contains logic to generate SVGs from the dataset's NDJSON format and contains
a simple a Flask application that allows selecting desired images from
randomly displayed batches from each dataset.

With examples such as O'Reilly's beautiful [engravings of
animals](https://www.oreilly.com/content/a-short-history-of-the-oreilly-animals/)
on their book covers there's a well established tradition of animal
illustrations on technical content - and what better way to honour that
tradition than with a hastily drawn doodle by a random person on the internet
that spins when your mouse hovers over it?

## Article changelog
* 2024-12-03: (minor) Fix links that were broken after site generator
  refactoring.
* 2022-09-11: (minor) Add HSTS, tweak no-www redirect, and reject HTTP methods
  other than GET or POST in Caddyfile. Also link to thread requesting
  suggestions for this Caddyfile on Caddy's Discourse.
