const colors = [ "#ffdef2", "#f2e2ff", "#e2eeff", "#ddfffc", "#ffffe3" ];
const t = document.querySelector('#title-highlight');
annotate(t, t.parentNode, colors[Math.floor(Math.random() * colors.length)]);
const e = document.querySelector('#logo-highlight');
const logoHLInfo = annotate(e, e.parentNode, "#ffdac0");
initAnnotations();
addRedrawOnMouseover(e, logoHLInfo);
