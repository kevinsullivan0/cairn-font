# Cairn 1.0 — personal edition

A carved, proportional type family for prose and interfaces. Four real styles:
**Regular, Italic, Bold, and Bold Italic**. They share the family name **Cairn**.
Its companion **Cairn Mono** provides the same four styles for code.
The archive itself does not install anything or change font preferences.

## Start here

Open **specimen.html**. It embeds every font, works offline, and needs no
installation. Try the size, theme, and sample-text controls. It shows all four
styles, longer prose, an archive interface, punctuation, and the carved parentheses.

The **proofs/** folder has family, small-text, prose/interface, and native
macOS Core Text specimens. These PNGs show actual fonts; they are not mockups
of invented letter shapes.

## Reuse in HTML

Copy **web/** beside your HTML file. In its head:

```html
<link rel="stylesheet" href="web/cairn.css">
```

Apply the family to the part of the page that should use it:

```html
<article class="cairn-prose">
  <h1>The last watch</h1>
  <p>Some words need <strong>weight</strong>; others need <em>emphasis</em>.</p>
  <p><strong><em>Both together</em></strong> uses Bold Italic.</p>
  <p class="cairn-numbers">01:11 / 08:48 / 12:00</p>
</article>
```

For your own size and line spacing, use `class="cairn"`, or
`font-family: var(--font-cairn)`. The stylesheet defines all four styles,
normal kerning, sensible fallback fonts, and disables synthetic bold/italic.
It does not change the whole page automatically. `.cairn-numbers` enables
proper aligned-width figures; ordinary text keeps proportional figures.

**web/example.html** is a complete editable starter using external fonts.
Keep **cairn.css** beside its **fonts/** folder when moving it.

For portable local HTML, use **web/cairn-embedded.css** instead. It embeds
all four fonts in one stylesheet and avoids local font URL restrictions.
To make a single-file HTML document, put the contents of that embedded
stylesheet inside a `<style>` element. **specimen.html** demonstrates this.
No CDN, network service, JavaScript library, or installed font is needed.

## Cairn Mono for code

Open **mono-specimen.html** to edit a code sample and try all four styles.
Every glyph advances **1440/2048 em (0.703125 em)**. No kerning or ligatures alter
columns. Narrow letters have purpose-drawn feet; wide letters use compact
stroke skeletons instead of just stretching the proportional font. The zero
is slashed and the `i/l/1` shapes remain distinct. Start at **18 px**.

For HTML, add `web/cairn-mono.css` alongside the proportional stylesheet and
use `<pre class="cairn-code"><code>your code</code></pre>`. The portable
`web/cairn-mono-embedded.css` embeds all four Mono fonts. In an editor or
terminal, select **Cairn Mono**. It has the same 114 encoded characters as
Cairn, 117 total glyphs per style, and no Nerd Font icon patch.

**mono-validation.json** checks cell metrics, outline bounds, open counters,
separate dots, web-font round trips, and shaping at 14/16/18 px.
**mono-macos-validation.json** verifies installed family recognition, native
monospace traits, and equal Core Text advances for all four styles.
**proofs/mono.png** shows actual rendered glyphs at several sizes.

To rebuild Mono after installing the Python requirements:

```sh
python build_mono.py
python validate_mono.py
```

## Desktop use — when you choose to install

The eight files in **desktop/** are TrueType fonts with linked weight/style
metadata. On macOS, open the desired TTF files in Font Book, review its preview,
then choose Install only when you are ready. In an application, choose
**Cairn** or **Cairn Mono**, then Regular, Italic, Bold, or Bold Italic. Restart an application
if its font menu was already open. The same TTF files can be installed through
the operating system font settings on other desktop systems.

The package does not install itself. Font Book installation and the font
menus of individual apps have not been tested.

## Sizes and character coverage

Start with **18 px / 1.65 line spacing for prose**, or **16 px for interfaces**.
Use 14 px secondary text sparingly. Native 12–20 px proofs are included;
12 px is a stress test, not the intended reading size. The sharp detail has
more room at 18 px and above. Cairn is proportional; choose **Cairn Mono** for fixed-width code.

All printable ASCII characters are present, plus nonbreaking space, smart
single/double quotes, low double quote, en/em dashes, ellipsis, bullet, minus,
and the ordinary symbol repertoire. There are **114 encoded characters and
127 glyphs per style**, including ten alternate tabular digits. Accented
letters and additional scripts are not drawn; the web stack falls back for
those. No Nerd Font icons or variable-weight axis are included.

The inherited Elbjorg ornaments have been removed. All encoded glyphs are
drawn from Cairn’s own source. Parentheses have curved middles and faceted
ends, with separately fitted spacing in all four styles.

## Design and validation

Regular continues Cairn V, with a planed `r` crown and cut `S` shoulder,
cleaner quote marks, and freshly spaced practical punctuation. Bold is drawn
with a broader cutter and wider structure; `c/e` have extra opening room.
Italic has a restrained forward angle and redrawn `a/f/l/y`, including a
single-storey `a`. It keeps the blade heads, clipped feet, and carved joins.
Bold Italic combines both constructions. All four receive their own spacing.

**validation.json** records 12,257 outline-clearance checks per style,
OpenType kerning and tabular-figure shaping, all letter/digit counter
structures, small-size dot/counter checks, metadata, coverage, and identical
TTF-to-WOFF decoded tables. **macos-validation.json** records native Core Text
file decoding and recognition of bold/italic traits without registering or
installing fonts. Native macOS raster proofs supplement the FreeType proofs.
**web-validation.json** records offline DOM behavior and package link checks.

This is a usable personal first edition. Browser layout has not been visually
automated, Windows rendering has not been tested, and there is no manual
TrueType hinting. No reading-speed benefit is claimed. Shared line metrics
leave room for the ascenders, dots, descenders, and italic shapes.

## Contents

- **desktop/** — eight installable TTF files: four Cairn and four Cairn Mono.
- **web/** — eight WOFF files, separate external/embedded CSS for each family, example HTML.
- **specimen.html** — proportional font preview.
- **mono-specimen.html** — editable code preview with size, style, and background controls.
- **proofs/** — raster proofs and punctuation.
- **source/** — reusable builders, validators, and drawing definitions.
- **manifest.json** — hashes for all other files in this edition.

## Provenance

Cairn began as a readability study inspired by Elbjorg’s carved atmosphere.
The shipped alphabet, figures, punctuation, and symbols are generated from
Cairn’s drawing definitions. No original Elbjorg font file or ornament outlines
are included or required to build this edition. No distribution license has
yet been selected. The specimen prose is original, not a book excerpt.

## Rebuilding

Rebuilding needs only the included drawing source; it does not need any
reference font or installed Elbjorg. From **source/** with Python 3.12+:

```sh
python -m pip install -r requirements.txt
python build_family.py
python validate_family.py
```

To choose a different output directory, pass `--output /path/to/output` to
`build_family.py`, then that directory to `validate_family.py`. The source
folder also includes the native macOS proof tool and the web/proof generators.
Those optional generators accept the package directory as an argument.
