const els = document.querySelectorAll('.highlight-title');
const colors = [ "#ffdef2", "#f2e2ff", "#e2eeff", "#ddfffc", "#ffffe3" ];
let i = 0;
for (const e of els) {
	const hlInfo = annotate(e, e.parentNode, colors[i % colors.length]);
	addRedrawOnMouseover(e.parentNode.parentNode, hlInfo);
	i = i + 1;
}
const e = document.querySelector('#home-logo');
const logoHLInfo = annotate(e, e.parentNode, "#ffdac0");
initAnnotations();
addRedrawOnMouseover(e, logoHLInfo);
