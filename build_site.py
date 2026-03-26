import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


IN_FILE = Path("data/threads.json")
OUT_DIR = Path("site")
OUT_FILE = OUT_DIR / "index.html"


def main() -> None:
    if not IN_FILE.exists():
        raise SystemExit("Missing data/threads.json. Run: python scrape_threads.py")

    data = json.loads(IN_FILE.read_text(encoding="utf-8"))
    threads = data.get("threads", [])
    topic_counts = Counter(t.get("topic_group", "Other") for t in threads)

    base_url = os.getenv("SITE_BASE_URL", "https://febinalex.github.io/samsungf54").rstrip("/")
    page_url = f"{base_url}/"
    image_url = f"{base_url}/og-image.svg"
    now_iso = datetime.now(timezone.utc).isoformat()
    modified_iso = data.get("generated_at_utc") or now_iso

    payload = {
        "generated_at_utc": data.get("generated_at_utc"),
        "total_links": data.get("total_links", len(threads)),
        "total_threads": len(threads),
        "total_messages": sum(len(t.get("messages", [])) for t in threads),
        "total_replies": sum(max(len(t.get("messages", [])) - 1, 0) for t in threads),
        "total_views": sum(t.get("views", 0) for t in threads),
        "topics": dict(topic_counts),
        "threads": threads,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(
        render_html(payload, page_url=page_url, image_url=image_url, modified_iso=modified_iso),
        encoding="utf-8",
    )
    write_robots(base_url)
    write_sitemap(page_url, modified_iso)
    write_manifest()
    write_og_image(payload)
    print(f"Wrote {OUT_FILE}")
    print(f"Wrote {OUT_DIR / 'robots.txt'}")
    print(f"Wrote {OUT_DIR / 'sitemap.xml'}")
    print(f"Wrote {OUT_DIR / 'manifest.webmanifest'}")
    print(f"Wrote {OUT_DIR / 'og-image.svg'}")


def write_robots(base_url: str) -> None:
    content = (
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {base_url}/sitemap.xml\n"
    )
    (OUT_DIR / "robots.txt").write_text(content, encoding="utf-8")


def write_sitemap(page_url: str, modified_iso: str) -> None:
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{xml_escape(page_url)}</loc>
    <lastmod>{xml_escape(modified_iso)}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>
</urlset>
"""
    (OUT_DIR / "sitemap.xml").write_text(content, encoding="utf-8")


def write_manifest() -> None:
    manifest = {
        "name": "Samsung Galaxy F54 Display Complaint Board",
        "short_name": "F54 Complaints",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#f4f7fb",
        "theme_color": "#0f766e",
        "description": (
            "Publicly indexed complaint board tracking Samsung Galaxy F54 "
            "display green and pink line issue threads and replies."
        ),
        "icons": [],
    }
    (OUT_DIR / "manifest.webmanifest").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def write_og_image(payload: dict) -> None:
    threads = payload.get("total_threads", 0)
    replies = payload.get("total_replies", 0)
    title = "Samsung Galaxy F54"
    subtitle = "Display Green/Pink Line Complaints"
    stat_text = f"Threads: {threads}   Replies: {replies}"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#fff5f5"/>
      <stop offset="100%" stop-color="#ecfeff"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#g)"/>
  <rect x="55" y="60" width="1090" height="510" rx="24" fill="#ffffff" stroke="#d9e2ec" stroke-width="3"/>
  <text x="95" y="180" font-size="58" font-family="Segoe UI, Arial, sans-serif" font-weight="700" fill="#0f172a">{xml_escape(title)}</text>
  <text x="95" y="250" font-size="46" font-family="Segoe UI, Arial, sans-serif" font-weight="700" fill="#b91c1c">{xml_escape(subtitle)}</text>
  <text x="95" y="340" font-size="34" font-family="Segoe UI, Arial, sans-serif" fill="#0f766e">{xml_escape(stat_text)}</text>
  <text x="95" y="420" font-size="27" font-family="Segoe UI, Arial, sans-serif" fill="#475569">Community thread archive with posts and replies</text>
</svg>
"""
    (OUT_DIR / "og-image.svg").write_text(svg, encoding="utf-8")


def render_html(payload: dict, page_url: str, image_url: str, modified_iso: str) -> str:
    json_blob = json.dumps(payload, ensure_ascii=False)
    title = "Samsung Galaxy F54 Green Line and Pink Line Display Issue Complaints"
    description = (
        f"Track {payload.get('total_threads', 0)} public Samsung Galaxy F54 display complaint threads "
        f"and {payload.get('total_replies', 0)} replies related to green line and pink line issues."
    )
    keywords = (
        "Samsung F54 green line issue, Samsung F54 pink line issue, "
        "Samsung display line complaint, Galaxy F54 screen issue, Samsung community complaints"
    )
    web_json_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Samsung Galaxy F54 Display Complaint Board",
            "url": page_url,
            "description": description,
            "inLanguage": "en",
        },
        ensure_ascii=False,
    )
    dataset_json_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "name": "Samsung Galaxy F54 Display Issue Complaint Dataset",
            "description": description,
            "url": page_url,
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "isAccessibleForFree": True,
            "dateModified": modified_iso,
            "keywords": [
                "Samsung Galaxy F54",
                "Green line issue",
                "Pink line issue",
                "Display complaints",
            ],
        },
        ensure_ascii=False,
    )

    template = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>__TITLE__</title>
  <meta name="description" content="__DESCRIPTION__" />
  <meta name="keywords" content="__KEYWORDS__" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
  <meta name="author" content="Samsung Galaxy F54 Complaint Tracker" />
  <meta name="theme-color" content="#0f766e" />
  <meta name="referrer" content="strict-origin-when-cross-origin" />
  <meta name="format-detection" content="telephone=no" />
  <link rel="canonical" href="__PAGE_URL__" />
  <link rel="manifest" href="/manifest.webmanifest" />
  <link rel="sitemap" type="application/xml" href="/sitemap.xml" />

  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Samsung Galaxy F54 Complaint Board" />
  <meta property="og:title" content="__TITLE__" />
  <meta property="og:description" content="__DESCRIPTION__" />
  <meta property="og:url" content="__PAGE_URL__" />
  <meta property="og:image" content="__IMAGE_URL__" />
  <meta property="og:image:alt" content="Samsung Galaxy F54 display issue complaint board preview" />
  <meta property="og:locale" content="en_US" />

  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="__TITLE__" />
  <meta name="twitter:description" content="__DESCRIPTION__" />
  <meta name="twitter:image" content="__IMAGE_URL__" />

  <script type="application/ld+json">__WEB_JSON_LD__</script>
  <script type="application/ld+json">__DATASET_JSON_LD__</script>

  <style>
    :root {
      --bg: #f4f7fb;
      --card: #ffffff;
      --text: #0f172a;
      --muted: #475569;
      --line: #d9e2ec;
      --brand: #0f766e;
      --brand-soft: #ccfbf1;
      --alert: #b91c1c;
      --alert-soft: #fee2e2;
      --post: #fff7ed;
      --post-line: #fdba74;
      --reply: #f8fafc;
      --reply-line: #93c5fd;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background:
        radial-gradient(circle at 0 0, #ffe5e5 0, transparent 28%),
        radial-gradient(circle at 100% 0, #ddfff7 0, transparent 24%),
        var(--bg);
      color: var(--text);
    }
    .msg-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;
    }
    .avatar {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: #e2e8f0;
      flex-shrink: 0;
      object-fit: cover;
    }
    .kudos {
      font-size: 11px;
      color: #7c2d12;
      background: #ffedd5;
      padding: 1px 6px;
      border-radius: 4px;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 3px;
    }
    .solution-mark {
      color: #15803d;
      background: #dcfce7;
      padding: 2px 8px;
      border-radius: 6px;
      font-weight: 700;
      font-size: 11px;
      text-transform: uppercase;
      border: 1px solid #bbf7d0;
      margin-left: 8px;
    }
    .view-count {
      color: var(--muted);
      font-size: 11px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .container {
      max-width: 1120px;
      margin: 0 auto;
      padding: 18px 14px 28px;
    }
    .hero {
      border: 1px solid var(--line);
      border-radius: 16px;
      background: linear-gradient(120deg, #fff, #fff5f5, #ecfeff);
      padding: 16px;
      margin-bottom: 14px;
    }
    h1 {
      margin: 0 0 6px;
      font-size: 30px;
      line-height: 1.1;
    }
    .sub {
      margin: 0;
      color: var(--muted);
      font-size: 14px;
    }
    .stats {
      margin-top: 12px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 8px;
    }
    .stat {
      border: 1px solid var(--line);
      border-radius: 10px;
      background: #fff;
      padding: 10px;
    }
    .stat b {
      display: block;
      font-size: 22px;
      line-height: 1;
      margin-bottom: 4px;
    }
    .controls {
      display: grid;
      grid-template-columns: 1.4fr 0.8fr 0.8fr;
      gap: 10px;
      margin-bottom: 12px;
    }
    input, select {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 10px 12px;
      font-size: 14px;
      background: #fff;
      color: var(--text);
    }
    .topic-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 12px;
    }
    .topic-chip {
      font-size: 12px;
      border-radius: 999px;
      border: 1px solid #dbeafe;
      background: #eff6ff;
      color: #1e3a8a;
      padding: 3px 9px;
    }
    .thread {
      border: 1px solid var(--line);
      border-radius: 14px;
      background: var(--card);
      margin-bottom: 12px;
      overflow: hidden;
    }
    .thread-head {
      padding: 12px 13px;
      border-bottom: 1px solid var(--line);
      background: #f8fafc;
    }
    .title {
      margin: 0 0 6px;
      font-size: 18px;
      line-height: 1.2;
    }
    .meta {
      color: var(--muted);
      font-size: 12px;
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }
    .badge {
      border-radius: 999px;
      padding: 2px 8px;
      font-size: 11px;
      border: 1px solid transparent;
      font-weight: 700;
      letter-spacing: .02em;
      text-transform: uppercase;
    }
    .badge-alert {
      background: var(--alert-soft);
      color: var(--alert);
      border-color: #fecaca;
    }
    .badge-brand {
      background: var(--brand-soft);
      color: var(--brand);
      border-color: #99f6e4;
    }
    .body {
      padding: 12px 13px;
    }
    .post {
      border: 1px solid var(--post-line);
      border-left: 6px solid var(--post-line);
      border-radius: 10px;
      background: var(--post);
      padding: 10px;
      margin-bottom: 10px;
    }
    .post-label {
      font-size: 11px;
      font-weight: 700;
      color: #9a3412;
      text-transform: uppercase;
      margin-bottom: 5px;
      letter-spacing: .02em;
    }
    .msg-meta {
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 5px;
    }
    .msg-text {
      font-size: 14px;
      line-height: 1.5;
      white-space: pre-wrap;
      word-break: break-word;
    }
    details.replies {
      border: 1px solid var(--line);
      border-radius: 10px;
      background: #fff;
      overflow: hidden;
    }
    details.replies > summary {
      list-style: none;
      cursor: pointer;
      padding: 10px 12px;
      background: #f8fafc;
      border-bottom: 1px solid var(--line);
      font-size: 13px;
      font-weight: 700;
      color: #0f766e;
    }
    details.replies > summary::-webkit-details-marker { display: none; }
    .reply-list { padding: 0 10px 10px; }
    .reply {
      border: 1px solid #dbeafe;
      border-left: 5px solid var(--reply-line);
      border-radius: 10px;
      background: var(--reply);
      padding: 9px;
      margin-top: 9px;
    }
    .reply-label {
      font-size: 11px;
      font-weight: 700;
      color: #1d4ed8;
      margin-bottom: 4px;
      text-transform: uppercase;
      letter-spacing: .02em;
    }
    .muted { color: var(--muted); }
    .empty {
      padding: 14px;
      border: 1px dashed var(--line);
      border-radius: 10px;
      color: var(--muted);
      background: #fff;
      font-style: italic;
    }
    a { color: #0369a1; text-decoration: none; }
    a:hover { text-decoration: underline; }
    @media (max-width: 860px) {
      .controls { grid-template-columns: 1fr; }
      h1 { font-size: 24px; }
    }
  </style>
</head>
<body>
  <div class="container">
    <section class="hero">
      <h1>Samsung Galaxy F54 Display Complaint Board</h1>
      <p class="sub">Public Samsung Community complaints focused on F54 green/pink display line problems, with original posts and replies clearly separated.</p>
      <div class="stats" id="stats"></div>
    </section>

    <section class="controls">
      <input id="q" placeholder="Search complaint title, post text, reply text, author, thread id..." />
      <select id="topicFilter"></select>
      <select id="sortBy">
        <option value="replies_desc">Sort: Most Replies</option>
        <option value="new_desc">Sort: Newest Post Time</option>
        <option value="old_asc">Sort: Oldest Post Time</option>
      </select>
    </section>

    <section class="topic-row" id="topicRow"></section>
    <main id="root"></main>
  </div>

  <script>
    const DATA = __JSON_BLOB__;
    const root = document.getElementById("root");
    const stats = document.getElementById("stats");
    const q = document.getElementById("q");
    const topicFilter = document.getElementById("topicFilter");
    const sortBy = document.getElementById("sortBy");
    const topicRow = document.getElementById("topicRow");

    const statItems = [
      ["Threads", DATA.total_threads || 0],
      ["Posts + Replies", DATA.total_messages || 0],
      ["Replies", DATA.total_replies || 0],
      ["Total Views", DATA.total_views || 0],
    ];
    stats.innerHTML = statItems.map(([k, v]) => `<div class="stat"><b>${v >= 1000 ? (v/1000).toFixed(1) + 'k' : esc(v)}</b>${esc(k)}</div>`).join("");

    const topics = Object.keys(DATA.topics || {}).sort((a, b) => a.localeCompare(b));
    topicFilter.innerHTML = `<option value="">All Topics</option>` +
      topics.map(t => `<option value="${escAttr(t)}">${esc(t)} (${DATA.topics[t] || 0})</option>`).join("");
    topicRow.innerHTML = topics.map(t => `<span class="topic-chip">${esc(t)}: ${DATA.topics[t] || 0}</span>`).join("");

    function toTs(v) {
      const t = Date.parse(v || "");
      return Number.isNaN(t) ? 0 : t;
    }

    function render() {
      const query = (q.value || "").trim().toLowerCase();
      const topic = topicFilter.value;
      const sorter = sortBy.value;

      let items = (DATA.threads || []).slice();
      if (topic) items = items.filter(t => (t.topic_group || "") === topic);
      if (query) {
        items = items.filter(t => {
          const corpus = [
            t.title || "",
            t.topic_group || "",
            t.group || "",
            t.thread_id || "",
            t.url || "",
            ...(t.messages || []).map(m => (m.author || "") + " " + (m.subject || "") + " " + (m.text || ""))
          ].join(" ").toLowerCase();
          return corpus.includes(query);
        });
      }

      items.sort((a, b) => {
        const ar = Math.max((a.messages || []).length - 1, 0);
        const br = Math.max((b.messages || []).length - 1, 0);
        const at = toTs((a.messages || [])[0]?.published);
        const bt = toTs((b.messages || [])[0]?.published);
        if (sorter === "new_desc") return bt - at;
        if (sorter === "old_asc") return at - bt;
        return br - ar || bt - at;
      });

      if (!items.length) {
        root.innerHTML = `<div class="empty">No threads match the current filter.</div>`;
        return;
      }

      root.innerHTML = items.map((t, idx) => renderThread(t, idx)).join("");
    }

    function renderThread(t, idx) {
      const msgs = t.messages || [];
      const rootPost = msgs.find(m => m.source === "root") || msgs[0];
      const replies = msgs.filter(m => m !== rootPost);
      const openAttr = idx < 2 ? " open" : "";

      const postHtml = rootPost ? renderMessage(rootPost, "Original Complaint", "post") : `<div class="empty">Original post text unavailable.</div>`;

      const replyHtml = replies.length
        ? replies.map((r, i) => renderMessage(r, `Reply ${i + 1}`, "reply")).join("")
        : `<div class="empty">No replies found for this thread.</div>`;

      return `
        <section class="thread">
          <header class="thread-head">
            <h2 class="title">${esc(t.title || "Untitled")}</h2>
            <div class="meta">
              <span class="badge badge-alert">${esc(t.topic_group || "Issue")}</span>
              <span class="badge badge-brand">${replies.length} replies</span>
              <span class="view-count" title="Total thread views">👁️ ${esc(t.views || 0)}</span>
              <span>${esc(t.group || "Unknown group")}</span>
              <span>ID: ${esc(t.thread_id || "N/A")}</span>
              <span><a href="${escAttr(t.url || "#")}" target="_blank" rel="noopener noreferrer">Source Thread ↗</a></span>
            </div>
          </header>
          <div class="body">
            ${postHtml}
            <details class="replies"${openAttr}>
              <summary>Replies (${replies.length}) - click to show/hide</summary>
              <div class="reply-list">${replyHtml}</div>
            </details>
          </div>
        </section>
      `;
    }

    function renderMessage(m, label, className) {
      const solutionHtml = m.is_solution ? `<span class="solution-mark">✅ Solution</span>` : "";
      const avatarHtml = m.author_avatar ? `<img class="avatar" src="${escAttr(m.author_avatar)}" alt="" loading="lazy">` : `<div class="avatar"></div>`;
      const kudosHtml = m.kudos > 0 ? `<span class="kudos" title="${m.kudos} kudos">❤️ ${m.kudos}</span>` : "";
      const permalinkHtml = m.url ? `<a href="${escAttr(m.url)}" target="_blank" class="muted" style="font-size:10px; margin-left:auto;">permalink ↗</a>` : "";

      return `
        <article class="${className}">
          <div class="post-label">${esc(label)} ${solutionHtml}</div>
          <div class="msg-header">
            ${avatarHtml}
            <div class="msg-meta" style="margin-bottom:0">
              <b>${esc(m.author || "Unknown")}</b> | ${esc(m.published || "Unknown time")}
              ${kudosHtml}
            </div>
            ${permalinkHtml}
          </div>
          <div class="msg-text">${esc(m.text || "")}</div>
        </article>
      `;
    }

    function esc(v) {
      return String(v ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }

    function escAttr(v) {
      return esc(v).replace(/`/g, "");
    }

    q.addEventListener("input", render);
    topicFilter.addEventListener("change", render);
    sortBy.addEventListener("change", render);
    render();
  </script>
</body>
</html>
"""
    return (
        template.replace("__JSON_BLOB__", json_blob)
        .replace("__TITLE__", html_escape_attr(title))
        .replace("__DESCRIPTION__", html_escape_attr(description))
        .replace("__KEYWORDS__", html_escape_attr(keywords))
        .replace("__PAGE_URL__", html_escape_attr(page_url))
        .replace("__IMAGE_URL__", html_escape_attr(image_url))
        .replace("__WEB_JSON_LD__", web_json_ld)
        .replace("__DATASET_JSON_LD__", dataset_json_ld)
    )


def html_escape_attr(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def xml_escape(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


if __name__ == "__main__":
    main()
