"""Bundle redistributable MinGW DLL dependencies for the compiled ScummVM binary.

Only DLLs present in the included MSYS2 toolchain are copied. DLLs supplied by
Windows itself are never copied.
"""
from collections import deque
from pathlib import Path
import re
import shutil
import subprocess
import sys

def collect(executable: Path, compiler: Path) -> list[str]:
    destination = executable.parent
    compiler_bin = compiler.parent
    queue = deque([executable])
    seen = set()
    while queue:
        item = queue.popleft()
        out = subprocess.run(
            ["objdump", "-p", str(item)], check=True, capture_output=True, text=True
        ).stdout
        for name in re.findall(r"DLL Name:\s*([^\r\n]+)", out, re.I):
            name = name.strip()
            key = name.casefold()
            source = compiler_bin / name
            if source.is_file() and key not in seen:
                seen.add(key)
                target = destination / source.name
                shutil.copy2(source, target)
                queue.append(target)
    return sorted(seen)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: collect_mingw_dlls.py scummvm.exe path/to/g++")
    print("Bundled runtime DLLs:", collect(Path(sys.argv[1]), Path(sys.argv[2])))
