/*
 * diagram_extract.js
 * Reconstructs flow, state and sequence diagrams drawn with HTML and CSS (boxes, CSS-line
 * arrows, pseudo-element arrowheads) or inline SVG, using the browser's actual layout.
 * Output: Markdown listing boxes, connections (from -> to : label) and anything unresolved.
 *
 * Use in any Chromium-based browser (Chrome, Edge) with no installation:
 *   1. Open the HTML page. Press F12 and open the Console.
 *   2. Paste this whole file and press Enter.
 *   3. Run  extractAllDiagrams()   to extract every diagram the script can find, or
 *      select the diagram in the Elements panel and run  extractDiagram($0).
 *   4. The Markdown is copied to the clipboard (DevTools copy()) and printed.
 * Also used by extract_diagrams.py for batch runs.
 *
 * Best effort: always check the result against the picture. Unresolved items are listed, never guessed.
 */
(function () {
  const KEYWORDS = /(diagram|flow|state|sequence|swim|lane|lifeline|chart|graph|machine|figure|fsm|uml)/i;
  const ARROW_CHARS = /^[▶▷►▼▲◀→⟶➜➔←↑↓>]$/;
  const NEAR = 30, LABEL_NEAR = 48, HEAD_NEAR = 16;

  const squash = s => (s || '').replace(/\s+/g, ' ').trim();
  const cs = (el, pseudo) => getComputedStyle(el, pseudo || null);
  const visible = el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) return false;
    const s = cs(el);
    return s.display !== 'none' && s.visibility !== 'hidden' && parseFloat(s.opacity || '1') > 0;
  };
  const pseudoContent = (el, which) => {
    const c = cs(el, which).content;
    if (!c || c === 'none' || c === 'normal') return null;
    return c.replace(/^["']|["']$/g, '');
  };
  const ownText = el => {
    let t = '';
    for (const n of el.childNodes) if (n.nodeType === 3) t += n.textContent;
    return squash(t);
  };
  const isTransparent = c => !c || c === 'transparent' || /rgba\(.*,\s*0\)$/.test(c);
  const borderCount = s => ['Top', 'Right', 'Bottom', 'Left']
    .filter(side => parseFloat(s['border' + side + 'Width']) > 0 && s['border' + side + 'Style'] !== 'none').length;
  const center = r => ({ x: r.left + r.width / 2, y: r.top + r.height / 2 });
  const distToRect = (p, r) => {
    const dx = Math.max(r.left - p.x, 0, p.x - r.right);
    const dy = Math.max(r.top - p.y, 0, p.y - r.bottom);
    return Math.hypot(dx, dy);
  };
  const round = n => Math.round(n);

  function isBox(el) {
    if (el instanceof SVGElement && el.tagName.toLowerCase() !== 'svg') {
      return ['rect', 'ellipse', 'circle', 'polygon'].includes(el.tagName.toLowerCase());
    }
    const r = el.getBoundingClientRect();
    if (r.width < 28 || r.height < 14) return false;
    const s = cs(el);
    const text = squash(el.innerText || '');
    if (!text || text.length > 120) return false;
    return borderCount(s) >= 3 || !isTransparent(s.backgroundColor) || parseFloat(s.borderRadius) > 0 && borderCount(s) > 0;
  }

  function connectorGeometry(el) {
    const tag = el.tagName.toLowerCase();
    if (el instanceof SVGElement) {
      const m = el.getScreenCTM && el.getScreenCTM();
      if (!m) return null;
      const pt = (x, y) => ({ x: m.a * x + m.c * y + m.e, y: m.b * x + m.d * y + m.f });
      if (tag === 'line') {
        const g = a => parseFloat(el.getAttribute(a) || 0);
        return { p1: pt(g('x1'), g('y1')), p2: pt(g('x2'), g('y2')), svg: true };
      }
      if ((tag === 'path' || tag === 'polyline') && el.getTotalLength) {
        const L = el.getTotalLength();
        if (L < 16) return null;
        const a = el.getPointAtLength(0), b = el.getPointAtLength(L);
        return { p1: pt(a.x, a.y), p2: pt(b.x, b.y), svg: true };
      }
      return null;
    }
    const s = cs(el);
    const r = el.getBoundingClientRect();
    if (s.transform && s.transform !== 'none') {
      const m = s.transform.match(/matrix\(([^)]+)\)/);
      if (m) {
        const [a, b] = m[1].split(',').map(parseFloat);
        const w = el.offsetWidth, h = el.offsetHeight;
        if (Math.min(w, h) <= 8 && Math.max(w, h) >= 16) {
          let ang = Math.atan2(b, a);
          if (h > w) ang += Math.PI / 2;
          const len = Math.max(w, h) / 2, c = center(r);
          return { p1: { x: c.x - Math.cos(ang) * len, y: c.y - Math.sin(ang) * len },
                   p2: { x: c.x + Math.cos(ang) * len, y: c.y + Math.sin(ang) * len } };
        }
      }
    }
    if (r.height <= 8 && r.width >= 16) return { p1: { x: r.left, y: r.top + r.height / 2 }, p2: { x: r.right, y: r.top + r.height / 2 } };
    if (r.width <= 8 && r.height >= 16) return { p1: { x: r.left + r.width / 2, y: r.top }, p2: { x: r.left + r.width / 2, y: r.bottom } };
    return null;
  }

  function extractDiagram(root, index) {
    const all = [root, ...root.querySelectorAll('*')].filter(visible);
    const boxes = [], labels = [], connectors = [], heads = [];
    const boxSet = new Set();

    for (const el of all) if (el !== root && isBox(el)) { boxes.push(el); boxSet.add(el); }
    const boxOf = el => { for (let p = el; p && p !== root.parentElement; p = p.parentElement) if (boxSet.has(p)) return p; return null; };

    for (const el of all) {
      const tag = el.tagName.toLowerCase();
      const txt = ownText(el);
      const r = el.getBoundingClientRect();
      if (txt && ARROW_CHARS.test(txt) && r.width <= 24 && r.height <= 24) { heads.push({ c: center(r), ch: txt }); continue; }
      if (txt) {
        if (!boxOf(el)) labels.push({ text: txt, r, c: center(r), used: false });
        continue;
      }
      if (['marker', 'defs'].includes(tag) || el.closest && el.closest('marker,defs')) continue;
      const geo = connectorGeometry(el);
      if (geo && !boxSet.has(el)) {
        const before = pseudoContent(el, '::before'), after = pseudoContent(el, '::after');
        const markEnd = el.getAttribute && el.getAttribute('marker-end'), markStart = el.getAttribute && el.getAttribute('marker-start');
        const sty = cs(el);
        connectors.push({ el, ...geo,
          headEnd: !!(after !== null || markEnd || sty.markerEnd && sty.markerEnd !== 'none'),
          headStart: !!(before !== null || markStart || sty.markerStart && sty.markerStart !== 'none'),
          dashed: /dash|dot/.test(sty.borderTopStyle + sty.borderLeftStyle + (el.getAttribute && el.getAttribute('stroke-dasharray') || '')) });
        continue;
      }
      if (r.width >= 3 && r.height >= 3 && r.width <= 16 && r.height <= 16 && !boxSet.has(el)) {
        const s = cs(el);
        const triangle = borderCount(s) >= 2 && isTransparent(s.backgroundColor) && el.offsetWidth === 0;
        const svgHead = tag === 'polygon' || tag === 'path';
        if (triangle || svgHead) heads.push({ c: center(r) });
      }
    }

    const boxLabel = b => {
      const own = squash(b.innerText || b.textContent || '');
      if (own) return own;
      // SVG rects and overlay layouts: use text whose centre falls inside the box.
      const r = b.getBoundingClientRect();
      const inside = labels.filter(l => !l.used && l.c.x >= r.left && l.c.x <= r.right && l.c.y >= r.top && l.c.y <= r.bottom)
        .sort((x, y) => x.c.y - y.c.y || x.c.x - y.c.x);
      inside.forEach(l => { l.used = true; });
      return squash(inside.map(l => l.text).join(' ')) || '(unlabelled box)';
    };
    const boxRects = boxes.map(b => ({ b, r: b.getBoundingClientRect(), name: boxLabel(b) }));
    // Sequence-diagram support: the top row of boxes acts as lifeline headers.
    const minTop = Math.min(...boxRects.map(x => x.r.top));
    const topRow = boxRects.filter(x => x.r.top - minTop < 20);
    // A lifeline: a long vertical connector with no arrowheads hanging from a top-row box.
    const lifelineOf = k => {
      if (k.headStart || k.headEnd || Math.abs(k.p1.x - k.p2.x) > 3 || Math.abs(k.p2.y - k.p1.y) < 100) return null;
      const top = k.p1.y < k.p2.y ? k.p1 : k.p2;
      return topRow.find(h => distToRect(top, h.r) <= NEAR) || null;
    };
    const headers = [];
    for (const k of connectors) { const h = lifelineOf(k); if (h && !headers.includes(h)) { headers.push(h); k.lifeline = true; } }

    function nodeAt(p) {
      let best = null, bd = Infinity;
      for (const x of boxRects) { const d = distToRect(p, x.r); if (d < bd) { bd = d; best = x; } }
      if (best && bd <= NEAR) return best.name;
      let hb = null, hd = Infinity;
      for (const h of headers) { const d = Math.abs(center(h.r).x - p.x); if (d < hd) { hd = d; hb = h; } }
      if (hb && hd <= hb.r.width / 2 + NEAR && p.y > hb.r.bottom) return hb.name;
      return null;
    }

    const edges = [], unresolved = [];
    for (const k of connectors) {
      if (k.lifeline) continue;
      let { p1, p2, headStart, headEnd } = k;
      for (const h of heads) {
        if (Math.hypot(h.c.x - p2.x, h.c.y - p2.y) <= HEAD_NEAR) headEnd = true;
        if (Math.hypot(h.c.x - p1.x, h.c.y - p1.y) <= HEAD_NEAR) headStart = true;
      }
      const a = nodeAt(p1), b = nodeAt(p2);
      // Both ends on the same node with no arrowhead: a lifeline, divider or border, not a connection.
      if (a && a === b && !headStart && !headEnd) continue;
      const mid = { x: (p1.x + p2.x) / 2, y: (p1.y + p2.y) / 2 };
      let lab = null, ld = Infinity;
      for (const l of labels) { if (l.used) continue; const d = distToRect(mid, l.r); if (d < ld) { ld = d; lab = l; } }
      let label = '';
      if (lab && ld <= LABEL_NEAR) { lab.used = true; label = lab.text; }
      if (!a || !b || a === b) { unresolved.push({ p1, p2, label, a, b }); continue; }
      let from = a, to = b, dir = 'direction unknown';
      if (headEnd && !headStart) dir = '->';
      else if (headStart && !headEnd) { from = b; to = a; dir = '->'; }
      else if (headStart && headEnd) dir = '<->';
      edges.push({ from, to, dir, label, dashed: k.dashed, y: Math.min(p1.y, p2.y), x: Math.min(p1.x, p2.x) });
    }
    edges.sort((e1, e2) => e1.y - e2.y || e1.x - e2.x);
    for (const e of edges) {
      const num = labels.find(l => !l.used && /^\d{1,3}[.)]?$/.test(l.text) && Math.abs(l.c.y - e.y) <= 16);
      if (num) { num.used = true; e.step = num.text.replace(/[.)]$/, ''); }
    }

    const desc = squash(root.getAttribute('aria-label') || root.id || root.getAttribute('class') || root.tagName);
    const out = [`### Diagram ${index} (rendered HTML/CSS): ${desc}`, '', 'Boxes, top to bottom, left to right:'];
    boxRects.slice().sort((x, y) => x.r.top - y.r.top || x.r.left - y.r.left)
      .forEach(x => out.push(`- ${x.name}`));
    out.push('', 'Connections, in vertical order:');
    if (!edges.length) out.push('- none resolved');
    edges.forEach((e, i) => {
      const arrow = e.dir === '->' ? '->' : e.dir === '<->' ? '<->' : '--';
      out.push(`${i + 1}. ${e.step ? '[step ' + e.step + '] ' : ''}${e.from} ${arrow} ${e.to}${e.label ? ` : ${e.label}` : ''}${e.dashed ? ' (dashed)' : ''}${e.dir === 'direction unknown' ? ' (direction unknown)' : ''}`);
    });
    const loose = labels.filter(l => !l.used);
    if (loose.length) {
      out.push('', 'Labels not attached to a box or connection (check against the picture):');
      loose.sort((x, y) => x.c.y - y.c.y || x.c.x - y.c.x).forEach(l => out.push(`- "${l.text}" at (${round(l.c.x)}, ${round(l.c.y)})`));
    }
    if (unresolved.length) {
      out.push('', 'Connectors whose ends could not be matched to boxes (check against the picture):');
      unresolved.forEach(u => out.push(`- from (${round(u.p1.x)}, ${round(u.p1.y)}) ${u.a ? '[' + u.a + ']' : ''} to (${round(u.p2.x)}, ${round(u.p2.y)}) ${u.b ? '[' + u.b + ']' : ''}${u.label ? ' label: ' + u.label : ''}`));
    }
    out.push('', `Extraction summary: ${boxRects.length} boxes, ${edges.length} connections resolved, ${unresolved.length} unresolved, ${loose.length} loose labels.`, '');
    return { markdown: out.join('\n'), boxes: boxRects.length, edges: edges.length, unresolved: unresolved.length };
  }

  function findDiagramRoots() {
    const cands = [...document.querySelectorAll('figure, [data-diagram], [role="img"], [class], [id]')]
      .filter(el => el.tagName.toLowerCase() !== 'svg' || !el.closest('figure'))
      .filter(el => el === el.closest('figure') || el.hasAttribute('data-diagram') || el.getAttribute('role') === 'img'
        || KEYWORDS.test((el.getAttribute('class') || '') + ' ' + (el.id || '') + ' ' + (el.getAttribute('aria-label') || '')))
      .filter(visible);
    // Any sizeable SVG is a candidate too, whatever its class names.
    for (const svg of document.querySelectorAll('svg')) {
      const r = svg.getBoundingClientRect();
      if (r.width >= 150 && r.height >= 80 && visible(svg) && !cands.includes(svg)) cands.push(svg);
    }
    // Keep the outermost candidate that still contains at least two boxes.
    const roots = cands.filter(el => !cands.some(o => o !== el && o.contains(el)));
    return roots;
  }

  function extractAllDiagrams() {
    const roots = findDiagramRoots();
    const parts = [];
    let n = 0;
    for (const r of roots) {
      const res = extractDiagram(r, n + 1);
      if (res.boxes >= 2) { n += 1; parts.push(res.markdown); }
    }
    const md = parts.length ? parts.join('\n') :
      'No diagram containers found. Select the diagram in the Elements panel and run extractDiagram($0).';
    if (typeof copy === 'function') { try { copy(md); } catch (e) {} }
    console.log(md);
    return md;
  }

  window.extractDiagram = (el) => {
    const md = extractDiagram(el, 1).markdown;
    if (typeof copy === 'function') { try { copy(md); } catch (e) {} }
    console.log(md);
    return md;
  };
  window.extractAllDiagrams = extractAllDiagrams;
  window.__findDiagramRoots = findDiagramRoots;
})();
