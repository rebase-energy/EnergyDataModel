"""Build a self-contained HTML class explorer for energydatamodel.

Introspects the live class hierarchy starting from ``Element``, captures
each class's dataclass fields, docstring (rendered through docutils to
HTML), parent classes, autodoc page link, and source location. Emits
``edm-explorer.html``: a single-file Cytoscape.js viewer with pan/zoom,
a click-to-reveal sidebar, and a category filter in the legend.

Run from the package root::

    uv run python build_class_explorer.py

By default writes two copies::

    ./edm-explorer.html                   (standalone, double-click to open)
    docs/_static/edm-explorer.html        (served by Sphinx via iframe)

Flags::

    --github-base URL   Base URL for source links
                        (default: rebase-energy/EnergyDataModel main).
    --docs-base PATH    Relative prefix for autodoc deep links from where
                        the explorer is served (default: '../' so it works
                        from docs/_static/ → docs/energydatamodel/...).
    --out PATH          Override default output paths; if given, only this
                        single file is written.
"""

from __future__ import annotations

import argparse
import dataclasses
import inspect
import io
import json
import re
import sys
import typing
from contextlib import redirect_stderr
from pathlib import Path

import energydatamodel as edm
from docutils.core import publish_parts
from energydatamodel.bases import Sensor

PACKAGE_ROOT = Path(edm.__file__).resolve().parent
PACKAGE_NAME = edm.__name__

# Module → semantic category. Anything not listed is "other".
MODULE_CATEGORY = {
    "energydatamodel.containers": "collection",
    "energydatamodel.area": "area",
    "energydatamodel.wind": "generation",
    "energydatamodel.solar": "generation",
    "energydatamodel.hydro": "generation",
    "energydatamodel.battery": "generation",
    "energydatamodel.building": "demand",
    "energydatamodel.heatpump": "demand",
    "energydatamodel.weather": "sensor",
}

CATEGORY_PALETTE = {
    "abstract": {"fill": "#E2E8F0", "stroke": "#4A5568", "text": "#1A202C"},
    "base": {"fill": "#CBD5E0", "stroke": "#4A5568", "text": "#1A202C"},
    "collection": {"fill": "#BEE3F8", "stroke": "#2B6CB0", "text": "#1A365D"},
    "area": {"fill": "#E9D8FD", "stroke": "#6B46C1", "text": "#322659"},
    "generation": {"fill": "#C6F6D5", "stroke": "#2F855A", "text": "#22543D"},
    "demand": {"fill": "#FED7AA", "stroke": "#C05621", "text": "#7B341E"},
    "sensor": {"fill": "#FEFCBF", "stroke": "#B7791F", "text": "#5F370E"},
    "grid_node": {"fill": "#FED7D7", "stroke": "#C53030", "text": "#742A2A"},
    "grid_edge": {"fill": "#FED7D7", "stroke": "#C53030", "text": "#742A2A"},
    "series": {"fill": "#B2F5EA", "stroke": "#2C7A7B", "text": "#234E52"},
    "other": {"fill": "#EDF2F7", "stroke": "#4A5568", "text": "#1A202C"},
}

# Hand-classified abstract/intermediate bases (rendered greyscale).
ABSTRACT_NAMES = {"Element", "Node", "Edge", "Collection", "Asset"}
BASE_NAMES = {"NodeAsset", "EdgeAsset", "Sensor", "GridNode", "Area"}

# Sphinx-specific roles that default docutils does not understand.
# Convert them to plain inline code so RST rendering doesn't choke.
SPHINX_ROLE_RE = re.compile(r":(?:class|func|meth|attr|mod|obj|data|exc|ref):`([^`]+)`")


def _categorize(cls: type) -> str:
    name = cls.__name__
    if name in ABSTRACT_NAMES:
        return "abstract"
    if name in BASE_NAMES:
        return "base"
    # Collection subtree wins over module — SubNetwork/Network live in
    # grid.py but are conceptually containers.
    if issubclass(cls, edm.Collection):
        return "collection"
    module = cls.__module__
    # Grid module mixes nodes (GridNode subclasses + Transformer as a NodeAsset)
    # with edges (EdgeAsset subclasses). Classify by Node vs Edge ancestry.
    if module == "energydatamodel.grid":
        if issubclass(cls, edm.Node):
            return "grid_node"
        return "grid_edge"
    if issubclass(cls, Sensor) and cls is not Sensor:
        return "sensor"
    return MODULE_CATEGORY.get(module, "other")


def _collect_classes() -> list[type]:
    """All Element subclasses, plus Asset (a sibling), in deterministic order."""
    seen: dict[str, type] = {}

    def walk(cls: type) -> None:
        if cls.__name__ in seen:
            return
        seen[cls.__name__] = cls
        for sub in cls.__subclasses__():
            walk(sub)

    walk(edm.Element)
    walk(edm.Asset)
    return sorted(seen.values(), key=lambda c: (_categorize(c), c.__name__))


def _format_type(annotation: object) -> str:
    """Render a type annotation as a readable string."""
    if annotation is dataclasses.MISSING or annotation is inspect.Parameter.empty:
        return ""
    if isinstance(annotation, str):
        return annotation
    try:
        return typing.get_type_hints(annotation, include_extras=False)  # type: ignore[arg-type]
    except Exception:
        pass
    try:
        return repr(annotation).replace("typing.", "")
    except Exception:
        return str(annotation)


def _format_default(field: dataclasses.Field) -> str | None:
    if field.default is not dataclasses.MISSING:
        return repr(field.default)
    if field.default_factory is not dataclasses.MISSING:
        try:
            return f"{field.default_factory.__name__}()"  # type: ignore[union-attr]
        except AttributeError:
            return repr(field.default_factory)
    return None


def _fields_for(cls: type) -> list[dict]:
    if not dataclasses.is_dataclass(cls):
        return []
    out = []
    for f in dataclasses.fields(cls):
        if f.name.startswith("_"):
            continue
        out.append(
            {
                "name": f.name,
                "type": _format_type(f.type),
                "default": _format_default(f),
            }
        )
    return out


def _source_link(cls: type, github_base: str | None) -> dict:
    try:
        file = Path(inspect.getsourcefile(cls) or "")
        _, lineno = inspect.getsourcelines(cls)
    except (OSError, TypeError):
        return {}
    rel = file.resolve().relative_to(PACKAGE_ROOT.parent) if file.is_relative_to(PACKAGE_ROOT.parent) else file
    info = {"path": str(rel), "line": lineno}
    if github_base:
        info["url"] = f"{github_base.rstrip('/')}/{rel}#L{lineno}"
    return info


def _docs_link(cls: type, docs_base: str | None) -> str | None:
    """Sphinx autodoc deep link for a class.

    Sphinx renders ``energydatamodel.wind`` at ``energydatamodel/wind.html``
    with anchors like ``#energydatamodel.wind.WindTurbine``.
    """
    if not docs_base:
        return None
    short = cls.__module__.rsplit(".", 1)[-1]
    return f"{docs_base.rstrip('/')}/energydatamodel/{short}.html#{cls.__module__}.{cls.__name__}"


def _parents(cls: type, all_names: set[str]) -> list[str]:
    """Direct base classes that are part of the EDM hierarchy."""
    return [b.__name__ for b in cls.__bases__ if b.__name__ in all_names]


def _render_docstring(cls: type) -> str:
    """Class docstring rendered to HTML via docutils.

    Strips dataclass-synthesized signatures and converts Sphinx-specific
    roles (``:class:`Foo```) to plain inline literals before rendering, so
    the default docutils RST parser doesn't error out.
    """
    raw = (inspect.getdoc(cls) or "").strip()
    if not raw:
        return ""
    # Drop dataclass __repr__ signature pseudo-docstring.
    if raw.startswith(f"{cls.__name__}(") and raw.split("\n", 1)[0].endswith(")"):
        return ""

    rst = SPHINX_ROLE_RE.sub(r"``\1``", raw)

    with redirect_stderr(io.StringIO()):
        parts = publish_parts(
            rst,
            writer_name="html5",
            settings_overrides={
                "report_level": 5,  # suppress all docutils warnings
                "halt_level": 5,
                "output_encoding": "unicode",
                "embed_stylesheet": False,
                "doctitle_xform": False,
            },
        )
    return parts.get("html_body") or parts.get("body") or ""


# Categories that get rendered as compound parent nodes (visual grouping
# at zoomed-out levels). "abstract", "base", and "series" stay as plain
# nodes — they're the trunk we want clearly visible.
GROUPED_CATEGORIES = {
    "collection": "Collections",
    "area": "Areas",
    "generation": "Generation & Storage",
    "demand": "Demand-side",
    "sensor": "Sensors",
    "grid_node": "Grid nodes",
    "grid_edge": "Grid edges",
}


def build_graph(github_base: str | None, docs_base: str | None) -> dict:
    classes = _collect_classes()
    names = {c.__name__ for c in classes}

    nodes = []
    edges = []

    # Compound parent nodes — one per grouped category.
    for cat, label in GROUPED_CATEGORIES.items():
        nodes.append(
            {
                "data": {
                    "id": f"__group_{cat}",
                    "label": label,
                    "category": cat,
                    "is_group": True,
                }
            }
        )

    for cls in classes:
        category = _categorize(cls)
        node_data = {
            "id": cls.__name__,
            "label": cls.__name__,
            "category": category,
            "module": cls.__module__,
            "qualname": f"{cls.__module__}.{cls.__name__}",
            "doc_html": _render_docstring(cls),
            "fields": _fields_for(cls),
            "parents": _parents(cls, names),
            "source": _source_link(cls, github_base),
            "docs_url": _docs_link(cls, docs_base),
        }
        if category in GROUPED_CATEGORIES:
            node_data["parent"] = f"__group_{category}"

        nodes.append({"data": node_data})

        for parent in _parents(cls, names):
            edges.append(
                {
                    "data": {
                        "id": f"{parent}->{cls.__name__}",
                        "source": parent,
                        "target": cls.__name__,
                    }
                }
            )

    return {"nodes": nodes, "edges": edges, "palette": CATEGORY_PALETTE}


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>EnergyDataModel — class explorer</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
  :root {
    --sidebar-w: 380px;
    --bg: #f7fafc;
    --panel: #ffffff;
    --border: #e2e8f0;
    --muted: #718096;
    --text: #1a202c;
    --accent: #319795;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; height: 100%; background: var(--bg); color: var(--text);
               font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }
  #app { display: grid; grid-template-columns: 1fr var(--sidebar-w); height: 100vh; }

  /* Hide the graph until the async ELK layout finishes, then fade in.
     Without this, the user sees nodes briefly stacked at (0,0) before
     the layout snaps them into place. */
  #cy { width: 100%; height: 100%; background: var(--panel);
        opacity: 0; transition: opacity 0.25s ease-out; }
  #cy.ready { opacity: 1; }

  #cy-loading { position: absolute; inset: 0; display: flex; align-items: center;
                justify-content: center; color: var(--muted); font-size: 13px;
                pointer-events: none; transition: opacity 0.2s ease-out; gap: 10px; }
  #cy-loading.hidden { opacity: 0; }
  #cy-loading::before { content: ''; width: 14px; height: 14px;
                        border: 2px solid var(--border);
                        border-top-color: var(--accent);
                        border-radius: 50%;
                        animation: spin 0.7s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  #sidebar { border-left: 1px solid var(--border); background: var(--panel);
             overflow-y: auto; padding: 20px; }
  #sidebar h1 { font-size: 13px; text-transform: uppercase; letter-spacing: 0.06em;
                color: var(--muted); margin: 0 0 8px 0; font-weight: 600; }
  #sidebar h2 { font-size: 22px; margin: 0 0 4px 0; font-weight: 600; }
  #sidebar .module { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
                     color: var(--muted); font-size: 12px; margin: 0 0 16px 0; }
  #sidebar .badge { display: inline-block; padding: 2px 8px; border-radius: 999px;
                    font-size: 11px; font-weight: 500; margin-bottom: 12px; }
  #sidebar section { margin-top: 18px; }
  #sidebar section h3 { font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em;
                        color: var(--muted); margin: 0 0 8px 0; font-weight: 600; }
  #sidebar .doc { font-size: 14px; line-height: 1.55; color: #2d3748; }
  #sidebar .doc p { margin: 0 0 10px 0; }
  #sidebar .doc code, #sidebar .doc tt.docutils.literal {
    font-family: ui-monospace, monospace; background: #edf2f7; padding: 1px 5px;
    border-radius: 3px; font-size: 12.5px; color: #2c5282;
  }
  #sidebar .doc ul { margin: 0 0 10px 0; padding-left: 18px; }
  #sidebar .doc li { margin: 2px 0; }
  #sidebar .field { padding: 6px 0; border-bottom: 1px solid #f1f5f9; font-size: 13px; }
  #sidebar .field:last-child { border-bottom: none; }
  #sidebar .field .fname { font-family: ui-monospace, monospace; font-weight: 600; color: var(--text); }
  #sidebar .field .ftype { font-family: ui-monospace, monospace; color: var(--accent); margin-left: 6px; }
  #sidebar .field .fdefault { font-family: ui-monospace, monospace; color: var(--muted); margin-left: 6px; }
  #sidebar .links a { color: var(--accent); text-decoration: none; cursor: pointer; }
  #sidebar .links a:hover { text-decoration: underline; }
  #sidebar .links { display: flex; flex-direction: column; gap: 6px; font-size: 13px; }
  #sidebar .parents .pill { display: inline-block; padding: 3px 10px; border: 1px solid var(--border);
                            border-radius: 999px; margin: 0 6px 6px 0; font-size: 12px;
                            font-family: ui-monospace, monospace; color: var(--accent); cursor: pointer; }
  #sidebar .parents .pill:hover { border-color: var(--accent); }
  #search { position: absolute; top: 16px; left: 16px; z-index: 10;
            padding: 8px 12px; border: 1px solid var(--border); border-radius: 8px;
            background: rgba(255,255,255,0.95); font-size: 13px; min-width: 220px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
  #legend { position: absolute; bottom: 16px; left: 50%; transform: translateX(-50%);
            background: rgba(255,255,255,0.95); border: 1px solid var(--border);
            border-radius: 8px; padding: 8px 14px; font-size: 11px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04); user-select: none;
            z-index: 10;
            display: flex; flex-wrap: wrap; align-items: center;
            gap: 4px 14px; max-width: calc(100% - 60px); }
  #legend .header { font-weight: 600; color: var(--muted); text-transform: uppercase;
                    letter-spacing: 0.06em; font-size: 10px; margin-right: 4px; }
  #legend .row { display: inline-flex; align-items: center; gap: 6px; cursor: pointer;
                 padding: 2px 4px; border-radius: 4px; transition: background 0.1s;
                 white-space: nowrap; }
  #legend .row:hover { background: #edf2f7; }
  #legend .row.off { opacity: 0.4; }
  #legend .row.off .label { text-decoration: line-through; }
  #legend .swatch { width: 12px; height: 12px; border-radius: 3px; border: 1px solid #ccc; }
  #legend .footer { font-size: 10px; color: var(--muted); margin-left: 4px; }
  #empty { color: var(--muted); font-size: 14px; padding: 40px 20px; text-align: center; }
</style>
<link rel="stylesheet" href="https://unpkg.com/tippy.js@6/dist/tippy.css" />
<body>
<div id="app">
  <div style="position: relative; height: 100%;">
    <input id="search" type="text" placeholder="Filter classes..." />
    <div id="legend"></div>
    <div id="cy"></div>
    <div id="cy-loading">Computing layout…</div>
  </div>
  <aside id="sidebar">
    <div id="empty">
      <strong>Click any class</strong> in the diagram to see its fields,
      docstring, parent classes, and links to the API reference and source.<br /><br />
      Drag to pan, scroll to zoom. Click categories in the legend to toggle.
    </div>
  </aside>
</div>

<script src="https://unpkg.com/cytoscape@3.30.0/dist/cytoscape.min.js"></script>
<script src="https://unpkg.com/elkjs@0.9.3/lib/elk.bundled.js"></script>
<script src="https://unpkg.com/cytoscape-elk@2.2.0/dist/cytoscape-elk.js"></script>
<script src="https://unpkg.com/@popperjs/core@2"></script>
<script src="https://unpkg.com/tippy.js@6"></script>
<script src="https://unpkg.com/cytoscape-popper@2"></script>
<script>
// Register cytoscape extensions. UMD bundles vary: some expose a
// camelCase `window.cytoscapeFoo`, some expose `window["cytoscape-foo"]`.
// Tolerate both forms.
function _useExt(name) {
  const camel = name.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
  const ext = window[camel] || window[name];
  if (ext && typeof cytoscape !== 'undefined') cytoscape.use(ext);
}
_useExt('cytoscape-elk');
_useExt('cytoscape-popper');

const GRAPH = __GRAPH_JSON__;

const palette = GRAPH.palette;
const nodesByCategory = {};
GRAPH.nodes.forEach(n => {
  const c = n.data.category;
  (nodesByCategory[c] = nodesByCategory[c] || []).push(n);
});

const hiddenCategories = new Set();

// Build legend (with category-toggle behavior)
const legendEl = document.getElementById('legend');
legendEl.innerHTML = '<div class="header">Filter</div>';
Object.entries(palette).forEach(([cat, colors]) => {
  if (!nodesByCategory[cat]) return;
  const row = document.createElement('div');
  row.className = 'row';
  row.dataset.cat = cat;
  row.innerHTML =
    `<span class="swatch" style="background:${colors.fill};border-color:${colors.stroke}"></span>` +
    `<span class="label">${cat.replace('_', ' ')}</span>`;
  row.addEventListener('click', () => toggleCategory(cat, row));
  legendEl.appendChild(row);
});
// (No "click to hide" footer — the cursor change on hover communicates
// it. Footer would force the legend onto two lines, breaking the
// horizontal layout.)

function toggleCategory(cat, rowEl) {
  if (hiddenCategories.has(cat)) {
    hiddenCategories.delete(cat);
    rowEl.classList.remove('off');
  } else {
    hiddenCategories.add(cat);
    rowEl.classList.add('off');
  }
  cy.batch(() => {
    cy.nodes().forEach(n => {
      const hide = hiddenCategories.has(n.data('category'));
      n.style('display', hide ? 'none' : 'element');
    });
  });
  // Re-run layout so freed-up space is reclaimed (and re-fit viewport).
  runLayout();
}

function hexWithAlpha(hex, alpha) {
  // Lighten a #RRGGBB color by mixing it with white at a given amount.
  // Used for compound parent backgrounds so they sit visually behind
  // their children without competing for attention.
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  const mix = (c) => Math.round(c + (255 - c) * (1 - alpha));
  return `rgb(${mix(r)}, ${mix(g)}, ${mix(b)})`;
}

// Cytoscape
const cy = cytoscape({
  container: document.getElementById('cy'),
  elements: { nodes: GRAPH.nodes, edges: GRAPH.edges },
  style: [
    // Leaf class nodes
    {
      selector: 'node',
      style: {
        'shape': 'round-rectangle',
        'background-color': ele => palette[ele.data('category')]?.fill || '#EDF2F7',
        'border-color':     ele => palette[ele.data('category')]?.stroke || '#4A5568',
        'border-width': 1.5,
        'label': 'data(label)',
        'color': ele => palette[ele.data('category')]?.text || '#1A202C',
        'font-size': 13,
        'font-family': 'Inter, system-ui, -apple-system, "Segoe UI", Helvetica, sans-serif',
        'font-weight': 500,
        'text-valign': 'center',
        'text-halign': 'center',
        'text-wrap': 'wrap',
        'text-max-width': 110,
        'padding': 6,
        'width': 'label',
        'height': 'label',
      }
    },
    // Compound parent nodes — paler background, label at top, no fill competing.
    {
      selector: 'node[?is_group]',
      style: {
        'shape': 'round-rectangle',
        'background-color':  ele => hexWithAlpha(palette[ele.data('category')]?.fill || '#EDF2F7', 0.3),
        'background-opacity': 0.55,
        'border-color':      ele => palette[ele.data('category')]?.stroke || '#A0AEC0',
        'border-width': 1.5,
        'border-style': 'dashed',
        'label': 'data(label)',
        'color':              ele => palette[ele.data('category')]?.text || '#1A202C',
        'font-size': 15,
        'font-weight': 600,
        'text-valign': 'top',
        'text-halign': 'center',
        'text-margin-y': -8,
        'padding': 18,
      }
    },
    {
      selector: 'node.dimmed',
      style: { 'opacity': 0.7 }
    },
    {
      selector: 'edge.dimmed',
      style: { 'opacity': 0.4 }
    },
    // Hover: subtle thicken on the node border, no color shift — meant to
    // be clearly weaker than `:selected` (which shifts to teal).
    {
      selector: 'node.hover',
      style: { 'border-width': 2.5 }
    },
    {
      selector: 'node:selected',
      style: {
        'border-width': 3,
        'border-color': '#319795',
      }
    },
    {
      selector: 'edge',
      style: {
        'curve-style': 'bezier',
        'target-arrow-shape': 'triangle',
        'line-color': '#A0AEC0',
        'target-arrow-color': '#A0AEC0',
        'arrow-scale': 0.8,
        'width': 1.2,
        'opacity': 0.85,
      }
    },
    {
      selector: 'edge.highlighted',
      style: { 'line-color': '#319795', 'target-arrow-color': '#319795', 'width': 2.5, 'opacity': 1 }
    },
    // Hover edge: faded teal, slight thicken — clearly weaker than `.highlighted`.
    {
      selector: 'edge.hover',
      style: { 'line-color': '#4FD1C5', 'target-arrow-color': '#4FD1C5', 'width': 1.6, 'opacity': 0.95 }
    }
  ],
  wheelSensitivity: 0.2,
  minZoom: 0.2,
  maxZoom: 4,
  // View-only: users pan/zoom but cannot drag nodes around. The graph
  // is a fixed visualisation, not an editor.
  autoungrabify: true,
  autounselectify: false,
  boxSelectionEnabled: false,
});

// Layout: ELK layered, compound-aware, left-to-right. Class names extend
// horizontally, so a horizontal hierarchy lets siblings stack vertically
// (compact) while the long axis carries the inheritance chain.
const LAYOUT = {
  name: 'elk',
  fit: true,
  padding: 30,
  animate: true,
  animationDuration: 220,
  animationEasing: 'ease-out',
  elk: {
    'algorithm': 'layered',
    'elk.direction': 'RIGHT',
    'elk.layered.spacing.nodeNodeBetweenLayers': 55,
    'elk.spacing.nodeNode': 28,
    // Brandes-Köpf gives cleaner sibling alignment than NETWORK_SIMPLEX
    // for class hierarchies — same-rank nodes line up on a common axis.
    'elk.layered.nodePlacement.strategy': 'BRANDES_KOEPF',
    'elk.layered.nodePlacement.bk.fixedAlignment': 'BALANCED',
    'elk.layered.crossingMinimization.strategy': 'LAYER_SWEEP',
    'elk.layered.compaction.postCompaction.strategy': 'LEFT',
    'elk.aspectRatio': 1.6,
    'elk.hierarchyHandling': 'INCLUDE_CHILDREN',
    'elk.padding': '[top=18,left=24,bottom=18,right=18]',
  }
};

function runLayout() {
  const layout = cy.layout(LAYOUT);
  // Reveal the graph + hide the loading indicator only once ELK has
  // finished placing nodes. Without this the user sees a brief flash of
  // every node stacked at (0,0) before the async layout completes.
  layout.one('layoutstop', () => {
    document.getElementById('cy').classList.add('ready');
    const loader = document.getElementById('cy-loading');
    if (loader) loader.classList.add('hidden');
  });
  layout.run();
}

// Sidebar render
const sidebar = document.getElementById('sidebar');

function renderClass(data) {
  const colors = palette[data.category] || palette.other;
  const fieldRow = f => {
    const t = f.type ? `<span class="ftype">: ${escapeHtml(f.type)}</span>` : '';
    const d = f.default ? `<span class="fdefault"> = ${escapeHtml(f.default)}</span>` : '';
    return `<div class="field"><span class="fname">${f.name}</span>${t}${d}</div>`;
  };
  const fields = data.fields.length
    ? data.fields.map(fieldRow).join('')
    : '<div style="color: var(--muted); font-size: 13px;">No declared fields.</div>';

  const parents = data.parents.length
    ? data.parents.map(p => `<a class="pill" data-class="${p}">${p}</a>`).join('')
    : '<span style="color: var(--muted); font-size: 13px;">(none)</span>';

  const links = [];
  if (data.docs_url) {
    links.push(
      `<a href="${data.docs_url}" target="_parent" rel="noopener">View full API docs ↗</a>`
    );
  }
  if (data.source.url) {
    links.push(
      `<a href="${data.source.url}" target="_blank" rel="noopener">` +
      `Source: ${data.source.path}:${data.source.line} ↗</a>`
    );
  } else if (data.source.path) {
    links.push(
      `<span style="font-family: ui-monospace, monospace; color: var(--muted); font-size: 12px;">` +
      `${data.source.path}:${data.source.line}</span>`
    );
  }
  const linksHtml = links.length
    ? `<div class="links">${links.join('')}</div>`
    : '<span style="color: var(--muted);">(unavailable)</span>';

  sidebar.innerHTML = `
    <h1>EnergyDataModel</h1>
    <h2>${data.label}</h2>
    <div class="module">${data.module}</div>
    <span class="badge" style="background:${colors.fill};color:${colors.text}">${data.category}</span>

    ${data.doc_html ? `<section><h3>Docstring</h3><div class="doc">${data.doc_html}</div></section>` : ''}

    <section>
      <h3>Fields (${data.fields.length})</h3>
      ${fields}
    </section>

    <section>
      <h3>Parent classes</h3>
      <div class="parents">${parents}</div>
    </section>

    <section>
      <h3>Links</h3>
      ${linksHtml}
    </section>
  `;

  sidebar.querySelectorAll('a.pill').forEach(a => {
    a.addEventListener('click', () => {
      const target = cy.getElementById(a.dataset.class);
      if (target.length) {
        cy.elements().unselect();
        target.select();
        cy.animate({ center: { eles: target }, zoom: 1.3 }, { duration: 350 });
        renderClass(target.data());
        highlightNeighborhood(target);
      }
    });
  });
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

function highlightNeighborhood(node) {
  cy.elements().removeClass('dimmed highlighted');
  const nbh = node.closedNeighborhood();
  // Dim everything outside the neighborhood — but never dim the compound
  // category boxes; they're scaffolding and should stay clearly visible.
  cy.elements().not(nbh).not('node[?is_group]').addClass('dimmed');
  nbh.edges().addClass('highlighted');
}

cy.on('tap', 'node', evt => {
  // Ignore taps on the compound parent boxes — they're visual grouping only.
  if (evt.target.data('is_group')) return;
  renderClass(evt.target.data());
  highlightNeighborhood(evt.target);
  // Reflect selection in URL so external deep-links work and the back
  // button walks selection history.
  history.replaceState(null, '', '#' + evt.target.id());
});
cy.on('tap', evt => {
  if (evt.target === cy) {
    cy.elements().removeClass('dimmed highlighted');
  }
});

// Hover: highlight connected edges + show a tippy tooltip with class
// summary. Lets users scan the graph without committing to a click
// (which would repaint the whole sidebar).
let activeTip = null;
function destroyTip() {
  if (activeTip) {
    activeTip.destroy();
    activeTip = null;
  }
}
function showTip(node) {
  destroyTip();
  if (typeof tippy === 'undefined' || typeof node.popperRef !== 'function') return;
  const ref = node.popperRef();
  const fieldCount = (node.data('fields') || []).length;
  const cat = node.data('category');
  const dummy = document.createElement('div');
  document.body.appendChild(dummy);
  activeTip = tippy(dummy, {
    getReferenceClientRect: () => ref.getBoundingClientRect(),
    trigger: 'manual',
    placement: 'top',
    arrow: true,
    allowHTML: true,
    appendTo: document.body,
    hideOnClick: false,
    content:
      '<strong>' + node.data('label') + '</strong>' +
      '<div style="opacity:.7;font-size:11px;margin-top:2px">' +
      cat + ' · ' + fieldCount + ' field' + (fieldCount === 1 ? '' : 's') +
      '</div>',
  });
  activeTip.show();
}
cy.on('mouseover', 'node', evt => {
  if (evt.target.data('is_group')) return;
  evt.target.addClass('hover');
  evt.target.connectedEdges().addClass('hover');
  showTip(evt.target);
});
cy.on('mouseout', 'node', evt => {
  evt.target.removeClass('hover');
  evt.target.connectedEdges().removeClass('hover');
  destroyTip();
});
cy.on('pan zoom drag', destroyTip);

// Search
document.getElementById('search').addEventListener('input', e => {
  const q = e.target.value.trim().toLowerCase();
  if (!q) { cy.elements().removeClass('dimmed'); return; }
  const matches = cy.nodes().filter(n => n.data('label').toLowerCase().includes(q));
  cy.elements().addClass('dimmed');
  matches.removeClass('dimmed');
  matches.connectedEdges().connectedNodes().removeClass('dimmed');
});

// Initial layout + initial selection. Honor `#ClassName` in the URL so
// autodoc pages can deep-link straight into the explorer; fall back to
// `Element` (the root) when the hash is missing or unknown.
cy.ready(() => {
  runLayout();
  const initialId = decodeURIComponent(location.hash.slice(1));
  const requested = initialId ? cy.getElementById(initialId) : cy.collection();
  const start = (requested.length && !requested.data('is_group'))
    ? requested
    : cy.getElementById('Element');
  if (start.length) {
    start.select();
    renderClass(start.data());
    highlightNeighborhood(start);
  }
});

// Sync external hash changes (back button, manually edited URL) into
// the selected class.
window.addEventListener('hashchange', () => {
  const id = decodeURIComponent(location.hash.slice(1));
  if (!id) return;
  const node = cy.getElementById(id);
  if (node.length && !node.data('is_group')) {
    cy.elements().unselect();
    node.select();
    cy.animate({ center: { eles: node }, zoom: 1.3 }, { duration: 350 });
    renderClass(node.data());
    highlightNeighborhood(node);
  }
});

// Re-fit on window resize so iframe size changes don't leave the graph
// stranded in a corner.
let resizeTimer;
window.addEventListener('resize', () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => cy.fit(cy.elements().not('.dimmed'), 30), 150);
});
</script>
</body>
</html>
"""


def write_html(graph: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    html = HTML_TEMPLATE.replace("__GRAPH_JSON__", json.dumps(graph, indent=2))
    out_path.write_text(html)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--github-base",
        default="https://github.com/rebase-energy/EnergyDataModel/blob/main",
        help="Base URL for source links (set to empty string to disable)",
    )
    parser.add_argument(
        "--docs-base",
        default="..",
        help="Relative prefix for autodoc deep links from where the explorer is "
        "served (default: '..' so it works from docs/_static/edm-explorer.html "
        "→ docs/energydatamodel/<module>.html). Pass '' to disable autodoc links.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Override default output paths; if given, writes only this single file.",
    )
    args = parser.parse_args()

    graph = build_graph(args.github_base or None, args.docs_base or None)

    here = Path(__file__).parent
    if args.out is not None:
        targets = [args.out]
    else:
        targets = [
            here / "edm-explorer.html",
            here / "docs" / "_static" / "edm-explorer.html",
        ]

    for path in targets:
        write_html(graph, path)
        print(f"Wrote {path} ({len(graph['nodes'])} classes, {len(graph['edges'])} edges)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
