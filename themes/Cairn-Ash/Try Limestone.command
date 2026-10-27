#!/bin/zsh
set -eu
THEME_DIR="${0:A:h}"
/usr/bin/open -na /Applications/kitty.app --args --config "$THEME_DIR/kitty/light.conf" --title "Cairn Ash / Limestone trial" --directory "$THEME_DIR" /bin/zsh -l
