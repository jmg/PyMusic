"""Console interface — replaces the legacy ``interfaces/console.py``.

Usage::

    pymusic scan /path/to/music
    pymusic search "depeche mode"
    pymusic stats
    pymusic radios list
    pymusic radio add URL --name "Metro 95.1"
    pymusic playlist export "rock" /tmp/rock --max-mb 700
    pymusic clean
    pymusic gui
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from . import __version__, library
from .config import configure
from .tags import format_duration


def _cmd_scan(args: argparse.Namespace) -> int:
    last = [0]

    def report(progress):
        if progress.scanned - last[0] >= 100:
            last[0] = progress.scanned
            print(f"  scanned={progress.scanned} added={progress.added} "
                  f"skipped={progress.skipped}", file=sys.stderr)

    print(f"Scanning {args.path} ...", file=sys.stderr)
    result = library.scan_directory(args.path, on_progress=report)
    print(f"Done. Added {result.added}, skipped {result.skipped} "
          f"(of {result.scanned} files).")
    return 0


def _cmd_search(args: argparse.Namespace) -> int:
    songs = library.search_songs(args.query)
    for song in songs[: args.limit]:
        print(f"{song.id:6d}  {song.artist or '-':30.30s}  "
              f"{song.display_title:40.40s}  {song.album or '-':25.25s}  "
              f"[{format_duration(song.duration or 0)}]")
    if not songs:
        print("(no matches)", file=sys.stderr)
        return 1
    return 0


def _cmd_stats(_args: argparse.Namespace) -> int:
    s = library.stats()
    print(f"Songs   : {s['songs']}")
    print(f"Artists : {s['artists']}")
    print(f"Albums  : {s['albums']}")
    print(f"Radios  : {s['radios']}")
    print(f"Total   : {format_duration(s['duration'])}")
    return 0


def _cmd_clean(_args: argparse.Namespace) -> int:
    removed = library.remove_missing_files()
    print(f"Removed {removed} entries with missing files.")
    return 0


def _cmd_radios_list(_args: argparse.Namespace) -> int:
    radios = library.fetch_radios()
    if not radios:
        print("(no radios)")
        return 0
    for r in radios:
        print(f"{r.id:4d}  {r.name or '(unnamed)':25.25s}  {r.url}")
    return 0


def _cmd_radio_add(args: argparse.Namespace) -> int:
    radio = library.add_radio(args.url, name=args.name or "", genre=args.genre or "")
    print(f"Added radio #{radio.id}: {radio.name or radio.url}")
    return 0


def _cmd_radio_remove(args: argparse.Namespace) -> int:
    if library.delete_radio(args.id):
        print(f"Removed radio #{args.id}")
        return 0
    print(f"No radio with id {args.id}", file=sys.stderr)
    return 1


def _cmd_export(args: argparse.Namespace) -> int:
    print(f"Exporting songs matching {args.query!r} into {args.dest} "
          f"(<= {args.max_mb} MB)", file=sys.stderr)
    result = library.generate_playlist_to_dir(
        filter_query=args.query,
        destination=args.dest,
        max_size_mb=args.max_mb,
    )
    mb = result.total_bytes / (1024 * 1024)
    print(f"Copied {result.copied} songs ({mb:.1f} MB), "
          f"skipped {result.skipped}.")
    if result.errors:
        print(f"({len(result.errors)} errors)", file=sys.stderr)
    return 0


def _cmd_gui(_args: argparse.Namespace) -> int:
    from .gui.app import main as gui_main
    return gui_main()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pymusic",
        description="Modern music player and library manager.",
    )
    parser.add_argument("--version", action="version", version=f"pymusic {__version__}")
    parser.add_argument("--db", type=Path, help="Override database path.")
    parser.add_argument("-v", "--verbose", action="count", default=0)

    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("scan", help="Scan a directory and import audio files.")
    p.add_argument("path", type=Path)
    p.set_defaults(func=_cmd_scan)

    p = sub.add_parser("search", help="Search the library.")
    p.add_argument("query", nargs="?", default="")
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=_cmd_search)

    p = sub.add_parser("stats", help="Show library statistics.")
    p.set_defaults(func=_cmd_stats)

    p = sub.add_parser("clean", help="Remove library entries whose files are missing.")
    p.set_defaults(func=_cmd_clean)

    p = sub.add_parser("radios", help="List configured radio streams.")
    p.set_defaults(func=_cmd_radios_list)

    p = sub.add_parser("radio", help="Manage a radio stream.")
    rsub = p.add_subparsers(dest="radio_cmd", required=True)
    rp = rsub.add_parser("add")
    rp.add_argument("url")
    rp.add_argument("--name", default="")
    rp.add_argument("--genre", default="")
    rp.set_defaults(func=_cmd_radio_add)
    rp = rsub.add_parser("remove")
    rp.add_argument("id", type=int)
    rp.set_defaults(func=_cmd_radio_remove)

    p = sub.add_parser("export", help="Copy songs matching a query into a directory.")
    p.add_argument("query")
    p.add_argument("dest", type=Path)
    p.add_argument("--max-mb", type=int, default=700, help="Size budget in MB.")
    p.set_defaults(func=_cmd_export)

    p = sub.add_parser("gui", help="Launch the graphical interface.")
    p.set_defaults(func=_cmd_gui)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose >= 2 else logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )
    if args.db is not None:
        configure(args.db)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
