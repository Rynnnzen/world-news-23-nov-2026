#!/usr/bin/env python3
"""Entry point for the make.fun news-image-20261123 entry.

The image is already drawn and shipped in assets/entry.png; this program
copies it to the output directory and proves the copy is byte for byte the
shipped file. It is standard library only and makes no network calls.

Output directory precedence:
    1. --output-dir PATH
    2. $MAKEFUN_OUTPUT_DIR
    3. /output
"""

import argparse
import hashlib
import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SOURCE = REPO_ROOT / "assets" / "entry.png"
BUFFER = 1024 * 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1048576
MAX_DIMENSION = 1024


def png_dimensions(path):
    """Read width and height from a PNG IHDR without any third-party library."""
    with open(path, "rb") as fh:
        header = fh.read(24)
    if len(header) < 24 or header[:8] != PNG_SIGNATURE:
        raise ValueError("%s is not a PNG file" % path)
    if header[12:16] != b"IHDR":
        raise ValueError("%s has no PNG IHDR header" % path)
    width = int.from_bytes(header[16:20], "big")
    height = int.from_bytes(header[20:24], "big")
    return width, height


def check_gate(path):
    """Fail early if the shipped image breaks the competition's size limits."""
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError("%s is %d bytes, over the %d byte limit"
                         % (path, size, MAX_BYTES))
    width, height = png_dimensions(path)
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValueError("%s is %dx%d, over the %dx%d limit"
                         % (path, width, height, MAX_DIMENSION, MAX_DIMENSION))
    return size, width, height


def sha256_file(path):
    """Return the hex SHA-256 of a file, reading it in fixed-size blocks."""
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(BUFFER)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def resolve_output_dir(cli_value):
    """Pick the output directory: flag, then env var, then /output."""
    if cli_value:
        return Path(cli_value).expanduser()
    env_value = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_value:
        return Path(env_value).expanduser()
    return Path("/output")


def copy_atomically(source, destination):
    """Copy source to destination through a temp file in the same directory.

    Returns (sha256, byte count). The temp file is flushed and fsynced before
    os.replace, so readers of destination never see a partial image.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    # The prefix must start with a letter/digit/underscore: the grader rejects
    # output paths whose segments begin with a dot.
    fd, tmp_name = tempfile.mkstemp(prefix="entry-", suffix=".png.tmp",
                                    dir=str(destination.parent))
    tmp_path = Path(tmp_name)
    digest = hashlib.sha256()
    total = 0
    try:
        with open(source, "rb") as src, os.fdopen(fd, "wb") as dst:
            while True:
                chunk = src.read(BUFFER)
                if not chunk:
                    break
                digest.update(chunk)
                dst.write(chunk)
                total += len(chunk)
            dst.flush()
            os.fsync(dst.fileno())
            # mkstemp creates the temp file 0600; the grader runs as another
            # user and must be able to read the output, so set it world-readable
            # before the rename carries this mode onto the final entry.png.
            os.fchmod(dst.fileno(), 0o644)
        os.replace(tmp_path, destination)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise
    return digest.hexdigest(), total


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Copy the shipped news image to the make.fun output directory.")
    parser.add_argument("--output-dir", default=None,
                        help="directory to write entry.png into "
                             "(default: $MAKEFUN_OUTPUT_DIR, then /output)")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    if not SOURCE.is_file():
        sys.exit("error: shipped image is missing: %s" % SOURCE)

    try:
        source_size, source_w, source_h = check_gate(SOURCE)
    except (OSError, ValueError) as exc:
        sys.exit("error: %s" % exc)

    output_dir = resolve_output_dir(args.output_dir)
    destination = output_dir / "entry.png"

    expected = sha256_file(SOURCE)
    written, size = copy_atomically(SOURCE, destination)

    if written != expected:
        try:
            destination.unlink()
        except FileNotFoundError:
            pass
        sys.exit("error: checksum of written copy does not match the shipped "
                 "image (wrote %s, expected %s)" % (written, expected))

    actual = sha256_file(destination)
    if actual != expected:
        sys.exit("error: checksum of %s changed after it was written "
                 "(found %s, expected %s)" % (destination, actual, expected))

    print("wrote %s (%d bytes, %dx%d PNG)" % (destination, size, source_w, source_h))
    print("sha256 %s" % actual)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
