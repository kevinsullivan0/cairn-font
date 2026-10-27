# Cairn Ash 1.11 — Everyday, Relic, and Bronze

Hearthstone (dark) and Limestone (light), with a quiet Everyday edition and a
more tactile Relic edition. All three editions share the same typography and control scale. Relic adds mineral texture, asymmetric stone chips, inset joints, and
geometric tool marks. Everyday and Relic keep prose and code surfaces flat.

## Install

1. Install the Cairn fonts from the repository’s `desktop/` directory.
2. Copy either or both folders inside `obsidian/` into your vault’s `.obsidian/themes/`.
3. Select **Cairn Ash**, **Cairn Ash Relic**, or **Cairn Ash Bronze** in Settings → Appearance → Themes.
4. Choose the Dark or Light base scheme.

Choose **Cairn** as the Text font in Appearance to use it for prose. **Cairn Mono**
is available as a Monospace font. The themes otherwise respect Appearance fonts
and sizes; Cairn is used for the note title and H1/H2. Restart Obsidian if newly
installed fonts are missing from the font picker.

## Try without installing

Open `compare-nord.html` for the same interactive workspace beside a Nord reference.
The edition menu switches Everyday and Relic. `preview.html` includes light mode,
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

## Bronze and stronger structural material

Bronze is a third selectable edition with a warmer charcoal editor background
and faint, broad mineral fields. There is no fine grit or fracture texture on
the page and no overlay above glyphs; code panels remain flat. The bars share
Relic’s slightly stronger mottling and restrained extra roughness. The native
top-left ribbon cap now continues the same finish, preserving its drag area.

Use the edition menu in `compare-nord.html` to switch Bronze, Relic, and Everyday
beside the same Nord sample. It starts with Bronze. `bronze-proof.png` and
`bronze-light-proof.png` compare native representative renderings with Relic.
These are font/material proofs, not live Obsidian screenshots.

Bronze body contrast is at least 6.79:1 dark and 8.61:1 light across the measured
texture range. Text roles on the page and active line stay over 4.5:1; details
are in `materials/bronze-contrast.json`. `source/build_relic.py` builds both
Relic and Bronze after the base builder; `source/check_bronze.py` checks the
optional editor field. Surface changes preserve fonts, sizes, the native Vim
cursor, and the clear margin rail.
