"""
Builds the _site/ directory deployed to GitHub Pages.

Copies cockpit-data/ as-is, then:
  - injects an "Archive" dropdown (sorted newest-first) into every
    cockpit-YYYY-MM-DD.html file, replacing the <!--ARCHIVE_OPTIONS--> marker
  - regenerates cockpit-data/latest.html to redirect to the newest edition
  - regenerates index.html to redirect to latest.html

Run from the repository root: python3 scripts/build_pages_site.py
"""
import datetime
import re
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE = REPO_ROOT / "_site"
SITE_DATA = SITE / "cockpit-data"
DATA = REPO_ROOT / "cockpit-data"

EDITION_RE = re.compile(r"^cockpit-(\d{4}-\d{2}-\d{2})\.html$")


def build():
    SITE.mkdir(parents=True, exist_ok=True)
    SITE_DATA.mkdir(parents=True, exist_ok=True)

    for pattern in ("*.html", "*.csv", "*.xlsx"):
        for f in DATA.glob(pattern):
            shutil.copy2(f, SITE_DATA / f.name)

    editions = []
    for f in SITE_DATA.glob("cockpit-*.html"):
        m = EDITION_RE.match(f.name)
        if m:
            editions.append((m.group(1), f.name))
    editions.sort(reverse=True)  # newest date first

    if not editions:
        raise SystemExit("No cockpit-YYYY-MM-DD.html files found in cockpit-data/")

    print(f"Found {len(editions)} edition(s); latest is {editions[0][1]}")

    option_rows = []
    for date_str, fname in editions:
        d = datetime.date.fromisoformat(date_str)
        label = d.strftime("%B %-d, %Y")
        option_rows.append((fname, label))

    for date_str, fname in editions:
        path = SITE_DATA / fname
        content = path.read_text(encoding="utf-8")
        opts_html = "\n          ".join(
            f'<option value="./{opt_fname}"{" selected" if opt_fname == fname else ""}>{label}</option>'
            for opt_fname, label in option_rows
        )
        content = content.replace("<!--ARCHIVE_OPTIONS-->", opts_html)
        path.write_text(content, encoding="utf-8")

    latest_fname = editions[0][1]
    latest_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=./{latest_fname}">
  <title>Industry Intelligence Cockpit — Latest Edition</title>
</head>
<body style="font-family:Inter,Arial,sans-serif;background:#F7F8FA;color:#00294D;padding:40px;">
  <p>Redirecting to the latest edition&hellip; If you are not redirected, <a href="./{latest_fname}">click here</a>.</p>
</body>
</html>
"""
    (SITE_DATA / "latest.html").write_text(latest_html, encoding="utf-8")

    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=./cockpit-data/latest.html">
  <title>Industry Intelligence Cockpit</title>
</head>
<body style="font-family:Inter,Arial,sans-serif;background:#F7F8FA;color:#00294D;padding:40px;">
  <p>Redirecting to the latest edition&hellip; If you are not redirected, <a href="./cockpit-data/latest.html">click here</a>.</p>
</body>
</html>
"""
    (SITE / "index.html").write_text(index_html, encoding="utf-8")

    print(f"Built _site/ with {len(editions)} archived edition(s)")


if __name__ == "__main__":
    build()
