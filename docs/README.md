# Documentation map

Cairn now includes a design language, reusable material, desktop themes, and two
font families. Start with the part you need; the existing font and theme paths
remain stable.

## Design websites and tools

1. [Design language](../DESIGN-LANGUAGE.md): shared identity, anti-patterns,
   and room for application-specific flair.
2. [Web profiles](web-profiles.md): Stone and paper or Ash, typography roles,
   palette mapping, and existing material assets.
3. [Web interface guide](web-interface-guide.md): implementation, readable
   layouts, controls, truthful metadata, licensing, and review checklist.

## Use the fonts

- [Font quick start](../README.html), [build and usage guide](../USAGE.md).
- [Cairn specimen](../specimen.html), [Cairn Mono specimen](../mono-specimen.html),
  and [Mono spacing comparison](../mono-spacing.html). Download and open these
  HTML files locally; they include embedded fonts.
- [Web font files and CSS](../web), [desktop fonts](../desktop), and
  [rendering proofs](../proofs).

## Use or extend themes and material

- [Cairn Ash](../themes/Cairn-Ash/README.md): Everyday, Relic, Bronze, dark/light
  modes, Obsidian themes, Kitty palettes, and validation limits.
- [Material JSON](../themes/Cairn-Ash/material.json) and
  [material CSS](../themes/Cairn-Ash/material.css): exported roles and assets.
- [Design notes](../themes/Cairn-Ash/DESIGN-NOTES.md): critique and refinement
  history, not a replacement for current usage instructions.
- [Earlier palette studies](../themes/Cairn-Dragnipur/README.md): Ember,
  Vellum, and studies that preceded Hearthstone.

## Repository layout and maintenance

| Location | Responsibility |
| --- | --- |
| `DESIGN-LANGUAGE.md`, `docs/` | Shared design guidance and navigation |
| `desktop/`, `web/` | Installable fonts and web distribution |
| `source/` | Font drawing, building, packaging, and validation |
| `proofs/`, root specimen HTML | Font examples and rendering evidence |
| `themes/Cairn-Ash/` | Current material system, themes, theme source, and proofs |
| `themes/Cairn-Dragnipur/` | Earlier palette studies and their source |
| Root reports and `manifest.json` | Existing font/package validation records |
| License files and `third-party/` | License boundaries and required notices |

Put new shared design guidance under `docs/`, font changes in the existing font
source/distribution paths, and theme-specific changes with that theme. Keep
generated outputs beside the paths their builders already expect. Do not move
or rename distributed fonts, theme folders, specimen HTML, or historical reports
just to make the root look tidier: existing links, downloads, and build scripts
depend on them. If a future migration is needed, provide compatibility paths
and test the affected builders and specimens.

Keep application content and deployments in the application repository. Add
generic reusable decisions here without copying private project information.
For asset changes, follow the relevant build guide and refresh only the reports
and manifests that its workflow generates. Documentation-only updates do not
imply that font or theme validation has been rerun.

## Licenses

Read [LICENSING.md](../LICENSING.md), [OFL](../OFL.txt), [MIT](../LICENSE), and
[third-party notices](../THIRD_PARTY_NOTICES.md) before redistributing assets.
