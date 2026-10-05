# Lab onboarding

This repository has the onboarding documents for the group of Keno Bressem in Essen (NCT West, DKFZ) and Munich (TUM Klinikum). The Markdown files in `docs/` are the only source. A GitHub Action makes a Word file from each page and builds a website with a search function.

| Path | Content |
|---|---|
| `docs/essen.md`, `docs/tum.md` | Main guides, two pages or less each |
| `docs/reference/` | More information for the guides (employers, business trips, IT, RadCat, compute) |
| `docs/forms/` | Forms in German and English, with Word fields |
| `OPEN_ITEMS.md` | Information that is not available yet |

The English text follows ASD-STE100 (Simplified Technical English). Refer to [CONTRIBUTING.md](CONTRIBUTING.md).

## Change a document

1. Change the Markdown file on github.com (pencil icon) or on your computer.
2. Commit the change to `main` or open a pull request.
3. The Action "Build documents" makes the Word files and the website.

You can get the Word files from three locations.

- The artifact `onboarding-docx` of each Action run.
- The button "Word version" on each page of the website.
- The release for a tag, for example `v2026.10`.

Do not change the Word files. The next build replaces them. For the rules for the text, the form fields and new pages, refer to [CONTRIBUTING.md](CONTRIBUTING.md).

## Word build

1. pandoc reads the Markdown.
2. `templates/reference.docx` gives the styles (Arial, NCT colors, A4).
3. `build/filters/docx.lua` changes the form markers into Word content controls.
4. `build/build_docx.py` adds the header, the footer with the version date and page numbers, the table widths and the table colors.
5. `build/ooxml_fix.py` corrects the XML. The Word files then agree with the OOXML schema.

To change the styles, change the values in `build/make_reference_docx.py`. Then run `make reference` and commit the new `templates/reference.docx`.

## Local preview

You must have [pandoc](https://pandoc.org/installing.html) 3.x and Python 3.10 or newer. On a Mac, install pandoc with `brew install pandoc`.

Make a Python environment in the repository one time.

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then use these commands in the activated environment.

```
make serve        # Word files and live website at http://127.0.0.1:8000
make docx         # Word files only, in docs/downloads/
make lint         # ASD-STE100 check of the English text
```

If MkDocs cannot find a plugin or a theme, activate the environment and run `pip install -r requirements.txt` again.

If the Word build shows "bad CPU type in executable", your pandoc is for a different processor. On a Mac with Apple silicon, remove the Intel pandoc and install the arm64 pandoc (`brew install pandoc`). The build script shows the full procedure. To use a specific pandoc, set the variable `PANDOC`, for example `PANDOC=/opt/homebrew/bin/pandoc make docx`. To see only the website without Word files, use `python3 -m mkdocs serve`.

## Setup on GitHub

Do these steps one time.

1. Make a private repository in the institutional organization. Push this folder.
2. In Settings, Pages, set the source to "GitHub Actions".
3. In Settings, Secrets and variables, Actions, Variables, set `SITE_URL` to the Pages address. The Word files also use this address for their links.
4. To publish the website, set the variable `PAGES_ENABLED` to `true`.

Set `PAGES_ENABLED` only if the organization uses GitHub Enterprise Cloud and the Pages visibility is private. On all other plans, a Pages site is public, also from a private repository. This site has internal contacts, host names and IP addresses. If you do not set the variable, the Action makes only the Word files.

## Rules

Do not add passwords, links with access tokens, patient data or personal data of the persons in the group. Only work contacts are permitted. If you must have a group password (for example for the DKFZ hotel link), Keno sends it to you.
