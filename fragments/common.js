const svgNS = "http://www.w3.org/2000/svg"

// Calculate random offset within range of delta and minus delta.
function offset(delta) {
  return (Math.random() * (2*delta)) - delta;
}

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

const blockElToHLInfo = new Map();
let rObserver = new ResizeObserver(entries => {
  for (const e of entries) {
    const hlInfo = blockElToHLInfo.get(e.target);
    if (!hlInfo.nextPathD)
      preparePath(hlInfo);
  }
  for (const e of entries) {
    drawPath(blockElToHLInfo.get(e.target));
  }
})

function createSVG(hlInfo) {
  const svgEl = document.createElementNS(svgNS, "svg");
  svgEl.style.position = "absolute";
  svgEl.style.zIndex = -1;
  svgEl.style.top = "0";
  svgEl.style.left = "0";
  svgEl.style.overflow = "visible";
  const pathEl = document.createElementNS(svgNS, "path");
  pathEl.setAttribute("fill", "none");
  pathEl.setAttribute("stroke", hlInfo.strokeColor);
  svgEl.appendChild(pathEl);
  hlInfo.hlEl.insertAdjacentElement("beforebegin", svgEl);
  hlInfo.svg = svgEl;
}

function drawPath(hlInfo) {
  if (!hlInfo.nextPathD) {
    preparePath(hlInfo);
  }
  const pathEl = hlInfo.svg.children[0];
  pathEl.setAttribute("stroke-width", hlInfo.strokeWidth);
  pathEl.setAttribute("d", hlInfo.nextPathD);
  hlInfo.nextPathD = null;
}

function initAnnotations() {
  // Create SVGs.
  for (const hlInfo of blockElToHLInfo.values()) {
    createSVG(hlInfo);
  }
  // Prepare all paths.
  for (const hlInfo of blockElToHLInfo.values()) {
    preparePath(hlInfo);
  }
  // Drawing will be triggered by ResizeObserver.
  for (const parentBlockEl of blockElToHLInfo.keys()) {
    rObserver.observe(parentBlockEl);
  }
  // Redraw once fonts have loaded.
  document.fonts.ready.then(() => redrawAll());
}

function redrawAll() {
  for (const hlInfo of blockElToHLInfo.values()) {
    preparePath(hlInfo);
  }
  for (const hlInfo of blockElToHLInfo.values()) {
    drawPath(hlInfo);
  }
}

function addRedrawOnMouseover(el, hlInfo) {
  let repeating_cb;
  el.addEventListener("mouseover", () => { drawPath(hlInfo); repeating_cb=setInterval(() => (drawPath(hlInfo)), 240); }, false);
  el.addEventListener("mouseout", () => { clearInterval(repeating_cb);})
  el.addEventListener("click", () => { clearInterval(repeating_cb);})
}

function annotate(hlEl, parentBlockEl, strokeColor) {
  let hlInfo = { hlEl: hlEl, parentBlockEl: parentBlockEl, strokeColor: strokeColor}
  blockElToHLInfo.set(parentBlockEl, hlInfo);
  return hlInfo;
}

let fetchedPaths = new Set([window.location.pathname]);
const footerImage = document.querySelector('#footer-image');
let nextFooterImageSrc = null;
function calcNextFooterImageSrc() {
  let nextFooterImageIdx = Math.floor(Math.random() * NUM_FOOTER_IMAGES);
  nextFooterImageSrc = "/static/footer/" + String(nextFooterImageIdx).padStart(4, "0") + ".svg";
}
function changeFooterImage(noPreload) {
  footerImage.src = nextFooterImageSrc;
  calcNextFooterImageSrc();
  if (!noPreload)
    preloadFooterImage();
}
function preloadFooterImage() {
  if (fetchedPaths.has(nextFooterImageSrc))
    return;
  fetchedPaths.add(nextFooterImageSrc);
  fetch(nextFooterImageSrc);
}
calcNextFooterImageSrc();
changeFooterImage(true);
let footerImageAnimation = null;
footerImage.addEventListener("click", () => {
  // Restart the animation if it completed. WebKit seems to need pause+play.
  if (footerImageAnimation && footerImageAnimation.playState != "running") {
      footerImageAnimation.pause();
      footerImageAnimation.play();
  }
  changeFooterImage();
});
function footerImageMouseOver() {
  const anims = footerImage.getAnimations();
  if (anims.length != 0)
    footerImageAnimation = anims[0];
  preloadFooterImage();
}
footerImage.addEventListener("mouseover", footerImageMouseOver);
footerImage.addEventListener("touchstart", footerImageMouseOver, { passive: true });

function fetchOnMouseOver(event) {
  const destination = event.currentTarget.getAttribute("href").split("#")[0];
  if (fetchedPaths.has(destination))
    return;
  fetchedPaths.add(destination);
  fetch(destination);
}
const links = document.getElementsByTagName('a');
for (const e of links) {
  const destination = (e.getAttribute("href") ?? "").split("#")[0];
  if (destination.includes("?") || !destination.startsWith("/") ||
      destination.slice(destination.lastIndexOf("/") + 1).includes(".")) {
    continue;
  }
  e.addEventListener("mouseover", fetchOnMouseOver);
  e.addEventListener("touchstart", fetchOnMouseOver, { passive: true });
}
