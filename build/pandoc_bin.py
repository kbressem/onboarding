"""Find a pandoc executable that runs on this computer.

Set the environment variable PANDOC to use a specific pandoc binary, for
example PANDOC=/opt/homebrew/bin/pandoc make docx.
"""

import errno
import os
import re
import shutil
import subprocess
import sys

MIN_VERSION = (3, 0)
EBADARCH = getattr(errno, "EBADARCH", 86)   # macOS: "Bad CPU type in executable"

MSG_MISSING = """pandoc not found.
Install pandoc 3.x:
  macOS (Apple silicon or Intel): brew install pandoc
  or the installer for your processor from https://github.com/jgm/pandoc/releases
"""

MSG_ARCH = """pandoc at {exe} cannot run on this computer ({err}).
The pandoc binary is for a different processor type.

Find the cause:
  uname -m            # arm64 = Apple silicon, x86_64 = Intel
  file {exe}

Fix on Apple silicon (arm64):
  1. Remove the Intel pandoc. If you used the .pkg installer, run the
     uninstall script from https://pandoc.org/installing.html
  2. Install the native pandoc: brew install pandoc
     or pandoc-<version>-arm64-macOS.pkg from https://github.com/jgm/pandoc/releases
  Quick alternative: install Rosetta 2 with
     softwareupdate --install-rosetta --agree-to-license

Then open a new terminal and run: pandoc --version
"""


def pandoc_executable():
    exe = os.environ.get("PANDOC") or shutil.which("pandoc")
    if not exe:
        sys.exit(MSG_MISSING)
    try:
        out = subprocess.run([exe, "--version"], capture_output=True, text=True,
                             check=True).stdout
    except OSError as e:
        if e.errno in (errno.ENOEXEC, EBADARCH):
            sys.exit(MSG_ARCH.format(exe=exe, err=e.strerror))
        raise
    m = re.search(r"pandoc(?:\.exe)?\s+(\d+)\.(\d+)", out)
    if m and (int(m.group(1)), int(m.group(2))) < MIN_VERSION:
        sys.exit(f"pandoc {m.group(1)}.{m.group(2)} at {exe} is too old. "
                 f"Install pandoc {MIN_VERSION[0]}.x or newer.\n\n{MSG_MISSING}")
    return exe
