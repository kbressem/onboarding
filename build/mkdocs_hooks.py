"""MkDocs hooks for the onboarding site.

1. Renders form-field markers (`field:text`, `field:date`, `field:choice:A; B`,
   `field:check`, `field:photo`) as empty boxes on the website. The Word build
   turns the same markers into fillable content controls (build/filters/docx.lua).
2. Shows the front matter subtitle below the page title.
3. Adds a "Word version" button to every page that has a DOCX download.
4. Shows the date of the last change (git commit date, else the build date).
5. Removes HTML comments (TODO notes) from the published pages.
"""

import datetime as dt
import html
import re
import subprocess
from pathlib import Path

FIELD = re.compile(r"`field:([a-z]+):?([^`]*)`")


def _field_html(match):
    kind, arg = match.group(1), match.group(2).strip()
    if kind == "text":
        hint = html.escape(arg) if arg else "&nbsp;"
        return f'<span class="ff ff-text">{hint}</span>'
    if kind == "date":
        return '<span class="ff ff-date">TT.MM.JJJJ / DD.MM.YYYY</span>'
    if kind == "choice":
        opts = [html.escape(o.strip()) for o in arg.split(";") if o.strip()]
        return " ".join(f'<span class="ff-opt">&#9744; {o}</span>' for o in opts)
    if kind == "check":
        return '<span class="ff-opt">&#9744;</span>'
    if kind == "photo":
        return '<span class="ff ff-photo">Foto / Photo</span>'
    return match.group(0)


def _last_change(path):
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", Path(path).name],
                             cwd=Path(path).parent, capture_output=True, text=True,
                             check=True).stdout.strip()
        if out:
            return out
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        pass
    return dt.date.today().isoformat()


def on_page_markdown(markdown, page, config, files):
    markdown = re.sub(r"<!--.*?-->", "", markdown, flags=re.S)   # TODO notes stay in the source
    markdown = FIELD.sub(_field_html, markdown)
    subtitle = page.meta.get("subtitle")
    if subtitle:
        markdown = f'<p class="page-subtitle">{html.escape(str(subtitle))}</p>\n\n' + markdown
    if page.meta.get("docx", True) is not False:
        src = page.file.src_uri
        depth = src.count("/")
        target = "../" * depth + "downloads/" + src[:-3] + ".docx"
        button = (f'[:material-microsoft-word: Word version]({target})'
                  '{ .md-button .docx-button }\n\n')
        markdown = button + markdown
    if page.file.abs_src_path:
        markdown += f'\n\n<p class="page-date">Last change {_last_change(page.file.abs_src_path)}</p>\n'
    return markdown
