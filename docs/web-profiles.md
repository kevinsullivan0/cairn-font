# Web profiles: one family, distinct applications

Cairn is not one exact palette or page template. Keep the relationship between
carved display type, readable text, restrained mineral material, and deliberate
controls. Let each application have its own atmosphere and rhythm.

Use the [shared principles](../DESIGN-LANGUAGE.md) and
[implementation checks](web-interface-guide.md) with a chosen profile. The
profiles below are reusable design guidance, not a bundled CSS component system.

## Stone and paper: editorial starting point

Use a mineral-slate outer structure and lighter paper reading surfaces. Cairn
headings give the page its carved identity; system UI text carries sustained
reading and ordinary controls. A real monospace font is reserved for code,
identifiers, dates, and compact metadata where it helps.

Suggested role mapping:

| Role | Value | Purpose |
| --- | --- | --- |
| Ground | `#3b4447` | Slate outer canvas |
| Chrome | `#353e40` | Structural navigation |
| Ink on ground | `#eee9dd` | Main text on dark structure |
| Muted on ground | `#bfc5c1` | Secondary structural text |
| Structural line | `#727d7b` | Dividers; verify control contrast separately |
| Brass accent | `#e3c58b` | Focus and selective emphasis on dark structure |
| Paper | `#f2eee3` | Sustained reading surface |
| Ink on paper | `#283932` | Reading text |
| Muted on paper | `#617066` | Secondary reading information |
| Paper line | `#c3c9bd` | Quiet paper separators |

These are web-profile values, separate from the Ash JSON. A light reading surface
needs a dark focus indicator and dark link colors; do not carry a light brass
outline onto paper without checking its contrast.

For a collection, paper or mineral cards may have modestly irregular edges and
different widths when the content benefits. Sage/jade, ochre, and slate can
differentiate kinds of records, but text labels must retain the meaning. Keep
status separate from type. A compact list view is a useful alternative for
scanning. Cards must remain legible as records, not decorative tiles.

For a focused reader, keep the same type/material relationship but use a calmer
single reading column, less texture, and a quieter heading or divider treatment.
It need not copy the collection's card silhouettes, stagger, or density.

## Ash: consistent everyday work surfaces

Use the existing [Ash material tokens](../themes/Cairn-Ash/material.json) and
[CSS](../themes/Cairn-Ash/material.css) for a full dark or light work surface.
Hearthstone uses cool slate with soft ink; Limestone uses a warm light ground.
Everyday, Relic, and Bronze preserve one type/control scale while varying
material treatment. See the [theme README](../themes/Cairn-Ash/README.md).

This is a good starting point for editors, utilities, dense technical pages,
or a site that needs the same palette as the existing desktop theme. Mono-heavy
typography is an option for the task, not a requirement for family membership.

## Material assets already in this repository

- [bronze-editor.png](../themes/Cairn-Ash/materials/bronze-editor.png): broad
  mineral field for the outer ground or carefully tested broad surfaces.
- [basalt-chrome.png](../themes/Cairn-Ash/materials/basalt-chrome.png): structural
  stone variation for chrome or selective material cards.
- [basalt-grain.png](../themes/Cairn-Ash/materials/basalt-grain.png): quieter grain
  for smaller material surfaces.
- [Material metadata](../themes/Cairn-Ash/materials/texture.json) and
  [Bronze contrast results](../themes/Cairn-Ash/materials/bronze-contrast.json):
  source information and the limits of the existing tested application.

Reuse the real assets rather than inventing a noisy overlay. Tune the composite
for the new surface and measure it; duplicating texture layers changes the
contrast and is not automatically safe. Keep a flat fallback. Do not apply
distress above text or use a clipped surface to clip a control's focus area.

## Give an application its own signature

Choose one or two differences: a quieter reading rhythm, a particular divider,
an editorial title treatment, a distinct card proportion, or a restrained
semantic accent. Preserve the shared foundations and ordinary interaction
behavior. Avoid copying every visual detail, and avoid changing all the
foundations at once.

In the application's README record:

- Chosen profile and palette-role mapping.
- Display, reading, and code/metadata font roles.
- Its one or two distinctive choices and why they fit the task.
- Any accessibility-driven deviations and checks actually performed.

Keep site content, account details, and deployment configuration with that
application. The shared repository contains reusable design and assets.
