// pocket-familiar web card: one render path, three motifs (analog, cyberpunk, y2k-blog).
// Everything the user wrote (notes, lines, names) goes in through textContent, never as HTML.
const SAMPLE = { name: "Lucky", state: "fed", reason: "just ate", details: [], line: "Lucky is fed and purring.",
  streak: 1, hunger: 0, feeds: [], totals: {}, watch: { label: "Shipped this month", value: 0 },
  week: "", table: "01", generated: "", total: 0, motif: "analog" };
const d = DATA || SAMPLE;
const MOTIFS = ["analog", "cyberpunk", "y2k-blog"];
const MOTIF = MOTIFS.includes(d.motif) ? d.motif : "analog";
const GUESTBOOK = "https://github.com/RochaStone/pocket-familiar/issues";

// ---- style.json: palette, fonts and lines (checked in style.py: hex colours, plain font names)
const ST = d.style || {};
const PAL = Object.assign({ hero: "#50163C", accent: "#FE9DCA", paper: "#FFF7F4", paper_pink: "#FFE3F1",
  ink: "#3B1230", marker: "#C2246E", plum: "#50163C", wine: "#682047", gold: "#E9B949", cool: "#B9B3F5" }, ST.palette || {});
if (!(ST.palette || {}).wine) PAL.wine = PAL.plum;   // older style files have no wine: use plum
const FONTS = Object.assign({ masthead: "Fraunces", label: "Bricolage Grotesque", body: "Fraunces",
  scrawl: "Permanent Marker", mono: "DM Mono", pixel: "Silkscreen" }, ST.fonts || {});
const LINES = Object.assign({ todo: "", celebrate: "", affirm: "" }, ST.lines || {});
(function applyStyle() {
  const root = document.documentElement.style;
  const map = { ground: "hero", candy: "accent", cream: "paper", blush: "paper_pink", ink: "ink",
    magenta: "marker", plum: "plum", wine: "wine", gold: "gold" };   // hero is the ground, not an accent
  Object.entries(map).forEach(([v, k]) => root.setProperty("--" + v, PAL[k]));
  const stacks = { serif: ["masthead", "Georgia, serif"], label: ["label", "system-ui, sans-serif"],
    body: ["body", "Georgia, serif"], mono: ["mono", "ui-monospace, Menlo, monospace"],
    marker: ["scrawl", "'Marker Felt', cursive"], pixel: ["pixel", "'Pixelify Sans', ui-monospace, monospace"] };
  Object.entries(stacks).forEach(([v, [k, fb]]) => root.setProperty("--" + v, `"${FONTS[k]}", ${fb}`));
  const axes = { masthead: ":wght@900", label: ":wght@400;800", body: ":ital,wght@0,400;1,400", mono: ":wght@400;500",
    scrawl: "", pixel: ":wght@400;700" };
  const families = Object.entries(axes).map(([k, ax]) => [FONTS[k], ax]).concat([["Pixelify Sans", ""]]);
  families.forEach(([fam, ax]) => [ax, ""].forEach(a => {   // one link per font, so one unknown font cannot break the rest
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "https://fonts.googleapis.com/css2?family=" + encodeURIComponent(fam).replace(/%20/g, "+") + a + "&display=swap";
    document.head.appendChild(link);
  }));
})();

// ---- the leopard, drawn from shapes on a 32 x 32 grid, then outlined in ink on every edge.
// Fur = accent, rosettes = hero, muzzle and belly = paper_pink, grill = gold with white diamonds.
const N = 32;
function drawLeopard(state, pose) {
  const g = Array.from({ length: N }, () => Array(N).fill(null));
  const part = Array.from({ length: N }, () => Array(N).fill(""));
  const inside = (x, y) => x >= 0 && y >= 0 && x < N && y < N;
  const set = (x, y, c, p) => { if (inside(x, y)) { g[y][x] = c; if (p) part[y][x] = p; } };
  const ellipse = (cx, cy, rx, ry, c, p) => {
    for (let y = Math.floor(cy - ry); y <= Math.ceil(cy + ry); y++)
      for (let x = Math.floor(cx - rx); x <= Math.ceil(cx + rx); x++)
        if (((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1) set(x, y, c, p);
  };
  const limb = (pts, r, c, p) => {       // a thick line through points, for arms and tail
    for (let i = 0; i < pts.length - 1; i++) {
      const [x0, y0] = pts[i], [x1, y1] = pts[i + 1];
      const steps = Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0)) * 2 || 1;
      for (let s = 0; s <= steps; s++) ellipse(x0 + (x1 - x0) * s / steps, y0 + (y1 - y0) * s / steps, r, r, c, p);
    }
  };
  const up = state === "celebrating";
  // tail behind the body (restless gets a second pose, swapped by CSS)
  const tails = { rest: [[23, 28], [27, 28], [29.5, 25.5], [29, 22], [26.5, 21]], flick: [[23, 28], [27, 28], [30, 26], [31, 22], [30, 19]] };   // curled, her signature
  limb(tails[pose || "rest"], 1.1, "A", "tail");
  // body, sitting
  ellipse(16, 24.5, 7.6, 6.2, "A", "body");
  ellipse(16, 25.5, 3.6, 4, "P", "body");             // belly
  // arms: down by the paws, or up in the air
  if (up) {
    limb([[9, 22], [4, 18], [2.5, 12]], 1.1, "A", "arm");
    limb([[23, 22], [28, 18], [29.5, 12]], 1.1, "A", "arm");
    ellipse(2.5, 11, 1.6, 1.6, "A", "arm"); ellipse(29.5, 11, 1.6, 1.6, "A", "arm");
  } else {
    ellipse(12.5, 29.6, 2.2, 1.4, "A", "arm"); ellipse(19.5, 29.6, 2.2, 1.4, "A", "arm");   // front paws
  }
  // ears: small and round, with a darker inner ear
  ellipse(8.5, 5.5, 2.6, 2.6, "A", "ear"); ellipse(23.5, 5.5, 2.6, 2.6, "A", "ear");
  set(8, 5, "H"); set(9, 5, "H"); set(8, 6, "H"); set(23, 5, "H"); set(24, 5, "H"); set(24, 6, "H");
  // head
  ellipse(16, 12, 9.6, 7.6, "A", "head");
  ellipse(16, 16, 4.6, 2.8, "P", "head");             // muzzle
  // rosettes: broken rings of hero pink around a fur centre, each ring missing a different side
  // rosettes: a broken wine ring around a darker fur centre (two tones read as leopard, not as dots)
  const RING = [[-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0]];
  const ros = [[9, 7, 0], [16, 5, 2], [23, 7, 5], [7, 13, 3], [25, 13, 6], [11, 21, 1], [21, 21, 4], [9, 26, 7], [23, 26, 2]];
  ros.forEach(([x, y, gap]) => {
    if (inside(x, y) && g[y][x] === "A") set(x, y, "M");
    RING.forEach(([dx, dy], i) => {
      if (i === gap) return;   // one gap, so each ring reads as a rosette
      if (inside(x + dx, y + dy) && g[y + dy][x + dx] === "A") set(x + dx, y + dy, "H");
    });
  });
  // nose
  set(15, 14, "H"); set(16, 14, "H"); set(15, 15, "K"); set(16, 15, "K");
  // mouth and grill: four white diamonds on a gold bar, lips in ink
  const open = state === "hungry";
  for (let x = 12; x <= 19; x++) { set(x, 16, "K"); set(x, 18, "K"); }
  ["K", "W", "G", "W", "G", "W", "G", "W"].forEach((c, i) => set(12 + i, 17, c));
  set(19, 17, "K");
  set(14, 17, "S");   // the grill's shine: one bright gold pixel, always there
  if (open) { for (let x = 13; x <= 18; x++) { set(x, 18, "R"); set(x, 19, "K"); } set(12, 18, "K"); set(19, 18, "K"); }
  // eyes, per mood: 4 wide, 3 tall, so she can really look at you
  const E = {
    fed:         [".KK.", "K..K", "...."],          // content: closed and smiling
    celebrating: ["WKKK", "KKKW", "KKKK"],          // big and bright
    hungry:      ["WKKK", "KKKK", "KKKW"],          // big, looking up at the snack
    sleepy:      ["....", "KKKK", ".GK."],          // heavy lid, gold showing below
    asleep:      ["....", "K..K", ".KK."],          // closed
    worried:     ["WWWW", "WKKW", "WWWW"],          // wide, tiny pupils
    restless:    ["KKKK", "WWKK", "WWKK"]           // side-eye
  }[state] || [];
  [[9, 9], [19, 9]].forEach(([ex, ey]) => E.forEach((row, dy) => [...row].forEach((c, dx) => { if (c !== ".") set(ex + dx, ey + dy, c); })));
  if (state === "worried") [[9, 9], [19, 9]].forEach(([ex, ey]) => {   // ink ring around wide eyes
    for (let dx = -1; dx <= 4; dx++) for (let dy = -1; dy <= 3; dy++)
      if ((dx < 0 || dx > 3 || dy < 0 || dy > 2) && inside(ex + dx, ey + dy) && g[ey + dy][ex + dx] === "A") set(ex + dx, ey + dy, "K");
  });
  // ink outline on every outer edge, and a neck line where the head meets the body
  const filled = (x, y) => inside(x, y) && g[y][x] !== null;
  const ink = [];
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
    if (g[y][x] === null && [[1, 0], [-1, 0], [0, 1], [0, -1]].some(([dx, dy]) => filled(x + dx, y + dy))) ink.push([x, y]);
    if (part[y][x] === "body" && g[y][x] === "A" && inside(x, y - 1) && part[y - 1][x] === "head") ink.push([x, y]);
    if (part[y][x] === "arm" && g[y][x] === "A" && [[1, 0], [-1, 0], [0, -1], [0, 1]].some(([dx, dy]) => inside(x + dx, y + dy) && ["body", "head", "tail"].includes(part[y + dy][x + dx]))) ink.push([x, y]);
  }
  ink.forEach(([x, y]) => set(x, y, "K"));
  return g;
}
function mixHex(a, b, t) {   // blend two hex colours, t = 0..1
  const p = x => [1, 3, 5].map(i => parseInt(x.length === 4 ? x[Math.ceil(i / 2)].repeat(2) : x.slice(i, i + 2), 16));
  const [ra, rb] = [p(a), p(b)];
  return "#" + ra.map((v, i) => Math.round(v + (rb[i] - v) * t).toString(16).padStart(2, "0")).join("");
}
const PIX = () => ({ K: PAL.ink, A: PAL.accent, H: PAL.wine, M: mixHex(PAL.accent, PAL.wine, .3), P: PAL.paper_pink,
  S: mixHex(PAL.gold, "#FFFFFF", .6), W: "#FFFFFF", G: PAL.gold, R: PAL.marker });
function petSvg(state) {   // returns SVG markup built only from our own numbers and palette
  const colours = PIX();
  const svgPx = g => g.map((row, y) => row.map((c, x) => c ? `<rect x="${x}" y="${y}" width="1.02" height="1.02" fill="${colours[c]}"/>` : "").join("")).join("");
  let out = state === "restless"   // tail flick: two poses, swapped by CSS
    ? `<g class="pet"><g class="pose-a">${svgPx(drawLeopard(state, "rest"))}</g><g class="pose-b">${svgPx(drawLeopard(state, "flick"))}</g></g>`
    : `<g class="pet">${svgPx(drawLeopard(state))}</g>`;
  const star = (x, y, s, cls) => `<path class="glint ${cls}" fill="#FFFFFF" stroke="${PAL.gold}" stroke-width=".2" d="M${x} ${y - s}L${x + s * .3} ${y - s * .3}L${x + s} ${y}L${x + s * .3} ${y + s * .3}L${x} ${y + s}L${x - s * .3} ${y + s * .3}L${x - s} ${y}L${x - s * .3} ${y - s * .3}Z"/>`;
  if (state === "celebrating") out += star(13.5, 17.5, 1.6, "grill") + star(17.5, 17.5, 1.2, "grill two");
  const text = (x, y, t, size, color) => `<text x="${x}" y="${y}" font-family="${FONTS.mono}, monospace" font-weight="500" font-size="${size}" fill="${color}">${t}</text>`;
  if (state === "asleep" || state === "sleepy") out += text(25, 4, "z", 3.4, PAL.plum) + text(28, 1, "Z", 4.2, PAL.plum);
  if (state === "worried") out += `<path d="M28 4 Q26.4 7 28 8 Q29.6 7 28 4Z" fill="${PAL.paper}" stroke="${PAL.ink}" stroke-width=".4"/>`;
  if (state === "celebrating") out += star(2, 6, 1.8, "") + star(30, 5, 2, "two") + star(29, 18, 1.4, "") + star(3, 20, 1.3, "two") + star(16, 1, 1.2, "");
  return `<svg class="pet-svg" viewBox="-1 -2 34 34" role="img" aria-label="Pixel leopard, ${state}">${out}</svg>`;
}


// ---- small DOM builder: h("div.class", child, child...). Strings become text nodes.
function h(spec, ...kids) {
  const [tag, ...cls] = spec.split(".");
  const n = document.createElement(tag || "div");
  if (cls.length) n.className = cls.join(" ");
  kids.flat().forEach(k => { if (k === null || k === undefined || k === false) return; n.append(k instanceof Node ? k : String(k)); });
  return n;
}
// Two renderings of one mood: painted (analog, y2k-blog) and pixel (cyberpunk, terminal, status line).
// Both are our own SVG, built from numbers and the checked palette, never from anything she typed.
function pet(cls, style) {
  const box = h("div." + cls);
  box.innerHTML = style === "painted" && d.painted ? d.painted : petSvg(d.state);
  return box;
}
const FED = 100 - Math.max(0, Math.min(100, d.hunger));   // full bar = fed
const celebrating = d.state === "celebrating";
function blocks(n = 10) {   // a meter made of blocks
  const on = Math.round(FED / 100 * n);
  return h("span.blocks", ...Array.from({ length: n }, (_, i) => h(i < on ? "i.on" : "i")));
}
function whyList() { return d.details && d.details.length ? h("ul", ...d.details.map(x => h("li", "· " + x))) : null; }
function totalsRows() {
  return Object.entries(d.totals).filter(([, v]) => v).map(([k, v]) => [k, "x" + v])
    .concat([["tax", "0 tokens"], ["total", d.feeds.length + " feeds"]]);
}
const toast = h("div.toast"); toast.setAttribute("role", "status"); toast.setAttribute("aria-live", "polite");
function say(msg) { toast.textContent = msg; }
function fallbackCopy(text) {
  const ta = h("textarea"); ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
  document.body.appendChild(ta); ta.select();
  let ok = false;
  try { ok = document.execCommand("copy"); } catch (err) { say("Copy did not work here (" + err.message + "). Type: " + text); }
  document.body.removeChild(ta);
  return ok;
}
function feedButtons(cls) {
  return ["shipped", "sent", "invoiced", "rested", "closed"].map(k => {
    const b = h("button." + cls, k);
    b.type = "button";
    b.addEventListener("click", () => {
      const cmd = `familiar feed ${k} ""`;
      const done = () => say("Copied: " + cmd + "  Paste it in your terminal.");
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(cmd).then(done, err => { if (fallbackCopy(cmd)) done(); else say("Copy blocked (" + err.message + "). Type: " + cmd); });
      } else if (fallbackCopy(cmd)) { done(); } else { say("Type this in your terminal: " + cmd); }
    });
    return b;
  });
}
const FEED_HELP = "Feeding happens in your terminal. Tap a dish to copy the command, then paste it there and add a note.";
const footLine = () => ["pocket-familiar", [ST.owner, ST.handle].filter(Boolean).join(" "), d.generated ? "printed " + d.generated : ""].filter(Boolean).join(" · ");
function fitOneLine(node, start, min) {   // shrink a line until it fits on one line
  let size = start;
  node.style.fontSize = size + "px";
  while (node.scrollWidth > node.clientWidth && size > min) { size -= 0.5; node.style.fontSize = size + "px"; }
}

// ---- analog: the blush guest check
function analog() {
  const slogan = LINES.todo ? h("div.slogan", LINES.todo) : null;
  const stage = h("div.stage",
    h("div.egg", pet("screen", "painted"), h("div.buttons", h("span"), h("span"), h("span"))),
    h("div.stamp", d.state),
    celebrating && LINES.celebrate ? h("div.sticker", LINES.celebrate) : null);
  const meter = h("div.meter", h("i")); meter.firstChild.style.width = FED + "%";
  const receipt = h("div.receipt", d.feeds.length ? d.feeds.map(f => h("div.r", h("span.d", f.day), h("span.k", f.kind), h("span.note", f.note || ""), h("span.t", f.time)))
    : h("div.empty", "Nothing ordered yet this week."));
  const totals = h("div.totals", ...totalsRows().map(([a, b], i, all) => h(i === all.length - 1 ? "div.r.grand" : "div.r", h("span", a), h("span", b))));
  const main = h("main.check",
    h("div.head", h("span.label.title", "Guest Check"), h("span.label", "Table " + d.table)),
    slogan,
    h("div.sub", h("span.label", "Server " + d.name), h("span.label", d.week ? "Week of " + d.week : "")),
    stage, h("h1", d.name), h("p.line", d.line), h("div.why", d.reason, whyList()),
    h("div.stats",
      h("div.stat", h("div.n", d.streak), h("span.label", "Day streak")),
      h("div.stat", meter, h("span.label", "Fed " + FED + "%")),
      h("div.stat", h("div.n", d.watch.value), h("span.label", d.watch.label))),
    receipt, totals,
    h("section.feed", h("h2", "Feed her"), h("div.row", feedButtons("pill")), h("p", FEED_HELP), toast),
    h("div.thanks", "THANK YOU!"), h("div.foot.label", footLine()));
  document.body.append(main);
  if (slogan) { fitOneLine(slogan, 22, 11); if (document.fonts) document.fonts.ready.then(() => fitOneLine(slogan, 22, 11), err => say("Fonts did not load (" + err.message + ").")); }
}

// ---- cyberpunk: a plum handheld with a pixel LCD and a terminal
function cyberpunk() {
  const prompt = cmd => h("div.p", h("span.ps", "rocheverse:~$"), " " + cmd);
  const out = t => h("div.o", t);
  const log = d.feeds.length ? d.feeds.map(f => out(`[${f.day} ${f.time}] ${f.kind.toUpperCase().padEnd(8)} ${f.note || ""}`)) : [out("no feeds yet this week")];
  const deck = h("main.deck",
    h("div.cart", h("span", d.name.toUpperCase() + " v1")),
    h("div.bezel",
      h("span.screw.tl"), h("span.screw.tr"), h("span.screw.bl"), h("span.screw.br"),
      h("div.leds", h("i.led.candy"), h("i.led.gold"), h("span.px", "pwr"), h("span.px.right", "pocket familiar")),
      h("div.lcd",
        pet("lcd-pet"),
        h("div.lcd-text",
          h("div.px.big", d.name), h("div.px.mood", d.state),
          h("div.px", "streak " + d.streak + "d"),
          h("div.px", "fed ", blocks(10), " " + FED + "%"),
          h("div.px.small", d.watch.label + ": " + d.watch.value),
          celebrating && LINES.celebrate ? h("div.px.small.cele", "✧ " + LINES.celebrate + " ✧") : null)),
      h("div.term",
        prompt("familiar status"), out(d.line), out("why: " + d.reason), ...(d.details || []).map(x => out("  · " + x)),
        prompt("familiar card"), ...log,
        out(totalsRows().map(([a, b]) => a + " " + b).join(" · ")),
        h("div.p", h("span.ps", "rocheverse:~$"), " ", h("span.cursor", " "))),
      h("div.keys", h("span.px.keylabel", "feed"), h("div.keyrow", feedButtons("key"))),
      h("p.help", FEED_HELP), toast),
    h("div.foot.px", footLine()));
  document.body.append(deck);
}

// ---- y2k-blog: a 2003 blog page in an OS window
function y2kBlog() {
  const visitor = String(d.total || 0).padStart(6, "0").replace(/(\d{3})(\d{3})/, "$1,$2");
  const box = (title, ...kids) => h("div.box", h("h3.px", title), ...kids);
  const meter = h("div.meter", h("i")); meter.firstChild.style.width = FED + "%";
  const posts = d.feeds.length ? d.feeds.slice().reverse().map(f => h("article.post",
      h("div.when.px", f.day + " " + f.time), h("div.what", h("span.tag", f.kind), " ", f.note || ""))) :
    [h("article.post", h("div.what", "no posts yet this week. feed her and she writes one."))];
  const sign = h("a.sign", "sign my guestbook ♡"); sign.href = GUESTBOOK; sign.target = "_blank"; sign.rel = "noopener";
  const win = h("main.win",
    h("div.titlebar", h("span.btns", h("i"), h("i"), h("i")), h("span.wtitle.px", d.name.toLowerCase() + ".exe"), h("span.wmeta.px", "rocheverse")),
    h("div.marquee", h("span", celebrating && LINES.celebrate ? "✧ " + LINES.celebrate + " ✧ " + d.line : d.line)),
    h("div.cols",
      h("aside.side",
        h("div.box.petbox", pet("blogpet", "painted"), h("div.petname", d.name)),
        box("about me", h("p", "pocket familiar. I eat what you ship.")),
        box("mood:", h("p.mood", "✧ " + d.state), h("p.small", d.reason)),
        box("streak", h("p", d.streak + " day" + (d.streak === 1 ? "" : "s")), meter, h("p.small", "fed " + FED + "%")),
        box("currently watching", h("p", d.watch.label + ": " + d.watch.value)),
        h("div.counter.px", "you are visitor no. ", h("span.digits", visitor))),
      h("section.posts",
        h("h1", d.name + "'s week"),
        h("div.updated", "last updated " + (d.generated || "today")),
        celebrating ? h("div.stars", "★ ✧ ★ ✧ ★") : null,
        ...posts,
        h("div.tally", totalsRows().map(([a, b]) => a + ": " + b).join("  ·  ")),
        h("div.guestbook", h("h3.px", "guestbook"), h("p", FEED_HELP), h("div.row", feedButtons("chip")), toast, sign))),
    h("div.statusbar.px", footLine()));
  document.body.append(win);
}

// ---- one entry point
function render() {
  document.body.className = "m-" + MOTIF;
  ({ "analog": analog, "cyberpunk": cyberpunk, "y2k-blog": y2kBlog })[MOTIF]();
  const root = document.documentElement;
  root.dataset.motif = MOTIF;
  root.dataset.rendered = "ok";
  const check = () => { root.dataset.overflow = root.scrollWidth > window.innerWidth + 1 ? "yes" : "no"; };
  check();
  if (document.fonts) document.fonts.ready.then(check, err => say("Fonts did not load (" + err.message + ")."));
}
render();
