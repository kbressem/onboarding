"""MkDocs hooks for the onboarding site.

1. Renders form-field markers (`field:text`, `field:date`, `field:choice:A; B`,
   `field:check`, `field:photo`) as empty boxes on the website. The Word build
   turns the same markers into fillable content controls (build/filters/docx.lua).
2. Shows the front matter subtitle below the page title.
3. Adds a "Word version" button to every page that has a DOCX download.
"""

import html
import re

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


def on_page_markdown(markdown, page, config, files):
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
    return markdown
