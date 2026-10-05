#!/usr/bin/env python3
"""Create templates/reference.docx, the Word style template used by pandoc.

The design lives in this script so that changes are reviewable in Git.
Run it again after editing the constants below:

    python3 build/make_reference_docx.py

Colours follow the NCT corporate colours (Pantone 287 / 285), which are close
to TUM blue. Arial is the NCT office font and is available on every system.
"""

import subprocess
import tempfile
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from ooxml_fix import fix_docx

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "templates" / "reference.docx"

FONT = "Arial"
MONO = "Consolas"
DARK = "00186E"    # NCT dark blue (Pantone 287)
BLUE = "3273C3"    # NCT blue (Pantone 285)
LIGHT = "EAF1FA"   # very light blue for call-outs
TEXT = "1F1F1F"
GREY = "6B6B6B"


def rgb(hex_):
    return RGBColor.from_string(hex_)


def set_fonts(rpr, name):
    """Replace theme fonts by an explicit font in a w:rPr element."""
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in list(rfonts.attrib):
        if attr.endswith("Theme"):
            del rfonts.attrib[attr]
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), name)


def p_border(style, side, color, size=12, space=4):
    ppr = style.element.get_or_add_pPr()
    bdr = ppr.find(qn("w:pBdr"))
    if bdr is None:
        bdr = OxmlElement("w:pBdr")
        ppr.append(bdr)
    el = OxmlElement(f"w:{side}")
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), str(size))
    el.set(qn("w:space"), str(space))
    el.set(qn("w:color"), color)
    bdr.append(el)


def p_shading(style, fill):
    ppr = style.element.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    ppr.append(shd)


def para(style, size=None, color=None, bold=None, before=None, after=None,
         line=None, keep_next=None, font=None):
    if size is not None:
        style.font.size = Pt(size)
    if color is not None:
        style.font.color.rgb = rgb(color)
    if bold is not None:
        style.font.bold = bold
    if font is not None:
        set_fonts(style.element.get_or_add_rPr(), font)
    pf = getattr(style, "paragraph_format", None)
    if pf is not None:
        if before is not None:
            pf.space_before = Pt(before)
        if after is not None:
            pf.space_after = Pt(after)
        if line is not None:
            pf.line_spacing = line
        if keep_next is not None:
            pf.keep_with_next = keep_next


def get_style(doc, name, kind=WD_STYLE_TYPE.PARAGRAPH, base=None):
    """Find a style by its name as written in the file (pandoc capitalises
    built-in names such as "Heading 1", which python-docx lookups miss)."""
    for st in doc.styles:
        if st.name == name:
            return st
    try:
        return doc.styles[name]
    except KeyError:
        st = doc.styles.add_style(name, kind)
        if base:
            st.base_style = doc.styles[base]
        return st


def main():
    with tempfile.TemporaryDirectory() as tmp:
        default = Path(tmp) / "default.docx"
        with open(default, "wb") as fh:
            subprocess.run(
                ["pandoc", "--print-default-data-file", "reference.docx"],
                stdout=fh, check=True)
        doc = Document(default)

    # Explicit fonts everywhere (theme fonts would override Arial).
    for rfonts in doc.styles.element.iter(qn("w:rFonts")):
        for attr in list(rfonts.attrib):
            if attr.endswith("Theme"):
                del rfonts.attrib[attr]
        for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rfonts.set(qn(attr), FONT)
    defaults = doc.styles.element.find(qn("w:docDefaults"))
    set_fonts(defaults.find(qn("w:rPrDefault")).find(qn("w:rPr")), FONT)

    class _S:
        def __getitem__(self, name):
            return get_style(doc, name)
    s = _S()
    para(s["Normal"], size=10, color=TEXT, after=4, line=1.15, font=FONT)
    for name in ("Body Text", "First Paragraph"):
        para(s[name], size=10, before=0, after=6)
    para(s["Compact"], size=10, before=0, after=2)

    para(s["Title"], size=20, color=DARK, bold=True, before=0, after=4, line=1.0)
    p_border(s["Title"], "bottom", BLUE, size=12, space=6)
    s["Title"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    para(get_style(doc, "Subtitle", base="Title"), size=11, color=GREY,
         bold=False, before=2, after=2)
    for name in ("Author", "Date"):
        para(get_style(doc, name), size=9, color=GREY, before=0, after=0)
    s["Subtitle"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    # The subtitle inherits the title rule; remove it.
    sub_ppr = s["Subtitle"].element.get_or_add_pPr()
    for bdr in sub_ppr.findall(qn("w:pBdr")):
        sub_ppr.remove(bdr)

    para(s["Heading 1"], size=13, color=DARK, bold=True, before=14, after=4,
         keep_next=True, font=FONT)
    para(s["Heading 2"], size=11, color=BLUE, bold=True, before=10, after=3,
         keep_next=True, font=FONT)
    para(s["Heading 3"], size=10, color=TEXT, bold=True, before=8, after=2,
         keep_next=True, font=FONT)
    for name in ("Heading 1", "Heading 2", "Heading 3"):
        s[name].font.italic = False

    # Block quotes are used as call-outs.
    bt = s["Block Text"]
    para(bt, size=10, color=TEXT, before=6, after=8, font=FONT)
    bt.font.italic = False
    bt.paragraph_format.left_indent = Cm(0.2)
    bt.paragraph_format.right_indent = Cm(0.2)
    p_border(bt, "left", BLUE, size=18, space=8)
    p_shading(bt, LIGHT)

    hl = get_style(doc, "Hyperlink", WD_STYLE_TYPE.CHARACTER)
    hl.font.color.rgb = rgb(BLUE)
    hl.font.underline = False

    vc = get_style(doc, "Verbatim Char", WD_STYLE_TYPE.CHARACTER)
    set_fonts(vc.element.get_or_add_rPr(), MONO)
    vc.font.size = Pt(9)
    sc = get_style(doc, "Source Code", base="Normal")
    para(sc, size=8.5, before=4, after=6, line=1.0, font=MONO)
    p_shading(sc, "F3F4F6")

    # Table borders and header shading are set per table in build_docx.py.
    # Drop the conditional formats of pandoc's "Table" style (black rule).
    tbl_style = get_style(doc, "Table")
    for cond in tbl_style.element.findall(qn("w:tblStylePr")):
        tbl_style.element.remove(cond)

    ph = get_style(doc, "Placeholder Text", WD_STYLE_TYPE.CHARACTER)
    ph.font.color.rgb = rgb("8C8C8C")

    for name in ("Header", "Footer"):
        st = get_style(doc, name, base="Normal")
        para(st, size=8, color=GREY, before=0, after=0)

    # A4 with 2 cm margins.
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2.0)
    sec.top_margin, sec.bottom_margin = Cm(2.2), Cm(2.0)
    sec.header_distance = sec.footer_distance = Cm(1.0)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    fix_docx(OUT)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
