#!/bin/zsh
set -eu
THEME_DIR="${0:A:h}"
/usr/bin/open -na /Applications/kitty.app --args --config "$THEME_DIR/kitty/dark.conf" --override "font_family=Cairn Mono" --title "Cairn Ash / Hearthstone + Cairn Mono trial" --directory "$THEME_DIR" /bin/zsh -l
