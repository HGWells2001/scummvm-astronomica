#!/usr/bin/env bash
set -euo pipefail
# Must run from MSYS2 MINGW64, not a generic Git Bash.
if [[ "${MSYSTEM:-}" != "MINGW64" ]]; then
  echo "Run this from MSYS2 MINGW64, not Git Bash." >&2
  exit 2
fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
pacman -Syu --noconfirm
pacman -S --needed --noconfirm git make mingw-w64-x86_64-gcc mingw-w64-x86_64-SDL2 mingw-w64-x86_64-pkgconf mingw-w64-x86_64-python mingw-w64-x86_64-zlib mingw-w64-x86_64-libpng
python tools/verify_export.py
python tools/prepare_scummvm.py
cd work/fresh-20260913/scummvm
./configure --disable-all-engines --enable-engine=astronomica
make -j"${ASTRO_BUILD_JOBS:-4}"
./scummvm.exe --list-engines | grep -i astronomica
echo "Astronomica engine built successfully."
