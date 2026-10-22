"""Inspect or safely unpack a user's original Astronomica game archive.

No game content is downloaded, modified, or added to source control.
"""
import argparse
import hashlib
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import tempfile
import zipfile

GAME_DATA_MD5 = "84099c2580e5c71beec97ca3e52a5967"
EXE_PREFIX_MD5 = "14929fa8e52d7e3bc539244413703ecb"
EXE_LENGTH = 418376
MAX_FILES = 10000
MAX_TOTAL_BYTES = 2 * 1024**3
MAX_FILE_BYTES = 512 * 1024**2


def _archive_entries(archive):
    files = {}
    total = 0
    for entry in archive.infolist():
        raw_name = entry.filename
        if "\\" in raw_name or ":" in raw_name or "\x00" in raw_name:
            raise ValueError(f"Unsafe archive name: {raw_name!r}")
        parts = PurePosixPath(raw_name).parts
        if not parts or raw_name.startswith("/") or any(p in (".", "..") for p in parts):
            raise ValueError(f"Unsafe archive path: {raw_name!r}")
        if entry.is_dir():
            continue
        mode = (entry.external_attr >> 16) & 0xFFFF
        if stat.S_IFMT(mode) == stat.S_IFLNK:
            raise ValueError(f"Archive contains a symbolic link: {raw_name}")
        key = "/".join(parts).casefold()
        if key in files:
            raise ValueError(f"Ambiguous duplicate file: {raw_name}")
        if entry.file_size > MAX_FILE_BYTES:
            raise ValueError(f"Oversized archive member: {raw_name}")
        total += entry.file_size
        if total > MAX_TOTAL_BYTES:
            raise ValueError("Archive uncompressed size exceeds safety limit")
        files[key] = entry
        if len(files) > MAX_FILES:
            raise ValueError("Archive contains too many files")
    return files, total


def inspect_archive(archive_path):
    with zipfile.ZipFile(archive_path) as archive:
        files, total = _archive_entries(archive)
        required = ("places/gamedata", "places/p1/megafile.hyp")
        for name in required:
            if name not in files:
                raise ValueError(f"Missing required original game file: {name}")
        data = archive.read(files["places/gamedata"])
        if hashlib.md5(data).hexdigest() != GAME_DATA_MD5 or len(data) != 1604:
            raise ValueError("GAMEDATA does not match the supported English edition")
        executables = [v for k, v in files.items() if k in ("setup/astroeng.exe", "setup/astro.exe", "astroeng.exe", "astro.exe")]
        exe = None
        for candidate in executables:
            with archive.open(candidate) as stream:
                prefix = stream.read(5000)
            if candidate.file_size == EXE_LENGTH and hashlib.md5(prefix).hexdigest() == EXE_PREFIX_MD5:
                exe = candidate
                break
        if exe is None:
            raise ValueError("No executable matching the supported Astronomica edition")
        # A full archive CRC check catches corruption before any output is created.
        bad_file = archive.testzip()
        if bad_file:
            raise ValueError(f"ZIP corruption detected in {bad_file}")
        return {"files": len(files), "uncompressed_bytes": total,
                "executable": exe.filename, "game_data": files["places/gamedata"].filename}


def extract_archive(archive_path, output):
    archive_path = Path(archive_path).resolve()
    output = Path(output).resolve()
    info = inspect_archive(archive_path)
    if output.exists():
        raise FileExistsError(f"Destination already exists, will not overwrite: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="astronomica-extract-", dir=output.parent) as temp:
        stage = Path(temp) / "game"
        stage.mkdir()
        with zipfile.ZipFile(archive_path) as archive:
            files, _ = _archive_entries(archive)
            for entry in files.values():
                path = stage.joinpath(*PurePosixPath(entry.filename).parts)
                path.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(entry) as source, path.open("wb") as target:
                    shutil.copyfileobj(source, target, length=1024 * 1024)
            # Put a copy at the game root for simple ScummVM directory detection.
            exe_name = Path(info["executable"]).name
            if (stage / exe_name).exists():
                pass
            else:
                shutil.copy2(stage.joinpath(*PurePosixPath(info["executable"]).parts), stage / exe_name)
        os.replace(stage, output)
    return info


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Your original Astronomica ZIP")
    parser.add_argument("--output", type=Path, default=Path("game_data"), help="Destination for game files")
    parser.add_argument("--verify-only", action="store_true", help="Check signatures and CRC without extracting")
    args = parser.parse_args(argv)
    try:
        result = inspect_archive(args.archive) if args.verify_only else extract_archive(args.archive, args.output)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        parser.exit(1, f"ERROR: {exc}\n")
    print("Astronomica archive verified:", result["files"], "files,", result["uncompressed_bytes"], "bytes")
    print("Supported executable:", result["executable"])
    if not args.verify_only:
        print("Game data extracted to:", args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
