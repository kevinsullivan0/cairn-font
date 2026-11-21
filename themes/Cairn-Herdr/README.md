# Cairn Gallery for Herdr

A blue terminal palette, mottled brass chrome, and a sidebar that can follow a four-painting day cycle, hold a fixed choice, or show a local image.

## Install

Use Herdr 0.1.16. Merge the contents of `config/` into your Herdr app home, ordinarily `~/.config/herdr-app`. Compare any same-named files before overwriting an existing customization. Select `cairn-gallery` from the layout picker, or run:

```sh
herdr-app do layout.switch '{"name":"cairn-gallery"}'
```

`keys.fragment.json` is an optional key section to merge into your existing `keys.json`. The Cairn font is optional. The layout uses Herdr’s shipped panels and icons for the default workspace controls.

Use the picture-frame button beside Settings to pick art. Auto checks the local clock every 30 seconds. Morning begins at 05:00, afternoon at 12:00, evening at 17:00, and night at 21:00. To restore the 256 px sidebar width while the layout is active:

```sh
herdr-app do layout.resize '{"id":"sidebar","px":256}'
```

This release edition uses the bundled Herdr panels and omits the optional Codex account usage panel.

## Artwork and sources

[The Hours of Bellweather Reach](config/art/beacon/tide_hours/contact-sheet.jpg) has four 960 × 3360 masters and smaller opaque sidebar editions. The [recipe](config/art/beacon/tide_hours/README.md) reproduces the art offline. The three fixed studies and their source are also included.

The files under `config/mods/` marked `cloned_from` are modified Herdr 0.1.16 mods. Their upstream license and notices are included under `licenses/`. Cairn’s locally imported art, live preferences, session data, and wallpaper-derived images are excluded from this package.

The modified Herdr files retain their upstream Apache 2.0 terms. The original Cairn files use the repository’s [project license](../../LICENSE).
