const colors = [ "#ffdef2", "#f2e2ff", "#e2eeff", "#ddfffc", "#ffffe3" ];
const t = document.querySelector('#title-highlight');
annotate(t, t.parentNode, colors[Math.floor(Math.random() * colors.length)]);
const e = document.querySelector('#logo-highlight');
const logoHLInfo = annotate(e, e.parentNode, "#ffdac0");
initAnnotations();
addRedrawOnMouseover(e, logoHLInfo);
document.querySelectorAll('pre:has(code)').forEach(preEl => {
  let clickCount = 0, lastClickTime = 0, lastClickedElement = null;
  preEl.addEventListener('click', (event) => {
    const now = Date.now();
    if (event.target !== lastClickedElement || now - lastClickTime >= 500) {
      clickCount = 1;
    } else {
      clickCount++;
    }
    if (clickCount === 4) {
      window.getSelection().selectAllChildren(preEl);
      clickCount = 0;
    }
    lastClickedElement = event.target;
    lastClickTime = now;
  });
});
