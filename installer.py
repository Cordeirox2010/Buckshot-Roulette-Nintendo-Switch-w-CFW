#!/usr/bin/env python3
"""Buckshot Roulette - Nintendo Switch (Ubuntu/Kubuntu) port installer (unofficial).

Takes the user's OWN copy of the game (the .exe / .x86_64 / .pck from Steam), extracts the Godot
data pack, applies two tiny source patches, installs a Steam stub and a native arm64 Godot 4.1.1
runtime, and creates a launcher + desktop shortcut.  No game files are shipped with this tool.

Usage:  ./install.sh "/path/to/Buckshot Roulette.exe"  [--dest DIR] [--no-shortcut] [--force]
"""
import argparse
import hashlib
import os
import platform
import shutil
import stat
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAGIC = b"GDPC"
PACK_DIR_ENCRYPTED = 1
PACK_REL_FILEBASE = 2
FILE_ENCRYPTED = 1
MIN_FREE_BYTES = 1_300_000_000

RUNTIME_NAME = "godot411.linux.release.arm64"


def die(msg):
    print("\nERROR: " + msg, file=sys.stderr)
    sys.exit(1)


def info(msg):
    print(msg, flush=True)


# --------------------------------------------------------------------------- pack parsing
def find_pack(f, size):
    """Return the offset where the Godot pack starts (embedded in an exe, or a standalone .pck)."""
    f.seek(0)
    if f.read(4) == MAGIC:
        return 0
    if size < 16:
        die("File too small to contain a Godot pack.")
    f.seek(size - 12)
    tail = f.read(12)
    if tail[8:12] != MAGIC:
        die("No Godot pack found in this file. Point the installer at the game's main file "
            "('Buckshot Roulette.exe', 'Buckshot Roulette.x86_64' or the .pck).")
    pack_size, = struct.unpack("<Q", tail[:8])
    start = size - 12 - pack_size
    if start < 0:
        die("Corrupted pack trailer.")
    return start


def read_pack(path):
    size = os.path.getsize(path)
    f = open(path, "rb")
    start = find_pack(f, size)
    f.seek(start)
    magic, fmt, vmaj, vmin, vpat, flags, file_base = struct.unpack("<4sIIIIIQ", f.read(32))
    if magic != MAGIC:
        die("Bad pack header.")
    if fmt != 2:
        die("Unsupported pack format %d (this patcher supports format 2 / Godot 4.1)." % fmt)
    if (vmaj, vmin) != (4, 1):
        die("The game was built with Godot %d.%d.%d; this patcher ships Godot 4.1.1. "
            "A different engine version needs its own runtime." % (vmaj, vmin, vpat))
    if flags & PACK_DIR_ENCRYPTED:
        die("The pack directory is encrypted; not supported.")
    f.read(16 * 4)  # reserved
    # Offsets are absolute inside the host file, unless the REL_FILEBASE flag is set.
    base = file_base + (start if flags & PACK_REL_FILEBASE else 0)
    count, = struct.unpack("<I", f.read(4))
    if count == 0 or count > 200000:
        die("Implausible file count in pack (%d)." % count)
    entries = []
    for _ in range(count):
        plen, = struct.unpack("<I", f.read(4))
        raw = f.read(plen).rstrip(b"\0")
        ofs, fsize = struct.unpack("<QQ", f.read(16))
        md5 = f.read(16)
        fflags, = struct.unpack("<I", f.read(4))
        if fflags & FILE_ENCRYPTED:
            die("The pack contains encrypted files; not supported.")
        entries.append((raw.decode("utf-8", "replace"), base + ofs, fsize, md5))
    return f, (vmaj, vmin, vpat), entries


def safe_rel(path):
    rel = path[len("res://"):] if path.startswith("res://") else path
    rel = rel.replace("\\", "/").lstrip("/")
    parts = [p for p in rel.split("/") if p not in ("", ".")]
    if not parts or any(p == ".." for p in parts):
        return None
    return os.path.join(*parts)


def extract(f, entries, dest_game):
    total = len(entries)
    last_pct = -1
    for i, (path, off, size, md5) in enumerate(entries, 1):
        rel = safe_rel(path)
        if rel is None:
            die("Unsafe path in pack: %r" % path)
        out = os.path.join(dest_game, rel)
        if os.path.commonpath([os.path.abspath(out), os.path.abspath(dest_game)]) != os.path.abspath(dest_game):
            die("Path escapes the destination: %r" % path)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        h = hashlib.md5()
        f.seek(off)
        left = size
        with open(out, "wb") as g:
            while left > 0:
                chunk = f.read(min(left, 1 << 20))
                if not chunk:
                    die("Unexpected end of file while reading %s." % path)
                h.update(chunk)
                g.write(chunk)
                left -= len(chunk)
        if h.digest() != md5:
            die("Checksum mismatch for %s: the input file is corrupted. Re-verify the game files "
                "in Steam and try again." % path)
        pct = i * 100 // total
        if pct != last_pct and pct % 10 == 0:
            info("  extracted %d%%" % pct)
            last_pct = pct


# --------------------------------------------------------------------------- patches
def read_bytes(p):
    with open(p, "rb") as fh:
        return fh.read()


def patch_global_variables(game):
    p = os.path.join(game, "scripts", "GlobalVariables.gd")
    if not os.path.exists(p):
        die("scripts/GlobalVariables.gd not found: this does not look like the expected game version.")
    data = read_bytes(p)
    old = b"var using_steam = true"
    if data.count(old) != 1:
        die("Patch anchor 'using_steam' not found exactly once: unsupported game version.")
    with open(p, "wb") as fh:
        fh.write(data.replace(old, b"var using_steam = false"))


PIPELINE_FUNC = '''
# --- color tuning for the arm64 port (editable in res://color_tune.cfg) ---
func _apply_color_tune():
	var cfg = ConfigFile.new()
	if cfg.load("res://color_tune.cfg") != OK:
		return
	var rect = overlay.get_node_or_null("BackBufferCopy/ColorRect")
	if rect == null or not (rect.material is ShaderMaterial):
		return
	var m : ShaderMaterial = rect.material
	for k in ["brightness", "contrast", "saturation"]:
		if cfg.has_section_key("overlay", k):
			m.set_shader_parameter(k, float(cfg.get_value("overlay", k)))
	print("color tune: brightness=", m.get_shader_parameter("brightness"),
		" contrast=", m.get_shader_parameter("contrast"),
		" saturation=", m.get_shader_parameter("saturation"))
'''


def patch_pipeline_manager(game):
    p = os.path.join(game, "scripts", "PipelineManager.gd")
    if not os.path.exists(p):
        die("scripts/PipelineManager.gd not found: unsupported game version.")
    data = read_bytes(p)
    nl = b"\r\n" if b"\r\n" in data else b"\n"
    anchor = b"\t\toverlay.visible = true" + nl
    if data.count(anchor) != 1:
        die("Patch anchor in PipelineManager.gd not found exactly once: unsupported game version.")
    data = data.replace(anchor, anchor + b"\t\t_apply_color_tune()" + nl)
    if not data.endswith(nl):
        data += nl
    func = PIPELINE_FUNC.encode("utf-8")
    if nl == b"\r\n":
        func = func.replace(b"\n", b"\r\n")
    with open(p, "wb") as fh:
        fh.write(data + func)


# --------------------------------------------------------------------------- install pieces
def verify_runtime():
    rt = os.path.join(HERE, "godot", RUNTIME_NAME)
    shaf = rt + ".sha256"
    if not os.path.exists(rt):
        die("Runtime binary missing: %s" % rt)
    if os.path.exists(shaf):
        want = open(shaf).read().split()[0].strip().lower()
        h = hashlib.sha256()
        with open(rt, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        if h.hexdigest() != want:
            die("Runtime binary checksum mismatch; re-download the patcher.")
    return rt


def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def make_exec(path):
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def desktop_dir():
    try:
        out = subprocess.run(["xdg-user-dir", "DESKTOP"], capture_output=True, text=True, timeout=5)
        d = out.stdout.strip()
        if d and os.path.isdir(os.path.dirname(d)):
            return d
    except Exception:
        pass
    return os.path.expanduser("~/Desktop")


def main():
    ap = argparse.ArgumentParser(description="Buckshot Roulette - Nintendo Switch (Ubuntu/Kubuntu) port installer (unofficial).")
    ap.add_argument("game_file", help="Your game's main file: .exe, .x86_64 or .pck (from your own Steam copy)")
    ap.add_argument("--dest", default=os.path.expanduser("~/buckshot-roulette-switch"),
                    help="Install directory (default: ~/buckshot-roulette-switch)")
    ap.add_argument("--no-shortcut", action="store_true", help="Do not create a desktop shortcut")
    ap.add_argument("--force", action="store_true", help="Replace an existing install in --dest")
    a = ap.parse_args()

    if platform.machine().lower() not in ("aarch64", "arm64"):
        info("WARNING: this machine is %s, not arm64. The bundled runtime will not run here." % platform.machine())

    src = os.path.abspath(a.game_file)
    if not os.path.isfile(src):
        die("File not found: %s" % src)
    dest = os.path.abspath(os.path.expanduser(a.dest))
    game = os.path.join(dest, "game")
    if os.path.exists(game):
        if not a.force:
            die("%s already exists. Use --force to replace it." % game)
        shutil.rmtree(game)
    os.makedirs(dest, exist_ok=True)
    free = shutil.disk_usage(dest).free
    if free < MIN_FREE_BYTES:
        die("Not enough free space in %s (need ~1.3 GB, have %.1f GB)." % (dest, free / 1e9))

    info("[1/5] Verifying the bundled runtime...")
    rt_src = verify_runtime()

    info("[2/5] Reading the game's data pack...")
    f, ver, entries = read_pack(src)
    info("  Godot %d.%d.%d pack, %d files" % (ver + (len(entries),)))

    info("[3/5] Extracting (with checksum verification)...")
    os.makedirs(game)
    try:
        extract(f, entries, game)
    finally:
        f.close()

    info("[4/5] Applying patches...")
    patch_global_variables(game)
    patch_pipeline_manager(game)
    os.makedirs(os.path.join(game, "stub"), exist_ok=True)
    shutil.copy2(os.path.join(HERE, "stub", "steam_stub.gd"), os.path.join(game, "stub", "steam_stub.gd"))
    write_text(os.path.join(game, "override.cfg"),
               '[autoload]\n\nSteam="*res://stub/steam_stub.gd"\n\n'
               '[rendering]\n\nrenderer/rendering_method="gl_compatibility"\n'
               'renderer/rendering_method.mobile="gl_compatibility"\n')
    cfg = os.path.join(game, "color_tune.cfg")
    shutil.copy2(os.path.join(HERE, "color_tune.cfg"), cfg)

    info("[5/5] Installing runtime and launcher...")
    rt = os.path.join(dest, RUNTIME_NAME)
    shutil.copy2(rt_src, rt)
    make_exec(rt)
    run = os.path.join(dest, "run.sh")
    write_text(run,
               '#!/bin/bash\ncd "%s"\n'
               'exec ./%s --path game --rendering-driver opengl3 --fullscreen "$@" > "%s" 2>&1\n'
               % (dest, RUNTIME_NAME, os.path.join(dest, "last-run.log")))
    make_exec(run)

    shortcut = None
    if not a.no_shortcut:
        d = desktop_dir()
        os.makedirs(d, exist_ok=True)
        icon = os.path.join(game, "icon.png")
        if not os.path.exists(icon):
            icon = "applications-games"
        shortcut = os.path.join(d, "BuckshotRoulette.desktop")
        write_text(shortcut,
                   "[Desktop Entry]\nType=Application\nName=Buckshot Roulette\n"
                   "Comment=Buckshot Roulette (unofficial arm64 port, personal use)\n"
                   "Exec=%s\nPath=%s\nIcon=%s\nTerminal=false\nCategories=Game;\n" % (run, dest, icon))
        make_exec(shortcut)
        try:
            subprocess.run(["gio", "set", shortcut, "metadata::trusted", "true"],
                           capture_output=True, timeout=5)
        except Exception:
            pass

    info("\nDone.")
    info("  Install dir : %s" % dest)
    info("  Launch      : %s%s" % (run, ("   or the desktop shortcut " + shortcut) if shortcut else ""))
    info("  Color tuning: edit %s and relaunch" % cfg)
    info("  Log         : %s" % os.path.join(dest, "last-run.log"))
    info("Note: multiplayer, leaderboards and achievements are disabled (no Steamworks on arm64).")


if __name__ == "__main__":
    main()
