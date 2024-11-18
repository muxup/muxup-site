@font-face {
font-family:'Nunito Var';
src:url('/static/Nunito.var.v2.woff2') format('woff2-variations');
font-display:swap;
font-weight: 200 1000;
}
*, *::before, *::after {
box-sizing:border-box;
}
* {
margin:0;
}
input, button, textarea, select {
font:inherit;
}
img, picture, video, canvas, svg {
display:block;
max-width:100%;
}
html {
font-family:'Nunito Var', sans-serif;
height:100%;
font-size:16px;
-webkit-tap-highlight-color:transparent;
}
@media screen and (min-width:640px) {
html {
font-size:18px;
}
}
body {
line-height:1.5;
color:#222;
display:grid;
height:100%;
grid-template-rows:1fr auto;
background:#fff no-repeat 0% 0% / 100% .7rem linear-gradient(120deg, #ffffe3 20%, #ddfffc 20%, #ddfffc 40%, #e2eeff 40%, #e2eeff 60%, #f2e2ff 60%, #f2e2ff 80%, #ffdef2 80%, #ffdef2 100%);
tab-size:4;
}
h1, h2, h3, h4, h5, h6 {
line-height:1.25;
font-weight:600;
overflow-wrap:break-word;
letter-spacing:-.025em;
margin:1.75rem 0 .75rem;
}
h1 {
font-size:2.986rem
}
h2 {
font-size:2.488rem
}
p {
margin:.75rem 0;
font-weight:400;
overflow-wrap:break-word;
}
a {
color:inherit;
text-decoration:underline;
text-decoration-color:#aaa;
text-underline-offset:.15em;
}
a:hover {
text-decoration-thickness:2px;
}
ol, ul {
margin:0 0 0 1.5rem;
padding-left:0;
}
li {
margin:0 0 .25rem
}
::selection {
background:#ffdac0;
}
footer {
font-size:.833rem;
color:#777;
padding:0 1rem;
width:100%;
max-width:min(calc(750px + 2rem), calc(100vw - 1rem));
margin:0 auto;
}
footer p {
text-align:center;
margin:0 0 .75rem;
}
#footer-image {
margin:0 auto;
cursor:pointer;
}
$ if page_type == "home"
#home-container {
margin:0 auto;
padding:1rem;
max-width:min(calc(1110px + 2rem), calc(100vw - 1rem));
width:100%;
}
#hero {
position:relative;
margin:2.5rem 0;
}
#home-logo {
font-weight:700;
}
#home-logo a {
text-decoration:none;
}
.subtitle {
margin-top:-.75rem;
line-height:1.25;
font-size:2.074rem;
color:#555;
letter-spacing:-.025em;
}
.card-grid {
display:grid;
gap:.75rem;
margin:0 -1rem;
}
@media screen and (min-width:640px) {
.card-grid {
grid-auto-rows:1fr;
grid-template-columns:repeat(auto-fill,minmax(320px,1fr))
}
}
.card {
position:relative;
padding:.25rem 1rem 1rem 1rem;
border-radius:.25rem;
box-shadow:0 2px 6px rgba(0, 0, 0, .07)
}
.card:hover {
box-shadow:0 2px 6px rgba(0, 0, 0, .12)
}
a.card {
text-decoration:none;
}
.card-title {
font-size:1.2rem;
margin:.5rem 0 .1rem;
}
.card-date {
position:absolute;
bottom:0;
right:0;
margin:0;
font-size:.694rem;
color:#777;
}
.card-description {
margin:0;
}
$ elif page_type == "article"
#article-logo {
line-height:1.25;
margin:.5rem 0 0;
font-size:1.44rem;
font-weight:700;
position:relative;
}
#article-logo a {
text-decoration:none;
}
#article-title {
margin:1.5rem 0 0;
position:relative;
}
#article-meta {
font-size:.833rem;
color:#777;
}
#article-container {
margin:0 auto;
padding:1rem;
max-width:min(calc(750px + 2rem), calc(100vw - 1rem));
width:100%;
}
.anchor {
position: absolute;
text-decoration: none;
width:1.75ex;
margin-left:-1.4ex;
visibility:hidden;
font-size:.8em;
padding-top:.2em;
color:#aaa;
}
h2:hover .anchor,
h3:hover .anchor,
h4:hover .anchor,
h5:hover .anchor,
h6:hover .anchor,
summary:hover .anchor {
visibility:visible;
}
.anchor::before {
content:"#";
}
$ endif
$ if "<h3" in target_html
h3 {
font-size:2.074rem
}
$ endif
$ if "<h4" in target_html
h4 {
font-size:1.728rem
}
$ endif
$ if "<h5" in target_html
h5 {
font-size:1.44rem
}
$ endif
$ if "<h6" in target_html
h6 {
font-size:1.2rem
}
$ endif
$ if "<small" in target_html
small {
font-size:.833rem
}
$ endif
$ if "<mark" in target_html
mark {
background:#fff474
}
$ endif
$ if "<blockquote" in target_html
blockquote {
margin:1rem 0;
padding:0 0.8rem;
border-inline-start:4px solid #dadee4;
}
$ endif
$ if "<hr" in target_html
hr {
border:none;
border-top:4px solid #f1f3f5;
}
$ endif
$ if "<code" in target_html
code {
background:#f5f5f5;
padding:.125rem .25rem;
font-size:.833rem
}
$ endif
$ if "<pre" in target_html
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
}
$ endif
$ if "<table" in target_html
table {
border-spacing:.75rem 0;
text-align:left;
width:100%;
margin:0 0 1.5rem 0;
}
td, th {
border-bottom:.05rem solid #dadee4;
padding:.6rem 0;
}
$ endif
$ if "<kbd" in target_html
kbd {
background:#212529;
border-radius:.2rem;
color:#fff;
font-size:.85em;
font-weight:700;
line-height:1;
padding:2px 4px;
white-space:nowrap;
}
$ endif
$ if "<details" in target_html
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
$ endif
$ if extra_css
{{extra_css.rstrip()}}
$ endif
