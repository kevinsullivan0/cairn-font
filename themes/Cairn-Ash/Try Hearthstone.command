#!/bin/zsh
set -eu
THEME_DIR="${0:A:h}"
/usr/bin/open -na /Applications/kitty.app --args --config "$THEME_DIR/kitty/dark.conf" --title "Cairn Ash / Hearthstone trial" --directory "$THEME_DIR" /bin/zsh -l
