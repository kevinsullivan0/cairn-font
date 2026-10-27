#!/bin/zsh
printf '\n  CAIRN / DRAGNIPUR — %s\n\n' "$1"
printf '  A temporary window. Close it to finish; your normal config is unchanged.\n\n'
printf '  \033[31mRed: error\033[0m    \033[32mGreen: success\033[0m    \033[33mGold: warning\033[0m\n'
printf '  \033[34mSteel: paths\033[0m  \033[35mMauve: keywords\033[0m   \033[36mSage: accents\033[0m\n\n'
printf '  Il1 O0 rn m    () [] {}    0123456789\n\n'
printf '  Your shell is ready below.\n\n'
exec /bin/zsh -l
