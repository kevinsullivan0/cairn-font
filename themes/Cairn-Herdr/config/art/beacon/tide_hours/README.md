# The Hours of Bellweather Reach

Four views of an inhabited sky island. The day follows a linen-sailed ferry past the abbey. Its square lantern tower, copper roofs and viaduct reappear from different bearings. Clear morning haze gives way to an afternoon cumulus bank, swifts crossing the evening sky, and lamps beneath the moon.

The 960 × 3360 RGB PNG masters are in `masters/`. The active sidebar copies are 512 × 1792 opaque JPEGs. They have a localized dark glaze beneath the left-hand labels. The masters preserve the daylight values.

From this folder, with Python 3, Pillow and a C++17 compiler installed, repaint the entire sequence with

```sh
python3 paint_hours.py all --runtime ../../../backgrounds/cairn/cycle
```

For a small proof of a single hour, run

```sh
python3 paint_hours.py evening --width 320 --out /tmp/bellweather-proof
```

`paint_hours.py` stages the original architecture, cliffs, vegetation, sailboat and successive viewpoints. It uses the parent `raster.Canvas` for its RGB board and hand-placed paint marks. The native companion `oil.cpp` rasterizes the weather, rock, masonry and cast shadows into that board, then repaints it with coarse-to-fine, edge-following bristle marks. All geometry, weather, paint textures and details are generated locally from the recipe and fixed seeds.
