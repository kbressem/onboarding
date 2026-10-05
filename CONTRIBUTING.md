# Contributing

## Language

- Write the guides and the reference pages in English. Write the forms in German and English.
- Write the English text in ASD-STE100 (Simplified Technical English), Issue 9. Use the rules below. Run `make lint` before you commit.
- Keep the guides `essen.md` and `tum.md` at three Word pages or less, with dense information. The footer of the Word file shows the page count. Put more information in `docs/reference/` and add a link.
- If you do not have all the information, write an HTML comment, `<!-- TODO: information that is not available -->`. Also add the item to `OPEN_ITEMS.md`. The website and the Word files do not show comments.
- Do not add passwords, access tokens, patient data or personal data.

## ASD-STE100 rules

| Rule | Limit |
|---|---|
| Procedural sentences (instructions) | 20 words or less |
| Descriptive sentences | 25 words or less |
| Paragraphs | 6 sentences or less |
| Noun clusters | 3 words or less |
| Instructions | Imperative, one instruction in each sentence. Write the condition first ("If ..., do ..."). |
| Verbs | Active voice and simple tenses. Do not use "-ing" forms, except in technical names (for example "meeting", "training"). |
| Words | Use approved words in their approved meaning. Technical names and technical verbs for computer procedures (for example log in, download) are also permitted. |
| Long text | Use vertical lists. |

The ASD-STE100 dictionary is free from [asd-ste100.org](https://www.asd-ste100.org). These substitutions occur frequently in this repository.

<!-- ste-ignore-start -->

| Do not use | Use |
|---|---|
| need, require | must, necessary |
| ask | tell, speak to, contact |
| provide | give, supply |
| check (verb) | make sure, examine |
| request (verb) | tell, write |
| allow | let, permitted |
| approve | approval, approved |
| apply for | use the form, get |
| enter | write |
| submit | send |
| store, save | keep |
| create | make |
| choose, decide | select, decision |
| appear | show, is in |
| within | in, in ... or less |
| should | must, or a sentence with "if" |
| approximately | about |
| valid | applicable, correct |
| join | add, connect |
| work (verb) | operate, or the noun "work" |
| people | persons, personnel |
| e.g. | for example |

<!-- ste-ignore-end -->

Administrative terms are technical names, for example business trip, reimbursement, reservation and purchase. Keep German names of forms and offices (for example Dienstreiseantrag, Reisekostenstelle).

## Markdown for the website and Word

| Item | Syntax |
|---|---|
| Title and subtitle | Front matter `title:` and `subtitle:`. Do not use a `#` heading. |
| Sections | `##` and `###` |
| Note box | Block quote, `> text` |
| Table | Pipe table with a header row |
| Line break in a table cell | `<br>` |
| Link to a different page | Relative link to the `.md` file, for example `[RadCat](reference/radcat.md)` |
| Page without Word file | Front matter `docx: false` |

Do not use syntax for MkDocs only, for example admonitions (`!!! note`) or tabs. pandoc cannot read it.

## Form fields

Inline code with the prefix `field:` becomes a Word field and an empty box on the website.

| Marker | Word field |
|---|---|
| `` `field:text` `` | Text field |
| `` `field:text:Text in the field` `` | Text field with a custom placeholder |
| `` `field:date` `` | Date selection (dd.MM.yyyy) |
| `` `field:choice:Option A; Option B` `` | List of options. Use `;` between the options. |
| `` `field:check` `` | Checkbox |
| `` `field:photo` `` | Box for a photo |

Forms use a table with two columns. Write the German label in bold, then `<br>` and the English label. For an example, refer to `docs/forms/personal-information.md`.

## New page

1. Make the Markdown file in `docs/`. Add the front matter `title:` and, if necessary, `subtitle:`.
2. Add the page to `nav` in `mkdocs.yml`.
3. Run `make serve`. Examine the website and the Word file in `docs/downloads/`.
