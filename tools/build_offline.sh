#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Uses only the bundled source and bundled MSYS2 toolchain.
set -euo pipefail
: "${ASTRO_OFFLINE_ROOT:?Root not provided by COMPILA.cmd}"
base="$(cygpath -u "$ASTRO_OFFLINE_ROOT")"
cd "$base/scummvm"

for executable in gcc g++ make cmp sed python; do
  command -v "$executable" >/dev/null || { echo "Missing offline compiler dependency: $executable" >&2; exit 1; }
done
[[ -f engines/astronomica/configure.engine ]] || { echo "Missing custom Astronomica engine" >&2; exit 1; }
[[ -f video/paused_audio_gate.h ]] || { echo "Missing ASVM31 video-core overlay" >&2; exit 1; }
if [[ "${ASTRO_OFFLINE_CHECK:-0}" == "1" ]]; then
  echo "Offline prerequisites PASS: source, compiler, MSYS2 tools, paired engine/core."
  g++ --version | head -n 1
  exit 0
fi
echo "Configuring pinned ScummVM for custom Astronomica engine (offline)..."
# MSYS2 needs a writable /tmp, which was intentionally left out of the archive.
mkdir -p /tmp
printf 'int main(){return 0;}\n' > /tmp/astronomica-compiler-smoke.cpp
g++ -std=c++14 /tmp/astronomica-compiler-smoke.cpp -o /tmp/astronomica-compiler-smoke.exe
/tmp/astronomica-compiler-smoke.exe
rm -f /tmp/astronomica-compiler-smoke.cpp /tmp/astronomica-compiler-smoke.exe
if ! ./configure --disable-all-engines --enable-engine=astronomica; then
  echo "ScummVM configure failed, diagnostics:" >&2
  if [[ -f config.log ]]; then tail -n 120 config.log >&2; fi
  exit 1
fi
# Pinned configure appends -std=c++11 even after environment CXXFLAGS.
# This exact ASVM31 MinGW compatibility build requires C++14.
sed -i 's/-std=c++11/-std=c++14/g; s/-std=gnu++11/-std=gnu++14/g' config.mk
printf '\nCXXFLAGS += -std=c++14\n' >> config.mk
make -j"${ASTRO_OFFLINE_JOBS:-2}"
./scummvm.exe --list-engines | grep -i astronomica
mkdir -p "$base/bin"
cp scummvm.exe "$base/bin/scummvm.exe"
python "$base/tools/collect_mingw_dlls.py" "$base/bin/scummvm.exe" "$(command -v g++)"
echo "Offline Windows x64 build PASS."
