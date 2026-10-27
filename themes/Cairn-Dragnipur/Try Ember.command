#!/bin/zsh
set -eu
THEME_DIR="${0:A:h}"
/usr/bin/open -na /Applications/kitty.app --args --config "$THEME_DIR/kitty/ember.conf" --title "Cairn / Dragnipur — Ember preview" --directory "$THEME_DIR" /bin/zsh "$THEME_DIR/source/terminal-preview.zsh" Ember
