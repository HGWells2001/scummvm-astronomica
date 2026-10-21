"""Run original-data ScummVM v14 regression suites in isolated save/config directories.

This is NOT an automated full playthrough. Only the original game's own
native engine regressions are exercised. No original artwork or save data is
uploaded or copied to a repository. A complete manual playthrough is still
required before claiming Astronomica is completable.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

# The expected marker is emitted only when that native check reaches its
# success branch. We do not accept exit-code zero alone as evidence.
CHECKS = {
    "core": (
        ("astronomica_verify", "Astronomica script verification: PASS"),
        ("astronomica_verify_transitions", "Astronomica transition integration verification: PASS"),
        ("astronomica_verify_game_state", "Astronomica game state interaction verification: PASS"),
        ("astronomica_verify_endings", "Astronomica endings interaction verification: PASS"),
        ("astronomica_verify_postcredits", "Astronomica post-credits verification: PASS"),
    ),
    "saves": (
        ("astronomica_verify_rocket_saves", "Astronomica rocket saves: PASS"),
        ("astronomica_verify_builder_saves", "Astronomica builder saves: PASS"),
        ("astronomica_verify_p517_saves", "Astronomica P517 saves: PASS"),
    ),
    "av": (
        ("astronomica_verify_intro", "Astronomica intro verification: PASS"),
        ("astronomica_verify_audio_channels", "Astronomica audio channel verification: PASS"),
        ("astronomica_verify_world29", "Astronomica P29"),
        ("astronomica_verify_help", "Astronomica help verification: PASS"),
    ),
}

def plan(selection):
    if selection == "all":
        return CHECKS["core"] + CHECKS["saves"] + CHECKS["av"]
    return CHECKS[selection]


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as reader:
        for chunk in iter(lambda: reader.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_config(game_dir, flag):
    if not flag.startswith("astronomica_verify") or flag not in {item[0] for group in CHECKS.values() for item in group}:
        raise ValueError("Unknown native regression flag")
    path = game_dir.as_posix().replace("\\", "/")
    if "\n" in path or "\r" in path:
        raise ValueError("Invalid game data directory")
    return (
        "[scummvm]\n"
        "enable_unsupported_game_warning=false\n"
        "confirm_exit=false\n"
        "gui_theme=builtin\n"
        "[astronomica-audit]\n"
        "engineid=astronomica\n"
        "gameid=astronomica\n"
        f"path={path}\n"
        f"{flag}=true\n"
    )


def scan_verdict(returncode, combined_log, marker):
    return returncode == 0 and marker.lower() in combined_log.lower() and " FAIL" not in "\n".join(
        line for line in combined_log.splitlines() if line.startswith("Astronomica ") and "verification:" in line
    )


def execute(exe, game_dir, output, selected, timeout):
    if not exe.is_file():
        raise FileNotFoundError(f"ScummVM executable missing: {exe}")
    if not (game_dir / "PLACES" / "GAMEDATA").is_file():
        raise FileNotFoundError("Missing PLACES/GAMEDATA in original game directory")
    output.mkdir(parents=True, exist_ok=False)
    summary = {
        "scope": "Native deterministic regressions, not a real end-to-end human gameplay proof",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scummvm_sha256": sha256_file(exe),
        "selection": selected,
        "checks": [],
    }
    env = os.environ.copy()
    # A real audio backend is intentional: SDL dummy was found to distort
    # timing comparisons in the historic P537/P516 regressions.
    env.pop("SDL_VIDEODRIVER", None)
    env.pop("SDL_AUDIODRIVER", None)
    try:
        engine_list = subprocess.run(
            [str(exe), "--list-engines"],
            capture_output=True, text=True, errors="replace", timeout=30, env=env
        )
        if engine_list.returncode != 0 or "astronomica" not in (engine_list.stdout + engine_list.stderr).lower():
            raise RuntimeError("This ScummVM build does not register the Astronomica engine")
        for key, marker in plan(selected):
            case_dir = output / key
            case_dir.mkdir()
            savepath = case_dir / "isolated-saves"
            savepath.mkdir()
            config = case_dir / "test.ini"
            config.write_text(make_config(game_dir, key), encoding="utf-8")
            logfile = case_dir / "native.log"
            cmd = [
                str(exe), "--config=" + str(config), "--savepath=" + str(savepath),
                "--logfile=" + str(logfile), "--debuglevel=1", "astronomica-audit"
            ]
            cwd = case_dir / "scratch"
            cwd.mkdir()
            print(f"Running native check: {key}", flush=True)
            try:
                result = subprocess.run(
                    cmd, cwd=cwd, env=env, capture_output=True, text=True,
                    errors="replace", timeout=timeout,
                )
                code = result.returncode
                captured = result.stdout + "\n" + result.stderr
                timed_out = False
            except subprocess.TimeoutExpired as exc:
                code = None
                captured = str(exc)
                timed_out = True
            (case_dir / "console.log").write_text(captured, encoding="utf-8", errors="replace")
            engine_log = logfile.read_text(encoding="utf-8", errors="replace") if logfile.is_file() else ""
            # Screenshots/decoded original assets created by some native
            # tests stay in scratch only. Never include them in the report.
            combined = engine_log + "\n" + captured
            passed = not timed_out and scan_verdict(code, combined, marker)
            summary["checks"].append({
                "flag": key,
                "status": "PASS" if passed else "TIMEOUT" if timed_out else "FAIL",
                "exit_code": code,
                "expected_marker": marker,
                "marker_found": marker.lower() in combined.lower(),
                "native_log": str(logfile.relative_to(output)) if logfile.is_file() else None,
                "console_log": str((case_dir / "console.log").relative_to(output)),
            })
            if not passed:
                print(f"FAILED: {key}. See {case_dir / 'console.log'} and native.log", flush=True)
                break
        summary["passed"] = bool(summary["checks"]) and len(summary["checks"]) == len(plan(selected)) and all(
            x["status"] == "PASS" for x in summary["checks"]
        )
    except Exception as exc:
        summary["passed"] = False
        summary["error"] = str(exc)
        raise
    finally:
        (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, default=Path("scummvm.exe"))
    parser.add_argument("--game-dir", type=Path, default=Path("game_data"))
    parser.add_argument("--output", type=Path, default=None, help="New directory; existing folders are never overwritten")
    parser.add_argument("--suite", choices=("core", "saves", "av", "all"), default="core")
    parser.add_argument("--timeout", type=int, default=900, help="Seconds per native test")
    args = parser.parse_args(argv)
    if args.timeout < 30 or args.timeout > 3600:
        parser.error("--timeout must be between 30 and 3600 seconds")
    report_dir = args.output if args.output else Path("astronomica-diagnostics-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"))
    try:
        report = execute(args.exe.resolve(), args.game_dir.resolve(), report_dir.resolve(), args.suite, args.timeout)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    print("Native check summary:", "PASS" if report["passed"] else "FAIL", "({} checks)".format(len(report["checks"])))
    print("Evidence:", (report_dir / "summary.json").resolve())
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
