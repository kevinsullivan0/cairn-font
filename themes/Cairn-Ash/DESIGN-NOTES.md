# Relic — critique and refinement notes

An independent design critic reviewed the theme sources and native font/material
proof, then reviewed each revision before the next round. The aim was a workspace
that feels built from old stone and iron while remaining useful for ordinary work.
The atmosphere comes from weight, worn edges, and restrained warmth; no borrowed
artwork or literal fantasy imagery is used.

## Round 1 — material hierarchy

The critic found that uniformly ornate controls and many pristine double rules
made the stone feel applied to a modern interface. Thin fractures could resemble
scratches more than rock.

The revision reserves the inner inscription frame and Cairn action lettering for
primary actions. Utility buttons have a shallower edge and familiar interface type.
Metadata and minor rules are quieter, major panel joints deeper, and fractures are
fewer, broader, and more angular. The reading palette remains unchanged.

## Round 2 — density and construction

The critic found that deep navigation would repeat too many carved folder headings,
that symmetric panel trenches weakened the direction of light, and that wrapping
tabs made the specimen artificially forgiving.

The revision keeps inscription lettering on top-level folders and uses compact
interface type for descendants. The main panel boundary is deeper than its outer
edge, with a broken upper highlight on the vault header. The specimen now includes
a genuinely nested folder and a long tab title with single-line ellipsis.

## Round 3 — app structure and practical reading

The critic identified an Obsidian root-folder wrapper that could incorrectly make
top-level folders inherit nested styles. The selector now excludes that root, and
the specimen and checks include the real root → folder → descendant structure.

File search opens collapsed ancestors of matches, displays an empty state, and
restores the earlier folder state when cleared. The ledger's Copies column uses
right alignment and tabular numerals. The critic recommended no further increase
in texture or ornament.

## Fuller specimen

The direct Nord comparison uses identical content in both panes: more than 600
words of original field-record prose, nested lists, quotations, footnotes, a long
link, a six-record ledger, foldable notes, searchable records, task counts, local
action feedback, syntax-colored code, and an editable Markdown draft with a word
count. The Jump to menu moves both panes to the same example.

## Verification and limits

Dark body contrast remains 7.20:1. Tested material/control text stays at or above
4.52:1 in dark mode and 4.71:1 in light mode. The material is static and embedded;
reading and code interiors stay flat. The checks cover CSS parsing, native variable
compatibility, matched comparison content, primary/utility typography, nested-folder
selection, collapsed-folder search, empty states, task counts, draft editing, jump
navigation, and numerical alignment.

The reviewed Core Text image is a representative native font and material proof,
not a browser or Obsidian screenshot. Offline checks do not establish every live
layout or community-plugin interaction. Nord's stylesheet and Appearance settings
are preserved when installing the update; Relic is not selected automatically.

## 1.9 — construction and age

A further independent review found that the remaining pristine, continuous rules
looked more like drafting lines than stone. The critic recommended a shared
3–6 px ledge profile and sparse tooling within those edges, while preserving the
current grain and typography hierarchy.

The update adds three related six-pixel profiles to titles, the tab shelf, and
vault identity. Each has a thin iron-colored lip, a stone face, a dark recess,
and differently placed angular losses. The primary inlay also has a small break.
The title and vault profiles occupy pointer-transparent pseudo-elements; the
shelf uses a reserved border band so it does not take over Obsidian's native
window-control pseudo-elements. No parent element or text selection is clipped.

Dark and light Core Text proofs were reviewed. Checks cover the six embedded
vector profiles, their palette colors and bounded geometry, lack of external
references, decorative-only scope, reading contrast, and the existing expanded
comparison interactions. These remain mockup/native-proof checks, not live
Obsidian visual verification.

## 1.10 — irregular wear and selective weight

The critic found that matching chip slopes and stretched vector geometry made
edge damage look machined. Repeated thick rules also made the carved edges less
special. The recommended revision was fixed-size asymmetric fractures, fewer
heavy borders, and stronger broad mineral variation limited to structural panels.

The title now has two unequal chips, one with a small exposed facet. Their widths
stay fixed as the surrounding edge grows; the tab shelf uses one smaller chip.
The title, tab shelf, and vault seam have depths of 4, 2, and 1 pixels respectively.
The second title frame, folder rules, and several double borders are removed or
thinned. Primary tablets keep their weight, while menus and utility surfaces use
single edges and shallow depth.

The sidebar/topbar texture increases broad mineral variation without changing
fine grit or fracture strength. Its pixel-opacity standard deviation is 1.36 times
that of the ordinary tile, while mean alpha changes by less than 0.003 on a 0–255
scale. This measures the asset, not perceived comfort or a percentage increase in
visible texture. Smaller controls retain the original tile; prose and code stay flat.

Dark and light native proofs were reviewed. Offline checks pass for fixed-pixel
chip geometry at narrow and wide widths, decorative-only scope, CSS and preview
interactions, and material contrast. The conservative tested material minimum is
4.52:1 dark and 4.71:1 light; dark body contrast remains 7.20:1. These checks and
representative Core Text proofs do not substitute for live browser or Obsidian
visual verification.

## 1.10.1 — shared scale

User feedback identified Relic’s larger type and controls. Removed its title, H2,
H3, tab, folder, callout, button, navigation, and spacing overrides. Relic now
inherits the regular edition’s typography and density. Material and decorative
geometry remain; the folder seal is positioned outside text flow. The comparison
and native proofs use the shared scale. Offline checks reject typography and
padding overrides in the Relic overlay.

## 1.10.2 — editor cursor and clear margin

The line marker moves outside the glyph field: a two-pixel rail at an eight-pixel
negative inline offset leaves six pixels clear of text. No line padding or text
position changes on focus. The native CodeMirror 6 Vim cursor receives accent
fill while preserving its measured width; a fixed minimum was rejected because
proportional i/l/punctuation can be narrower than 1ch. Insert mode remains a thin
caret. A native font/layout proof includes a cursor over proportional i beside W.
Offline state checks pass; live Obsidian rendering has not been automated.

Relic also removes the native tab header’s two decorative concave connector
pseudo-elements. Their rounded fill produced pale square remnants beneath the
beveled tab corners. Tab labels, close controls, parent drag regions, and focus
areas retain their geometry.
