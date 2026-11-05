# Cairn design language

Cairn is a family of readable, useful interfaces built from a restrained stone
palette, carved display type, and clear working surfaces. Its character should
come from typography, proportions, material, and the content itself, rather than
from a stock landing-page layout.

This document carries Cairn's type and material decisions into websites and small
tools. The [web interface guide](docs/web-interface-guide.md) turns them into
implementation defaults and a review checklist. These are design guidelines, not
a shipped component library or a claim that every existing specimen follows them.
See [web profiles](docs/web-profiles.md) for distinct expressions of the family;
the Ash palette is one edition, not the limit of Cairn's identity.

## Keep the identity; fit the task

1. **Start with the work.** A reading page should open into readable text. A
   collection should make its records easy to scan, through rows or meaningful
   material cards. A tool should expose the next useful action. Do not add a
   hero, dashboard, or card grid by habit.
2. **Use the material palette by role.** Cool slate or warm limestone forms the
   canvas. Soft ink carries text. Bronze marks focus and deliberate action;
   patina distinguishes links. Copper is a selective emphasis, not a wash over
   every heading. Keep semantic states understandable without color alone.
3. **Reserve carved type for places with room.** Cairn gives the brand, title,
   or a major heading its identity. Dense navigation, metadata, long prose, and
   code must stay comfortable to read. A page does not need Cairn on every word
   to belong to the family.
4. **Build hierarchy with alignment and spacing.** Prefer shared edges, a
   bounded reading column, simple rules, and a four-pixel spacing rhythm.
   Group related records before enclosing them. Separate secondary navigation
   from the main reading or working surface.
5. **Keep decoration structural.** Use a quiet foundation appropriate to the profile.
   Relic and Bronze may add shallow ledges, worn edges, or mineral variation
   to structural surfaces. Do not put grit, cracks, artwork, or an overlay
   across glyphs. Never clip text, selection, focus, or a control's hit area.
6. **Compact does not mean tiny.** Reduce redundant wrappers, oversized gaps,
   repeated labels, and unnecessary controls before reducing text size.
   Material editions share the same type and control scale.
7. **Make controls honest and quiet.** Use specific verbs and recognizable
   links. Keep hover, current, focus, pressed, disabled, loading, and empty
   states distinct. Display only information and actions that actually exist.

## Avoid the interchangeable template

Do not add these without a concrete reason grounded in the page's purpose:

- A large centered slogan followed by three equally sized feature cards.
- Gradient blobs, neon glow, glass panels, pill-shaped containers everywhere,
  or large floating shadows as a substitute for hierarchy.
- An icon on every label, repeated badges, decorative statistics, or empty
  charts that add no information.
- Excessively large headings, narrow content trapped inside oversized padding,
  or a small useful area surrounded by promotional copy.
- Fantasy illustration, faux parchment, or distressing applied to every edge.
  Cairn's stone character is restrained; it is not a themed prop.
- Fabricated activity, dates, counts, endorsements, or claims of verification.

These are defaults for this design language, not universal bans. Departures
should solve a specific problem and remain consistent with the reading and
interaction priorities above.

## What stays shared and what may vary

**Shared:** semantic color roles, soft ink, stone/paper material relationships,
restrained depth, clear focus, honest metadata, and a separation between
display lettering and sustained reading. Four-pixel spacing and small control
radii are useful shared defaults; expressive content surfaces may vary.

**Task-specific:** navigation depth, number of columns, body font, reading width,
record layout, density, imagery needed to explain the subject, and material
edition. A reference index and a focused reader should look related without
being forced into the same layout.

Give each application room for one or two distinctive choices, such as a title
treatment, divider motif, or reading rhythm. Keep the shared color roles,
material restraint, and interaction behavior underneath. Family resemblance
should be apparent without repeating the same header, card shape, or ornament
on every page.

Record a new site's chosen profile and justified exceptions in its own README.
Change these shared guidelines only when the decision should carry to other
sites. Keep project content and deployment details in that project.

## Existing sources

- [Cairn Ash material tokens](themes/Cairn-Ash/material.json): color roles and
  four-pixel spacing scale.
- [Reusable material CSS](themes/Cairn-Ash/material.css): exported CSS variables,
  display/text/code roles, 720px reading width, 3px radius, and material assets.
- [Cairn Ash README](themes/Cairn-Ash/README.md): editions, construction, and
  measured contrast with verification limits.
- [Design notes](themes/Cairn-Ash/DESIGN-NOTES.md): selective ornament, compact
  utility type, unchanged control scale, and unblocked focus and selection.
- [Web font CSS](web/cairn.css), [mono CSS](web/cairn-mono.css), and
  [licensing](LICENSING.md): real font assets and redistribution requirements.
