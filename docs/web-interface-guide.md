# Cairn web interface guide

Use with the [design language](../DESIGN-LANGUAGE.md) and choose a
[web profile](web-profiles.md) before styling a page. The token table below
describes Cairn Ash 1.13 specifically. It is not the required palette for every
Cairn website. Web layout and component guidance are reusable defaults, not a
replacement for the theme's existing specimens.

## 1. Reuse the source assets

- Colors, spacing, type roles, and surface variables:
  [material.json](../themes/Cairn-Ash/material.json) and
  [material.css](../themes/Cairn-Ash/material.css).
- Proportional font: [web/cairn.css](../web/cairn.css) and its relative
  `fonts/Cairn-*.woff` files.
- Monospace font: [web/cairn-mono.css](../web/cairn-mono.css) and its relative
  `fonts/CairnMono-*.woff` files.
- Optional material: [relic.css](../themes/Cairn-Ash/relic.css),
  [bronze.css](../themes/Cairn-Ash/bronze.css), and
  [materials](../themes/Cairn-Ash/materials). These overlays include
  application-specific selectors; do not import an Obsidian theme as a generic
  web component stylesheet.

Preserve relative font paths, `font-display: swap`, and fallback families. Use
the actual font files, not a similarly named substitute or simulated carved
effect. The fonts cover 114 encoded characters, not arbitrary Unicode; test
fallbacks for the content's languages, symbols, and mathematics. JetBrains Mono
is an optional separate font dependency, not a font bundled by Cairn. If adding
it, obtain the real files and retain its license separately.

Read [LICENSING.md](../LICENSING.md). Redistributed Cairn fonts need the
[OFL](../OFL.txt); original scripts, themes, and documentation use
[MIT](../LICENSE). Preserve applicable [third-party notices](../THIRD_PARTY_NOTICES.md).
This guide does not expand those grants or the font's character coverage.

## 2. Bind colors to jobs

For the Ash profile, use the named `--cairn-*` variables or generate equivalent
application variables from the JSON. Other profiles should record their own
semantic mapping instead of silently overriding Ash. Set
`data-cairn-theme="light"` on the document root for Limestone when using the
material CSS; use `dark` for Hearthstone.

| Role / CSS suffix | Hearthstone | Limestone | Web use |
| --- | --- | --- | --- |
| `stone` | `#2e3440` | `#eee5d3` | Page and reading canvas |
| `stone-inset` | `#343c49` | `#e3d8c1` | Navigation, secondary panel |
| `stone-raised` | `#3b4252` | `#e8ddc6` | Selected row or grouped surface |
| `stone-hover` | `#434c5e` | `#dbcfb5` | Hover surface |
| `ink` | `#cac4b8` | `#463c30` | Main text |
| `ink-muted` | `#b3afa1` | `#695a48` | Secondary text, still readable |
| `groove` | `#556273` | `#b5a383` | Quiet separators, not text |
| `bronze` | `#c6b298` | `#7d511a` | Focus and deliberate emphasis |
| `copper` | `#ed9a7f` | `#934738` | Selective title or emphasis |
| `patina` | `#89cec4` | `#2b655d` | Links |
| `selection` | `#4b4d49` | `#d7be8d` | Selected text background |

The JSON also provides sage, steel, amethyst, ochre, active-line, and button
state colors. Assign them consistent semantic jobs before using them. A quiet
separator is not necessarily sufficient contrast for a control boundary;
check the actual component and use the button-edge/focus roles where needed.

## 3. Choose a type profile

The default editorial relationship is Cairn for display, comfortable system text
for reading and ordinary controls, and mono for code or metadata. Two useful
variations are:

- **Mono-focused technical pages (optional):** Cairn for the brand or main title;
  a readable mono such as JetBrains Mono for UI, record titles, metadata, and
  text. Avoid ligatures where literal code or identifiers matter.
- **Long-form reader or everyday tool (starting point):** Cairn for display lettering; a
  comfortable text family for sustained reading; a mono for code. The material
  CSS defaults to system text and JetBrains Mono/code fallbacks. Cairn prose
  is an explicit option, with the supplied `.cairn-prose` starting at 18px/1.65.

For new web pages, start long-form text around 16–18px with 1.65–1.75 line
height. Use smaller UI text only when it remains readable; compact metadata
must not force small reading text. Start with the existing 720px reading-width
token, then check the actual font and aim for a comfortable line length rather
than a fixed screen proportion. Keep headings in a modest scale and avoid
very wide tracking. Use the supplied real Regular, Italic, Bold, and Bold
Italic faces rather than synthetic styles.

## 4. Arrange the page around its content

- Use the existing spacing steps: 4, 8, 12, 16, 24, and 32px. A restrained
  2–3px radius fits ordinary web controls; the material token is 3px.
- A collection can use a slim header, compact secondary navigation, and a
  primary reading area. Record rows separated by 1px rules suit dense lists;
  distinct paper or mineral cards suit browsable collections. Choose based on
  the content, not a repeated generic grid template.
- A record needs a descriptive title, a brief useful summary, honest state
  or provenance, and direct actions. Keep the title most prominent. Align
  metadata consistently and let actions wrap instead of squeezing them.
- A reader needs an obvious way back, a clear source/title, readable text,
  and a deliberate end. Put tool controls beside the reading task, not between
  every paragraph. Do not add an infinite feed unless the product needs one.
- On narrow screens, collapse secondary columns into compact navigation;
  preserve the reading order and all required actions. Let code, tables, and
  equations scroll in their own containers rather than widening the page.
- Start reading surfaces flat. Subtle mineral variation can identify outer
  structure or card material. Keep any decorative pseudo-elements
  pointer-transparent and outside text, focus, and hit-area geometry. Material
  must remain quieter than the words laid over it.

## 5. Keep behavior and metadata trustworthy

Use semantic links and buttons, a skip link where navigation repeats, visible
keyboard focus, and an explicit current-page state such as `aria-current`.
Underline prose links or give them another non-color distinction. Theme
controls must show and change the actual theme. Respect reduced motion and
avoid layout-shifting hover effects.

Dates must name their source and meaning. Repository creation, newest commit,
content revision, synchronization, and deployment are different events. Do not
call a deployment date “content updated.” Store machine-readable timestamps,
display a clear date and time-zone basis when relevant, and show unknown or
unavailable values honestly. A failed refresh should not silently become zero
activity or a fabricated recent date. Never expose repository credentials in
client code to obtain metadata.

## 6. Review before calling it finished

- [ ] The first screen exposes the page's useful content or action.
- [ ] Display type, reading type, colors, and spacing match a chosen profile.
- [ ] No generic hero, decorative card grid, or ornamental statistic was added
      without a purpose.
- [ ] Real fonts load; fallbacks, punctuation, symbols, and long titles work.
- [ ] Long text, empty/error/loading states, and wrapped metadata were checked.
- [ ] Keyboard navigation, focus, current state, links, and controls work.
- [ ] Text contrast is at least 4.5:1 for normal text and 3:1 for large text;
      relevant control/focus boundaries meet their contrast requirements.
      Check rendered surfaces and states, not just a palette swatch.
- [ ] Narrow mobile width and 200% zoom preserve reading and actions without
      page-level horizontal scrolling; touch controls have adequate targets.
- [ ] Both themes were visually checked. No texture obstructs text or focus.
- [ ] Dates, counts, source links, and status claims match the actual data.
- [ ] Added fonts/assets retain their licenses and project content stays in
      the intended project and audience.

Existing theme contrast reports describe their tested specimens. They do not
certify a new website or replace its own browser and accessibility checks.
