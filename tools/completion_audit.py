"""Evidence-only preflight for a user's *original* Astronomica English CD ZIP.

Checks all puzzle, start and ending resources, then parses every scene using
the repository's original-format reader. Does not execute game scripts or
claim that any route is winnable. Never exports copyrighted game contents.
"""
import argparse
import hashlib
import importlib.util
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SCENES = 421
MUST_HAVE = set(range(501, 538)) | {0, 1, 423, 424, 425, 426, 427, 428, 429, 432, 433, 435, 436, 437}
SCENE_RE = re.compile(r"^PLACES/P([0-9]+)/MEGAFILE\.HYP$", re.I)
TAIL_RE = re.compile(r"^trailing ([0-9]+) bytes at 0x([0-9a-f]+)$")


def index_scenes(names):
    found = {}
    duplicate = []
    for name in names:
        match = SCENE_RE.fullmatch(name)
        if not match:
            continue
        number = int(match.group(1))
        if number in found:
            duplicate.append({"scene": number, "files": [found[number], name]})
        else:
            found[number] = name
    return found, duplicate


def _load_reader():
    path = ROOT / "outputs" / "astronomica-cleanroom" / "astro_reader.py"
    spec = importlib.util.spec_from_file_location("astronomica_original_reader", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _commands(value):
    if isinstance(value, dict):
        if "opcode" in value and "args" in value:
            yield value
        else:
            for item in value.values():
                yield from _commands(item)
    elif isinstance(value, list):
        for item in value:
            yield from _commands(item)


def decode_scene(reader, data):
    try:
        return reader.parse(data), 0
    except reader.FormatError as exc:
        match = TAIL_RE.fullmatch(str(exc))
        if not match:
            raise
        boundary = int(match.group(2), 16)
        if not 0 < boundary < len(data) or len(data) - boundary != int(match.group(1)):
            raise ValueError("Invalid trailing resource offset") from exc
        return reader.parse(data[:boundary]), len(data) - boundary


def audit_archive(archive_path, deep=True):
    from game_archive import inspect_archive
    info = inspect_archive(archive_path)
    results = {
        "scope": "English-CD static resource integrity, NOT a playable-route test",
        "archive_files": info["files"],
        "uncompressed_bytes": info["uncompressed_bytes"],
        "source_executable": info["executable"],
    }
    with zipfile.ZipFile(archive_path) as archive:
        scenes, duplicates = index_scenes(archive.namelist())
        missing = sorted(MUST_HAVE - scenes.keys())
        results.update(
            scene_count=len(scenes),
            expected_scene_count=EXPECTED_SCENES,
            missing_required_scenes=missing,
            duplicate_scene_ids=duplicates,
            all_required_present=not missing and not duplicates and len(scenes) == EXPECTED_SCENES,
        )
        if deep:
            reader = _load_reader()
            errors = []
            destinations = {}
            tail_count = 0
            modes = {}
            for scene_id, name in sorted(scenes.items()):
                try:
                    parsed, trailing = decode_scene(reader, archive.read(name))
                    tail_count += bool(trailing)
                    modes[str(scene_id)] = parsed["mode"]
                    jumps = sorted({int(c["args"][0]) for c in _commands(parsed)
                                    if c["opcode"] == 5 and c["args"]})
                    if jumps:
                        destinations[str(scene_id)] = jumps
                except (reader.FormatError, ValueError, IndexError, KeyError) as exc:
                    errors.append({"scene": scene_id, "error": str(exc)[:300]})
            missing_jumps = sorted({dest for values in destinations.values() for dest in values if dest >= 0 and dest not in scenes})
            results.update(
                parsed_scenes=len(scenes) - len(errors),
                scene_parse_errors=errors,
                scenes_with_trailing_data=tail_count,
                direct_scene_transitions=sum(len(v) for v in destinations.values()),
                unresolved_literal_destinations=missing_jumps,
                # Literal destinations can intentionally be symbolic; inspect before classifying a bug.
                unresolved_destination_note="Potential issues only: special or dynamic destination IDs may be intentional",
                entry_to_end_proven=False,
            )
        else:
            results["deep_scan_skipped"] = True
    results["preflight_pass"] = bool(results["all_required_present"] and not results.get("scene_parse_errors"))
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Original ASTROeng ZIP")
    parser.add_argument("--out", type=Path, default=Path("completion-audit.json"), help="JSON evidence report")
    parser.add_argument("--fast", action="store_true", help="Check ZIP, required files and signatures only")
    args = parser.parse_args(argv)
    try:
        report = audit_archive(args.archive, deep=not args.fast)
    except (ValueError, OSError, zipfile.BadZipFile, ImportError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Scenes:", report["scene_count"], "required complete:", report["all_required_present"])
    print("Preflight:", "PASS" if report["preflight_pass"] else "FAIL", "(static resources only)")
    print("Report:", args.out.resolve())
    return 0 if report["preflight_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
