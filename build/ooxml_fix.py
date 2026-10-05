"""Make DOCX files schema-conform after pandoc and python-docx have written them.

Pandoc and manual XML edits leave some elements in an order that the
OOXML schema does not allow. Word usually tolerates this, but strict
consumers and validators do not. This module

* sorts the children of pPr, rPr, tblPr, trPr, tcPr, sectPr, style and
  settings into schema order,
* pads numbering nsid values to 8 hex digits,
* adds missing required pgMar attributes,
* removes stray characters from element-only containers.

Usage: fix_docx(path) rewrites the file in place.
"""

import zipfile
from pathlib import Path

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"

ORDER = {
    "style": ["name", "aliases", "basedOn", "next", "link", "autoRedefine", "hidden",
              "uiPriority", "semiHidden", "unhideWhenUsed", "qFormat", "locked",
              "personal", "personalCompose", "personalReply", "rsid", "pPr", "rPr",
              "tblPr", "trPr", "tcPr", "tblStylePr"],
    "pPr": ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr",
            "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs",
            "suppressAutoHyphens", "kinsoku", "wordWrap", "overflowPunct",
            "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd",
            "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents",
            "suppressOverlap", "jc", "textDirection", "textAlignment",
            "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr",
            "pPrChange"],
    "rPr": ["ins", "del", "moveFrom", "moveTo", "rStyle", "rFonts", "b", "bCs", "i",
            "iCs", "caps", "smallCaps", "strike", "dstrike", "outline", "shadow",
            "emboss", "imprint", "noProof", "snapToGrid", "vanish", "webHidden",
            "color", "spacing", "w", "kern", "position", "sz", "szCs", "highlight",
            "u", "effect", "bdr", "shd", "fitText", "vertAlign", "rtl", "cs", "em",
            "lang", "eastAsianLayout", "specVanish", "oMath", "rPrChange"],
    "tblPr": ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize",
              "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd",
              "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook", "tblCaption",
              "tblDescription", "tblPrChange"],
    "trPr": ["cnfStyle", "divId", "gridBefore", "gridAfter", "wBefore", "wAfter",
             "cantSplit", "trHeight", "tblHeader", "tblCellSpacing", "jc", "hidden",
             "ins", "del", "trPrChange"],
    "tcPr": ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd",
             "noWrap", "tcMar", "textDirection", "tcFitText", "vAlign", "hideMark",
             "headers", "cellIns", "cellDel", "cellMerge", "tcPrChange"],
    "sectPr": ["headerReference", "footnotePr", "endnotePr", "type", "pgSz", "pgMar",
               "paperSrc", "pgBorders", "lnNumType", "pgNumType", "cols", "formProt",
               "vAlign", "noEndnote", "titlePg", "textDirection", "bidi", "rtlGutter",
               "docGrid", "printerSettings", "sectPrChange"],
    "settings": ["writeProtection", "view", "zoom", "removePersonalInformation",
                 "removeDateAndTime", "doNotDisplayPageBoundaries",
                 "displayBackgroundShape", "printPostScriptOverText",
                 "printFractionalCharacterWidth", "printFormsData",
                 "embedTrueTypeFonts", "embedSystemFonts", "saveSubsetFonts",
                 "saveFormsData", "mirrorMargins", "alignBordersAndEdges",
                 "bordersDoNotSurroundHeader", "bordersDoNotSurroundFooter",
                 "gutterAtTop", "hideSpellingErrors", "hideGrammaticalErrors",
                 "activeWritingStyle", "proofState", "formsDesign", "attachedTemplate",
                 "linkStyles", "stylePaneFormatFilter", "stylePaneSortMethod",
                 "documentType", "mailMerge", "revisionView", "trackRevisions",
                 "doNotTrackMoves", "doNotTrackFormatting", "documentProtection",
                 "autoFormatOverride", "styleLockTheme", "styleLockQFSet",
                 "defaultTabStop", "autoHyphenation", "consecutiveHyphenLimit",
                 "hyphenationZone", "doNotHyphenateCaps", "showEnvelope",
                 "summaryLength", "clickAndTypeStyle", "defaultTableStyle",
                 "evenAndOddHeaders", "bookFoldRevPrinting", "bookFoldPrinting",
                 "bookFoldPrintingSheets", "drawingGridHorizontalSpacing",
                 "drawingGridVerticalSpacing", "displayHorizontalDrawingGridEvery",
                 "displayVerticalDrawingGridEvery",
                 "doNotUseMarginsForDrawingGridOrigin", "drawingGridHorizontalOrigin",
                 "drawingGridVerticalOrigin", "doNotShadeFormData",
                 "noPunctuationKerning", "characterSpacingControl", "printTwoOnOne",
                 "strictFirstAndLastChars", "noLineBreaksAfter", "noLineBreaksBefore",
                 "savePreviewPicture", "doNotValidateAgainstSchema", "saveInvalidXml",
                 "ignoreMixedContent", "alwaysShowPlaceholderText",
                 "doNotDemarcateInvalidXml", "saveXmlDataOnly", "useXSLTWhenSaving",
                 "saveThroughXslt", "showXMLTags", "alwaysMergeEmptyNamespace",
                 "updateFields", "hdrShapeDefaults", "footnotePr", "endnotePr",
                 "compat", "docVars", "rsids", "mathPr", "attachedSchema",
                 "themeFontLang", "clrSchemeMapping", "doNotIncludeSubdocsInStats",
                 "doNotAutoCompressPictures", "forceUpgrade", "captions",
                 "readModeInkLockDown", "smartTagType", "schemaLibrary",
                 "shapeDefaults", "doNotEmbedSmartTags", "decimalSymbol",
                 "listSeparator"],
}
RANK = {parent: {name: i for i, name in enumerate(seq)} for parent, seq in ORDER.items()}
RANK["sectPr"]["footerReference"] = RANK["sectPr"]["headerReference"]

PGMAR_REQUIRED = ("top", "right", "bottom", "left", "header", "footer", "gutter")
PARTS = ("word/document.xml", "word/styles.xml", "word/numbering.xml",
         "word/settings.xml")


def _local(tag):
    return etree.QName(tag).localname if isinstance(tag, str) else None


def _sort_children(parent, ranks):
    children = list(parent)
    known = len(ranks) + 1

    def key(item):
        idx, child = item
        if not isinstance(child.tag, str):
            return (known, idx)                 # comments, processing instructions
        ns = etree.QName(child.tag).namespace
        if ns not in (W, M):
            return (known, idx)                 # extensions (w14, w15) at the end
        return (ranks.get(_local(child.tag), known), idx)

    ordered = [c for _, c in sorted(enumerate(children), key=key)]
    if ordered != children:
        for c in children:
            parent.remove(c)
        parent.extend(ordered)


def _fix_tree(root):
    for elem in root.iter():
        if not isinstance(elem.tag, str):
            continue
        q = etree.QName(elem.tag)
        if q.namespace != W:
            continue
        name = q.localname
        if name in RANK:
            # element-only containers: drop stray characters (pandoc's default
            # reference.docx has a ">" inside the Abstract Title rPr)
            if elem.text and elem.text.strip():
                elem.text = None
            for child in elem:
                if child.tail and child.tail.strip():
                    child.tail = None
            if name == "pPr":
                for dup in elem.findall(f"{{{W}}}pStyle")[1:]:
                    elem.remove(dup)
            _sort_children(elem, RANK[name])
        if name == "nsid":
            val = elem.get(f"{{{W}}}val")
            if val and len(val) < 8:
                elem.set(f"{{{W}}}val", val.zfill(8).upper())
        if name == "pgMar":
            for attr in PGMAR_REQUIRED:
                if elem.get(f"{{{W}}}{attr}") is None:
                    elem.set(f"{{{W}}}{attr}", "0")


def fix_docx(path):
    path = Path(path)
    tmp = path.with_suffix(".fix.tmp")
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename in PARTS or item.filename.startswith(("word/header", "word/footer")):
                root = etree.fromstring(data)
                _fix_tree(root)
                data = etree.tostring(root, xml_declaration=True, encoding="UTF-8",
                                      standalone=True)
            zout.writestr(item, data)
    tmp.replace(path)
