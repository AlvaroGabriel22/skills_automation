/* Bounded read-only metadata. No values, HTML, textContent, storage or actions.
 * Open shadow roots only; frames require their own authorized context API. */
(function inventoryDOM(options = {}) {
  const bounded = (n, fallback, cap) => Number.isFinite(n) ? Math.max(1, Math.min(cap, Math.floor(n))) : fallback;
  const maxNodes = bounded(options.maxNodes, 300, 2000);
  const maxCandidates = bounded(options.maxCandidates, 60, 200);
  const maxDepth = bounded(options.maxDepth, 18, 30);
  const short = v => typeof v === 'string' ? v.slice(0, 120) : '';
  const attr = (node, key) => short(node.getAttribute(key) || '');
  const describe = node => ({tag:short(node.localName || ''), id:attr(node,'id'), role:attr(node,'role'),
    name:attr(node,'name'), ariaLabel:attr(node,'aria-label'), title:attr(node,'title'),
    type:attr(node,'type'), testId:attr(node,'data-testid')});
  const choose = selector => {
    let matches;
    try { matches = document.querySelectorAll(selector); }
    catch (_) { return {error:'invalid_selector'}; }
    if (matches.length !== 1) return {error:matches.length ? 'ambiguous_selector' : 'missing_selector', count:matches.length};
    return {node:matches[0]};
  };
  const selected = options.rootSelector ? choose(options.rootSelector) : {node:document.documentElement};
  if (selected.error || !selected.node) return {error:selected.error || 'no_document', count:selected.count || 0, candidates:[]};
  const interesting = 'button,input,select,textarea,a[href],iframe,frame,svg,canvas,dialog,[role],[aria-modal],[contenteditable],[tabindex]';
  const candidates = [], stack = [{node:selected.node, depth:0, shadowPath:[]}];
  let visited = 0, truncated = false, openShadowRoots = 0;
  const pushChildren = (collection, depth, shadowPath) => {
    const room = Math.max(0, maxNodes - visited - stack.length);
    const limit = Math.min(collection.length, room);
    if (limit < collection.length) truncated = true;
    for (let i=limit-1;i>=0;i--) stack.push({node:collection[i], depth, shadowPath});
  };
  while (stack.length && visited < maxNodes) {
    const {node, depth, shadowPath} = stack.pop();
    visited++;
    if (node.matches(interesting)) {
      const r = node.getBoundingClientRect(), s = getComputedStyle(node);
      const visible = r.width>0 && r.height>0 && s.display!=='none' && s.visibility!=='hidden' && s.visibility!=='collapse';
      if (options.includeHidden || visible) {
        if (candidates.length >= maxCandidates) { truncated=true; break; }
        candidates.push({...describe(node), visibleHeuristic:visible,
          disabled:node.hasAttribute('disabled') || attr(node,'aria-disabled')==='true',
          ariaModal:attr(node,'aria-modal'), inert:node.hasAttribute('inert'),
          rect:{x:Math.round(r.x),y:Math.round(r.y),width:Math.round(r.width),height:Math.round(r.height)},
          position:short(s.position),pointerEvents:short(s.pointerEvents),shadowPath});
      }
    }
    if (depth>=maxDepth) { if (node.children.length || node.shadowRoot) truncated=true; continue; }
    if (node.localName==='iframe' || node.localName==='frame') continue;
    pushChildren(node.children,depth+1,shadowPath);
    if (node.shadowRoot && node.shadowRoot.mode==='open') {
      openShadowRoots++;
      pushChildren(node.shadowRoot.children,depth+1,[...shadowPath,describe(node)]);
    }
  }
  if (stack.length) truncated=true;
  let probe=null;
  if (options.probeSelector) {
    const chosen=choose(options.probeSelector);
    if (chosen.error) probe={error:chosen.error,count:chosen.count || 0};
    else {
      const r=chosen.node.getBoundingClientRect();
      const left=Math.max(0,r.left),right=Math.min(innerWidth,r.right),top=Math.max(0,r.top),bottom=Math.min(innerHeight,r.bottom);
      if (right<=left || bottom<=top) probe={error:'outside_viewport_or_empty'};
      else {
        const x=(left+right)/2,y=(top+bottom)/2;
        probe={point:{x:Math.round(x),y:Math.round(y)},target:describe(chosen.node),
          topToBottom:document.elementsFromPoint(x,y).slice(0,8).map(describe),
          note:'Heuristic only; descendants, shadow hosts and parent-frame overlays require interpretation.'};
      }
    }
  }
  return {visited,openShadowRoots,truncated,limits:{maxNodes,maxCandidates,maxDepth},candidates,probe};
})
