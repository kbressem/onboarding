--[[
Pandoc Lua filter used only for the Word (DOCX) build.

1. Form fields. Inline code that starts with "field:" becomes a Word content
   control (fillable field):
     `field:text`                  plain text field
     `field:text:Placeholder`      plain text field with custom placeholder
     `field:date`                  date picker (dd.MM.yyyy)
     `field:choice:A; B; C`        dropdown list (options separated by ;)
     `field:check`                 checkbox
     `field:photo`                 rich text field for pasting a photo
   The MkDocs hook (build/mkdocs_hooks.py) renders the same markers on the website.

2. <br> inside table cells becomes a Word line break.

3. Links to other pages of this repository (*.md) point to the website when the
   metadata variable site_url is set. Without site_url only the link text is kept.
]]

local PH_TEXT = "Hier eingeben / Type here"
local PH_DATE = "Datum wählen / Select a date"
local PH_CHOICE = "Auswählen / Select"
local PH_PHOTO = "Foto hier einfügen / Paste photo here"

local site_url = nil
local docpath = ""
local field_id = 1000

local function xml_escape(s)
  return (s:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

local function next_id()
  field_id = field_id + 1
  return tostring(field_id)
end

local function placeholder_run(text)
  return '<w:r><w:rPr><w:rStyle w:val="PlaceholderText"/></w:rPr><w:t xml:space="preserve">'
    .. xml_escape(text) .. '</w:t></w:r>'
end

local function sdt(props, content)
  return '<w:sdt><w:sdtPr><w:id w:val="' .. next_id() .. '"/>' .. props
    .. '</w:sdtPr><w:sdtContent>' .. content .. '</w:sdtContent></w:sdt>'
end

local function text_field(placeholder)
  return sdt('<w:showingPlcHdr/><w:text/>', placeholder_run(placeholder or PH_TEXT))
end

local function date_field()
  return sdt('<w:showingPlcHdr/><w:date><w:dateFormat w:val="dd.MM.yyyy"/>'
    .. '<w:lid w:val="de-DE"/><w:storeMappedDataAs w:val="dateTime"/>'
    .. '<w:calendar w:val="gregorian"/></w:date>', placeholder_run(PH_DATE))
end

local function choice_field(options)
  local items = '<w:listItem w:displayText="' .. PH_CHOICE .. '" w:value=""/>'
  for opt in options:gmatch("[^;]+") do
    opt = opt:gsub("^%s+", ""):gsub("%s+$", "")
    local e = xml_escape(opt)
    items = items .. '<w:listItem w:displayText="' .. e .. '" w:value="' .. e .. '"/>'
  end
  return sdt('<w:showingPlcHdr/><w:dropDownList>' .. items .. '</w:dropDownList>',
    placeholder_run(PH_CHOICE))
end

local function check_field()
  -- w14 namespace is declared by build_docx.py after pandoc has written the file.
  return sdt('<w14:checkbox><w14:checked w14:val="0"/>'
    .. '<w14:checkedState w14:val="2612" w14:font="MS Gothic"/>'
    .. '<w14:uncheckedState w14:val="2610" w14:font="MS Gothic"/></w14:checkbox>',
    '<w:r><w:rPr><w:rFonts w:ascii="MS Gothic" w:eastAsia="MS Gothic" w:hAnsi="MS Gothic"/>'
    .. '</w:rPr><w:t>☐</w:t></w:r>')
end

local function photo_field()
  return sdt('<w:showingPlcHdr/>', placeholder_run(PH_PHOTO))
end

function Code(el)
  local spec = el.text:match("^field:(.+)$")
  if not spec then return nil end
  local kind, arg = spec:match("^(%w+):?(.*)$")
  local xml
  if kind == "text" then
    xml = text_field(arg ~= "" and arg or nil)
  elseif kind == "date" then
    xml = date_field()
  elseif kind == "choice" then
    xml = choice_field(arg)
  elseif kind == "check" then
    xml = check_field()
  elseif kind == "photo" then
    xml = photo_field()
  else
    return nil
  end
  return pandoc.RawInline("openxml", xml)
end

function RawInline(el)
  if el.format == "html" and el.text:match("^<br%s*/?>$") then
    return pandoc.LineBreak()
  end
  return nil
end

local function resolve(target)
  -- Turn a relative link to a .md file into a website URL (use_directory_urls).
  local path, anchor = target:match("^([^#]*)(#?.*)$")
  local dir = pandoc.path.directory(docpath)
  if dir == "." then dir = "" end
  local full = pandoc.path.normalize(pandoc.path.join({ dir, path }))
  full = full:gsub("\\", "/")
  -- collapse "a/../" segments, pandoc.path.normalize keeps them
  local parts = {}
  for seg in full:gmatch("[^/]+") do
    if seg == ".." then
      table.remove(parts)
    elseif seg ~= "." then
      table.insert(parts, seg)
    end
  end
  full = table.concat(parts, "/")
  full = full:gsub("index%.md$", ""):gsub("%.md$", "/")
  return site_url:gsub("/*$", "/") .. full .. anchor
end

function Link(el)
  local t = el.target
  if t:match("^%a[%w+.-]*:") or t:match("^#") then
    return nil -- absolute URL, mailto: or in-page anchor
  end
  if t:match("%.md$") or t:match("%.md#") then
    if site_url then
      el.target = resolve(t)
      return el
    end
    return el.content
  end
  return nil
end

function Meta(meta)
  if meta.site_url then
    local s = pandoc.utils.stringify(meta.site_url)
    if s ~= "" then site_url = s end
  end
  if meta.docpath then
    docpath = pandoc.utils.stringify(meta.docpath)
  end
  return meta
end

-- Meta must run before the inline functions.
return {
  { Meta = Meta },
  { Code = Code, RawInline = RawInline, Link = Link },
}
