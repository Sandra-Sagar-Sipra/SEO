"""
Aiquire SEO Machine — Context Files Preview Server
Generates a visual HTML dashboard of all customized context files.
"""

import os
import http.server
import socketserver
import threading
import markdown
from pathlib import Path

CONTEXT_DIR = Path(__file__).parent / "context"
PORT = 8766

# File descriptions for the dashboard
FILE_META = {
    "brand-voice.md":       ("🎙️ Brand Voice",         "Tone, messaging pillars, voice examples, audience profiles"),
    "features.md":          ("⚙️ Features & Services",  "8 services, 4 case studies, pricing, differentiators"),
    "internal-links-map.md":("🔗 Internal Links Map",   "All Aiquire pages mapped with anchor text guidance"),
    "target-keywords.md":   ("🔍 Target Keywords",      "8 keyword clusters, 50+ keywords, competitor gaps"),
    "style-guide.md":       ("✏️ Style Guide",           "British English rules, formatting, terminology"),
    "competitor-analysis.md":("🏆 Competitor Analysis", "6 competitors, content gaps, differentiation opportunities"),
    "seo-guidelines.md":    ("📈 SEO Guidelines",        "Content structure, meta elements, readability rules"),
    "writing-examples.md":  ("📝 Writing Examples",      "Voice reference examples and blog post benchmarks"),
    "cro-best-practices.md":("💡 CRO Best Practices",   "Landing page conversion rules, CTAs, trust signals"),
    "blog-post-template.md":("📄 Blog Post Template",   "6-section template based on Ben's Bites format"),
}

HTML_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Aiquire SEO Machine — Context Files Preview</title>
<style>
  :root {{
    --bg: #0d0d0d;
    --surface: #161616;
    --card: #1e1e1e;
    --border: #2a2a2a;
    --accent: #5b6af0;
    --accent2: #8b5cf6;
    --text: #e8e8e8;
    --muted: #888;
    --code-bg: #121212;
    --tag: #1a2a1a;
    --tag-text: #4ade80;
    --pill: #1a1a2e;
    --pill-text: #818cf8;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.65;
  }}

  /* ── Header ── */
  .header {{
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-bottom: 1px solid var(--border);
    padding: 40px 60px 36px;
  }}
  .header-inner {{ max-width: 1200px; margin: 0 auto; }}
  .brand {{ display: flex; align-items: center; gap: 16px; margin-bottom: 12px; }}
  .brand-dot {{
    width: 12px; height: 12px; border-radius: 50%;
    background: var(--accent); box-shadow: 0 0 12px var(--accent);
  }}
  .brand h1 {{ font-size: 26px; font-weight: 700; letter-spacing: -0.5px; }}
  .brand span {{ color: var(--accent); }}
  .header-sub {{ color: var(--muted); font-size: 15px; margin-left: 28px; }}
  .header-pills {{ display: flex; gap: 10px; margin-top: 20px; flex-wrap: wrap; }}
  .pill {{
    background: var(--pill); color: var(--pill-text);
    padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: 600;
    border: 1px solid #2a2a4a;
  }}
  .pill.green {{ background: #0d2010; color: #4ade80; border-color: #1a4a20; }}
  .pill.amber {{ background: #201800; color: #fbbf24; border-color: #4a3800; }}

  /* ── Layout ── */
  .main {{ max-width: 1200px; margin: 0 auto; padding: 40px 40px 80px; }}

  /* ── Stats bar ── */
  .stats {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 16px; margin-bottom: 40px;
  }}
  .stat-card {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; padding: 20px 24px;
    text-align: center;
  }}
  .stat-num {{ font-size: 28px; font-weight: 700; color: var(--accent); }}
  .stat-label {{ font-size: 12px; color: var(--muted); margin-top: 4px; }}

  /* ── File Grid ── */
  .grid-label {{
    font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px;
    color: var(--muted); margin-bottom: 16px; font-weight: 600;
  }}
  .file-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
    margin-bottom: 48px;
  }}
  .file-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 22px;
    cursor: pointer;
    transition: border-color .2s, transform .15s;
    text-decoration: none; color: inherit;
    display: flex; flex-direction: column; gap: 8px;
  }}
  .file-card:hover {{ border-color: var(--accent); transform: translateY(-2px); }}
  .file-card.active {{ border-color: var(--accent); background: #1a1a2e; }}
  .file-icon {{ font-size: 20px; }}
  .file-name {{
    font-size: 15px; font-weight: 600; color: var(--text);
    display: flex; align-items: center; gap: 8px;
  }}
  .file-desc {{ font-size: 13px; color: var(--muted); line-height: 1.5; }}
  .file-badge {{
    align-self: flex-start;
    background: var(--tag); color: var(--tag-text);
    font-size: 10px; font-weight: 700;
    padding: 2px 8px; border-radius: 4px;
    letter-spacing: 0.5px;
    margin-top: 2px;
  }}

  /* ── Content viewer ── */
  #viewer {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
    display: none;
  }}
  #viewer.open {{ display: block; }}
  .viewer-header {{
    background: var(--card);
    border-bottom: 1px solid var(--border);
    padding: 18px 28px;
    display: flex; align-items: center; justify-content: space-between;
    gap: 16px;
  }}
  .viewer-title {{ font-size: 16px; font-weight: 600; }}
  .viewer-close {{
    background: none; border: 1px solid var(--border);
    color: var(--muted); cursor: pointer;
    padding: 6px 14px; border-radius: 8px;
    font-size: 13px; transition: color .2s, border-color .2s;
  }}
  .viewer-close:hover {{ color: var(--text); border-color: var(--text); }}
  .viewer-body {{ padding: 36px 48px; overflow-x: auto; }}

  /* ── Markdown styling ── */
  .md h1, .md h2, .md h3 {{ color: #e8e8f8; font-weight: 700; margin: 1.6em 0 0.6em; line-height: 1.3; }}
  .md h1 {{ font-size: 24px; border-bottom: 1px solid var(--border); padding-bottom: 12px; }}
  .md h2 {{ font-size: 19px; color: #b0b8ff; }}
  .md h3 {{ font-size: 16px; color: #c4c4f0; }}
  .md p {{ margin: 0.8em 0; color: var(--text); }}
  .md a {{ color: var(--accent); text-decoration: none; }}
  .md a:hover {{ text-decoration: underline; }}
  .md code {{
    background: var(--code-bg); color: #a5f3fc;
    padding: 2px 7px; border-radius: 5px;
    font-family: "JetBrains Mono", "Fira Code", monospace;
    font-size: 13px;
  }}
  .md pre {{
    background: var(--code-bg); border: 1px solid var(--border);
    border-radius: 10px; padding: 20px 24px;
    overflow-x: auto; margin: 1em 0;
  }}
  .md pre code {{ background: none; padding: 0; color: #a5f3fc; }}
  .md ul, .md ol {{ padding-left: 24px; margin: 0.8em 0; }}
  .md li {{ margin: 0.4em 0; color: var(--text); }}
  .md blockquote {{
    border-left: 3px solid var(--accent); padding: 10px 20px;
    background: #12121e; border-radius: 0 8px 8px 0;
    color: var(--muted); margin: 1em 0; font-style: italic;
  }}
  .md table {{
    border-collapse: collapse; width: 100%; margin: 1em 0;
    font-size: 14px;
  }}
  .md th {{
    background: var(--card); color: var(--pill-text);
    padding: 10px 16px; text-align: left;
    border: 1px solid var(--border); font-size: 12px;
    text-transform: uppercase; letter-spacing: 0.5px;
  }}
  .md td {{
    padding: 10px 16px; border: 1px solid var(--border);
    vertical-align: top;
  }}
  .md tr:nth-child(even) td {{ background: #1a1a1a; }}
  .md strong {{ color: #e8e8ff; font-weight: 600; }}
  .md em {{ color: #c4c4e8; }}
  .md hr {{ border: none; border-top: 1px solid var(--border); margin: 2em 0; }}

  /* ── Footer ── */
  .footer {{
    border-top: 1px solid var(--border);
    padding: 28px 40px;
    max-width: 1200px; margin: 0 auto;
    color: var(--muted); font-size: 13px;
    display: flex; justify-content: space-between; align-items: center;
    flex-wrap: wrap; gap: 10px;
  }}
  .footer a {{ color: var(--accent); text-decoration: none; }}
</style>
</head>
<body>

<div class="header">
  <div class="header-inner">
    <div class="brand">
      <div class="brand-dot"></div>
      <h1>Aiquire <span>SEO Machine</span></h1>
    </div>
    <p class="header-sub">Context files customized for Aiquire — AI Consulting &amp; Engineering</p>
    <div class="header-pills">
      <span class="pill green">✅ 10 Files Customized</span>
      <span class="pill">🇬🇧 British English</span>
      <span class="pill">🔍 50+ Target Keywords</span>
      <span class="pill">🏆 6 Competitors Mapped</span>
      <span class="pill amber">📝 Blog Template Ready</span>
      <span class="pill">🔗 Full Links Map</span>
    </div>
  </div>
</div>

<div class="main">
  <!-- Stats -->
  <div class="stats">
    <div class="stat-card"><div class="stat-num">40+</div><div class="stat-label">Production AI Projects</div></div>
    <div class="stat-card"><div class="stat-num">3.2×</div><div class="stat-label">Average ROI in 12mo</div></div>
    <div class="stat-card"><div class="stat-num">92%</div><div class="stat-label">Client Retention Rate</div></div>
    <div class="stat-card"><div class="stat-num">8</div><div class="stat-label">Services Documented</div></div>
    <div class="stat-card"><div class="stat-num">50+</div><div class="stat-label">Target Keywords</div></div>
    <div class="stat-card"><div class="stat-num">10</div><div class="stat-label">Context Files</div></div>
  </div>

  <!-- File cards -->
  <p class="grid-label">Click any file to preview its contents ↓</p>
  <div class="file-grid">
    {file_cards}
  </div>

  <!-- Viewer -->
  <div id="viewer">
    <div class="viewer-header">
      <span class="viewer-title" id="viewer-title">—</span>
      <button class="viewer-close" onclick="closeViewer()">✕ Close</button>
    </div>
    <div class="viewer-body">
      <div class="md" id="viewer-content"></div>
    </div>
  </div>
</div>

<div class="footer">
  <span>Aiquire SEO Machine · Customized March 2026</span>
  <a href="https://aiquire.siprahub.com" target="_blank">aiquire.siprahub.com ↗</a>
</div>

<script>
const contents = {content_map};

function openFile(slug) {{
  const viewer = document.getElementById('viewer');
  document.getElementById('viewer-title').textContent = slug;
  document.getElementById('viewer-content').innerHTML = contents[slug] || '<p>Content not found.</p>';
  viewer.classList.add('open');
  viewer.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
  document.querySelectorAll('.file-card').forEach(c => c.classList.remove('active'));
  document.querySelector(`[data-slug="${{slug}}"]`)?.classList.add('active');
}}

function closeViewer() {{
  document.getElementById('viewer').classList.remove('open');
  document.querySelectorAll('.file-card').forEach(c => c.classList.remove('active'));
}}
</script>
</body>
</html>"""

def build_html():
    # Convert each markdown file to HTML
    content_map = {}
    file_cards = []

    md_converter = markdown.Markdown(extensions=['tables', 'fenced_code', 'nl2br'])

    for filename, (label, desc) in FILE_META.items():
        filepath = CONTEXT_DIR / filename
        if not filepath.exists():
            continue

        raw = filepath.read_text(encoding="utf-8")
        md_converter.reset()
        html_content = md_converter.convert(raw)
        content_map[filename] = html_content.replace("`", "\\`").replace("${", "\\${")

        # Badge
        if "FULLY REWRITTEN" in raw or filename == "blog-post-template.md":
            badge = "✅ CUSTOMIZED"
        elif "UPDATED" in raw.upper() or "aiquire" in raw.lower():
            badge = "✅ UPDATED"
        else:
            badge = "📄 INCLUDED"

        icon = label.split()[0]
        title = " ".join(label.split()[1:])
        wc = len(raw.split())

        card = f"""<div class="file-card" data-slug="{filename}" onclick="openFile('{filename}')">
  <div class="file-icon">{icon}</div>
  <div class="file-name">{title}</div>
  <div class="file-desc">{desc}</div>
  <div style="display:flex;gap:8px;align-items:center;margin-top:4px;">
    <span class="file-badge">{badge}</span>
    <span style="font-size:11px;color:var(--muted)">~{wc:,} words</span>
  </div>
</div>"""
        file_cards.append(card)

    # Build JS content map
    js_map_parts = []
    for slug, html in content_map.items():
        safe = html.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
        js_map_parts.append(f'"{slug}": `{safe}`')
    js_map = "{" + ", ".join(js_map_parts) + "}"

    return HTML_SHELL.format(
        file_cards="\n    ".join(file_cards),
        content_map=js_map
    )


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            content = build_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # suppress access logs


if __name__ == "__main__":
    # Write static HTML file
    out_path = Path(__file__).parent / "output" / "context-preview.html"
    out_path.parent.mkdir(exist_ok=True)
    html = build_html()
    out_path.write_text(html, encoding="utf-8")
    print(f"[OK] Static HTML saved -> {out_path}")

    # Start server
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"[SERVER] Preview running at {url}")
        print(f"   Press Ctrl+C to stop\n")
        httpd.serve_forever()
