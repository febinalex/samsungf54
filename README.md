# Samsung Community Link Aggregator

This project fetches Samsung Community thread pages and builds a local website that groups threads and extracted messages.

## Files
- `links.txt`: input links (one per line)
- `scrape_threads.py`: fetches and extracts content into `data/threads.json`
- `build_site.py`: builds `site/index.html` from extracted JSON
- `site/index.html`: generated website

## Usage
1. Put your links in `links.txt`
2. Run:
   python scrape_threads.py
   python build_site.py
3. Open `site/index.html` in a browser

## SEO Setup (Important for Google indexing)
Before building the site for hosting, set your final domain:

PowerShell:
`$env:SITE_BASE_URL="https://your-domain.com"`

Then build:
`python build_site.py`

This generates SEO files inside `site/`:
- `index.html` with meta tags, Open Graph, Twitter cards, canonical, and JSON-LD
- `robots.txt`
- `sitemap.xml`
- `manifest.webmanifest`
- `og-image.svg`

After hosting, submit your sitemap in Google Search Console:
- `https://your-domain.com/sitemap.xml`

## Notes
- Extraction is heuristic because forum HTML can vary.
- The website keeps source links so you can jump to original posts.
