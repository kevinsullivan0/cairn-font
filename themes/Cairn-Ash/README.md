# Cairn Ash 1.13 — Everyday, Relic, and Bronze

Hearthstone (dark) and Limestone (light), with a quiet Everyday edition and a
more tactile Relic edition. All three editions share the same typography and control scale. Relic adds mineral texture, asymmetric stone chips, inset joints, and
geometric tool marks. Everyday and Relic keep prose and code surfaces flat.

## Install

1. Install the Cairn fonts from the repository’s `desktop/` directory.
2. Copy any of the folders inside `obsidian/` into your vault’s `.obsidian/themes/`.
3. Select **Cairn Ash**, **Cairn Ash Relic**, or **Cairn Ash Bronze** in Settings → Appearance → Themes.
4. Choose the Dark or Light base scheme.

Choose **Cairn** as the Text font in Appearance to use it for prose. **Cairn Mono**
is available as a Monospace font. The themes otherwise respect Appearance fonts
and sizes; Cairn is used for the note title and H1/H2. Restart Obsidian if newly
installed fonts are missing from the font picker.

## Try without installing

Open `compare-nord.html` for the same interactive workspace beside a Nord reference.
The edition menu switches Everyday, Relic, and Bronze. `preview.html` includes light mode,
body-font choices, search, tasks, a local draft, and terminal color previews.
These are standalone mockups, not running Obsidian windows.

On macOS with Kitty installed, double-click `Try Hearthstone.command` or
`Try Limestone.command` in Finder. Each opens a separate trial window.

## Files and validation

- `obsidian/`: complete installable theme folders.
- `kitty/`: softened terminal color configurations.
- `material.css` and `material.json`: reusable color, spacing, typography, and material tokens.
- `relic.css`: compiled material overlay, with embedded textures and ledges.
- `materials/`: deterministic pigment tiles, vector geometry, and contrast measurements.
- `source/`: theme builders, material generator, contrast checker, and palette evaluator.
- `DESIGN-NOTES.md`: design decisions and critique history.
- `edition-proof.png` and `edition-light-proof.png`: representative native font/material proofs.

Dark prose contrast is 7.20:1. Tested material text remains at least 4.52:1 dark
and 4.71:1 light. Offline DOM/CSS checks and native proofs were reviewed; live
Obsidian layout and community plugins are not exhaustively verified.

To rebuild themes: run `python source/build_theme.py`, then
`python source/build_relic.py` from any working directory. Preview HTML is a
frozen specimen of this release. `python source/check_material.py` verifies the
material assets. No local installation records, personal vault paths, notes,
preferences, or desktop painting are included.

## Editor cursor

In Vim normal mode, the native block cursor gets the theme’s accent fill and
contrasting text. Its measured glyph width is preserved, including narrow
proportional letters. Insert mode retains the ordinary caret. The active-line
rail sits in the margin with a six-pixel gap, rather than covering the first
character, and adds no line padding. The selector structure was checked against
the installed Obsidian 1.14.5 editor and exercised in offline state tests.

## Bronze: blue slate and worn bronze

Bronze keeps Nord’s cool `#2e3440` writing foundation, with more visible broad
slate mottling. Side panes, bars, and ordinary callouts use warmer oxidized
bronze stone. Semantic callout titles, icons, and colors retain their meaning;
custom theorem callouts are excluded. Code panels remain flat blue.
There is no grit or fracture overlay over the page text.

Relic and Bronze share slightly rougher structural material and sparse,
asymmetric chips with exposed fracture faces. Paired incised lozenges are
centered geometrically in note-title rules and horizontal breaks, with a
transparent gap that leaves the page mottling continuous. Decoration carries
no text and does not clip controls, focus outlines, or hit areas. Typography,
control dimensions, the native Vim block cursor, and clear margin rail are
unchanged. Everyday keeps its quiet material.

Use the edition menu in `compare-nord.html` to switch Bronze, Relic, and Everyday
beside the same Nord sample. It starts with Bronze and includes long prose,
section breaks, callouts, tables, search, tasks, and a local editor sample.
`bronze-proof.png` and `bronze-light-proof.png` compare native representative
renderings with Relic; `divider-proof.png` shows divider geometry at several
widths and enlarged chip details. These are font/material proofs, not live
Obsidian screenshots. The native proof’s warm note panel represents a callout.

Measured Bronze body contrast is at least 6.67:1 dark and 8.60:1 light across
the texture range. Tested text roles, warm panels/callouts, and active lines
stay above 4.5:1; details are in `materials/bronze-contrast.json`. This is not a
whole-app or plugin accessibility audit, nor a measure of subjective comfort.

`source/build_relic.py` builds both Relic and Bronze after the base builder;
`source/generate_stone.py` rebuilds material tiles, `source/stone_ledge.py`
defines the ledges, and `source/check_bronze.py` checks compositing bounds.
The preview HTML is a frozen specimen; rebuilding styles does not regenerate
its embedded frames.

## 1.13: finished workspace states

Inactive, hovered, current and keyboard-focused tabs retain one carved
silhouette, including the tab immediately before the current one. Inner hover
fills and native connector curves no longer contradict the shape. Inactive
tabs have a quiet edge; hover brightens the label; the current tab keeps its
accent underline and note-colored fill. Keyboard focus has an inset outline.
Native close visibility, drag regions, stacked tab spines, font sizes and
spacing are preserved.

Relic and Bronze extend the same quiet grain and shallow bevel to note
toolbars, notices, tooltips and navigation/settings states. Tooltips use the
soft palette ink. Reading/code surfaces and control dimensions stay unchanged.
`ui-proof.png` shows representative native drawings of these states in dark
and light, and the Workbench comparison includes a functional toolbar and
notification sample. These are offline specimens, not live app screenshots.

## Terminal palettes

Open `terminal.html` to compare Hearthstone and Limestone at a default 12 px
preview size, with JetBrains Mono or embedded Cairn Mono. In Finder, the two
trial launchers open separate Kitty windows at 12 pt without editing global
configuration. Normal ANSI colors are quieter than the bright set. Selection
and cursor ink remain distinct. The background stays opaque and flat.

`kitty/dark-colors.conf` and `kitty/light-colors.conf` contain colors only.
Include the chosen file from an existing Kitty configuration to retain your
font and window settings. The original `dark.conf` and `light.conf` remain
self-contained trial configurations. `terminal-palette.json` exports both
schemes and contrast measurements for reuse elsewhere.

Text slots 1–15 on the default background, selection text and cursor text
measure at least 4.5:1. Slot 0 retains an inset/background role for TUI
compatibility; dim text, application overrides and colored-background pairs
are outside that check. All four configuration files are parsed by Kitty.
