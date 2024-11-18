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
