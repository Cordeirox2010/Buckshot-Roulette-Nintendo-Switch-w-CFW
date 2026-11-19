# Buckshot Roulette: Nintendo Switch (Ubuntu/Kubuntu) Port (unofficial)

An installer that lets you run **your own, legally purchased copy** of *Buckshot Roulette* natively on a
Nintendo Switch running Ubuntu/Kubuntu (aarch64, via custom firmware), and on other 64-bit ARM Linux
devices. Developed and tested on a Switch Lite running Kubuntu 24.04.

> **This package contains no game files.** No `.pck`, no assets, no scripts, no music, no `.exe`.
> You need to own the game on Steam. The installer reads *your* copy and builds a patched, local copy
> on your device. Please do not share the result. This project is not affiliated with or endorsed by
> the game's developer or publisher. *Buckshot Roulette* is the property of its respective owners.

## Quick start

On the Switch, in Linux, inside a terminal, with the game file and this package already copied over:

```bash
tar xzf buckshot-roulette-switch-kubuntu-port.tar.gz
cd buckshot-roulette-switch-kubuntu-port
bash install.sh "/path/to/Buckshot Roulette.exe"
```

Then open **Buckshot Roulette** from the desktop shortcut. The full walkthrough is below.

## Step-by-step: installing on your Nintendo Switch

### 0. What you need

- A Nintendo Switch already set up to boot Linux through custom firmware, with **Ubuntu or Kubuntu for
  Switch (L4T, from the Switchroot project)** installed. This guide does **not** cover hacking a console or
  installing Linux. Follow the [Switchroot wiki](https://wiki.switchroot.org/) for supported models and
  steps. Modifying a console can void its warranty and risk online bans; that is your decision and your risk.
- A copy of *Buckshot Roulette* on Steam (on a PC, any OS).
- A way to move files to the Switch: an SD card reader, a USB drive, or the same Wi-Fi network.
- About 3 GB of free space on the Linux partition (about 1.3 GB for the install, plus the temporary game file).

### 1. Boot into Linux and open a terminal

1. Boot your Switch into Linux with your usual Switchroot boot method and log in.
2. Connect to Wi-Fi (network icon in the panel).
3. Open **Konsole** (the terminal) from the application menu.
4. Check that the system meets the requirements:

```bash
uname -m              # must print: aarch64
ldd --version | head -1   # glibc must be 2.35 or newer (Ubuntu 22.04+)
python3 --version     # must be installed (it is by default on Ubuntu)
```

### 2. Get your game file from Steam (on a PC)

Install *Buckshot Roulette* through Steam, then locate **one** of these files:

- Windows build: `steamapps/common/Buckshot Roulette/Buckshot Roulette_windows/Buckshot Roulette.exe`
- Linux build: `steamapps/common/Buckshot Roulette/Buckshot Roulette_linux/Buckshot Roulette.x86_64`

(Steam: right-click the game, Manage, Browse local files.) Only that single file is needed, about 750 MB.
The data pack is embedded in it.

### 3. Download this package

Download `buckshot-roulette-switch-kubuntu-port.tar.gz` from the repository's **Releases** page. The
archive already contains the arm64 runtime.

### 4. Move both files to the Switch

Pick whichever is easiest:

**A. SD card or USB drive.** Copy the game file and the `.tar.gz` onto the drive from your PC, plug it
into the Switch while Linux is running, and open it in **Dolphin** (the file manager, under "Devices").
Copy both files to your home folder (`/home/<your user>`).

**B. Over your Wi-Fi network (SSH).** On the Switch, enable SSH once and find its IP:

```bash
sudo apt update && sudo apt install -y openssh-server
hostname -I     # note the IP address
whoami          # note your username
```

Then, on your PC (Windows PowerShell, macOS or Linux terminal), from the folder holding the files:

```bash
scp "Buckshot Roulette.exe" buckshot-roulette-switch-kubuntu-port.tar.gz USER@SWITCH_IP:~/
```

Replace `USER` and `SWITCH_IP` with the values above. You will be asked for your Linux password.

If you only used SSH for this, you can turn it off afterwards: `sudo systemctl disable --now ssh`.

### 5. Install

In the Switch's terminal, from your home folder:

```bash
cd ~
tar xzf buckshot-roulette-switch-kubuntu-port.tar.gz
cd buckshot-roulette-switch-kubuntu-port
bash install.sh ~/"Buckshot Roulette.exe"
```

Use the real file name and path you copied (for the Linux build: `~/"Buckshot Roulette.x86_64"`).
The installer verifies every file, applies the patches and creates the launcher. It takes a few minutes.
When it prints `Done.`, you are finished.

### 6. Play

Open **Buckshot Roulette** from the desktop shortcut, or run it from a terminal:

```bash
~/buckshot-roulette-switch/run.sh
```

The first launch can take a little longer than the next ones.

### 7. Clean up (optional)

The installed game does not need the original file anymore. To free space:

```bash
rm ~/"Buckshot Roulette.exe" ~/buckshot-roulette-switch-kubuntu-port.tar.gz
```

### Updating, reinstalling and uninstalling

- **Reinstall or update the port:** run `bash install.sh <game file> --force`.
- **Uninstall:** `rm -rf ~/buckshot-roulette-switch ~/Desktop/BuckshotRoulette.desktop`.
  Your saves and settings stay in `~/.local/share/godot/app_userdata/Buckshot Roulette`; delete that
  folder too if you want a fully clean removal.

### Troubleshooting

| Problem | What to do |
|---|---|
| `No Godot pack found in this file` | You pointed the installer at the wrong file. Use the main game file listed in step 2. |
| `built with Godot X.Y.Z` / `unsupported game version` | Your game version differs from the supported one (v2.2.0.6, Godot 4.1.x). The installer refuses instead of guessing. |
| `Checksum mismatch` | The copied file is corrupted. In Steam, verify the game files, copy it again and retry. |
| `already exists. Use --force` | There is a previous install. Add `--force` to replace it. |
| `Not enough free space` | Free about 1.3 GB on the partition holding your home folder. |
| Game does not open or the screen stays black | Read `~/buckshot-roulette-switch/last-run.log` and check `uname -m` and `ldd --version` (step 1). |
| Colors look too light or too dark | Edit `~/buckshot-roulette-switch/game/color_tune.cfg` and relaunch (see below). |

## What the installer does

1. Finds the Godot data pack inside your game file (`.exe`, `.x86_64` or `.pck`).
2. Extracts it, **verifying every file's MD5** against the pack's own table.
3. Applies two tiny source patches: turns on the game's built-in non-Steam mode, and lets you tune the
   game's OpenGL post-processing colors from a text file.
4. Installs a **Steam stub** (our own code, `stub/steam_stub.gd`) so the game's scripts parse without
   the GodotSteam plugin, which does not exist for arm64 Linux.
5. Installs a **Godot 4.1.1 `template_release` arm64 runtime** and forces the OpenGL *Compatibility* renderer.
6. Creates `run.sh` and a desktop shortcut.

Options: `--dest DIR` (default `~/buckshot-roulette-switch`), `--no-shortcut`, `--force`.

## Requirements

- 64-bit ARM Linux (aarch64) with **glibc 2.35 or newer** (Ubuntu 22.04+) and an OpenGL 3.3+ driver.
  Tested: Switch Lite, Kubuntu 24.04.5, glibc 2.39, NVIDIA Tegra X1 (L4T 32.7.4), OpenGL 3.3.
- `python3` and about 1.3 GB of free space.
- The game at version **v2.2.0.6** (Godot 4.1.x).

## Color tuning

The game's OpenGL mode applies its own brightness/contrast/saturation overlay. Edit
`<install dir>/game/color_tune.cfg` and relaunch. Defaults: `brightness=0.10`, `contrast=1.24`,
`saturation=0.23` (the game's originals are 0.15 / 1.176 / 0.23). Lower `brightness` darkens the blacks;
higher `contrast` adds contrast.

## Limitations

- **Multiplayer, leaderboards and achievements are disabled** (they need Steamworks, which is not
  available on arm64).
- Settings and progress live in Godot's user data: `~/.local/share/godot/app_userdata/Buckshot Roulette`.
- Performance and visuals depend on your GPU driver. Logs: `<install dir>/last-run.log`.

## If you cloned the repository

The runtime binary is not stored in git (it is 77 MB). Either download the release archive, which
includes it, or put the binary at `godot/godot411.linux.release.arm64`.

### Rebuilding the runtime yourself

`docker/Dockerfile` cross-compiles Godot 4.1.1 for arm64 from the official source tarball:

```bash
docker build -t godot411-arm64 -f docker/Dockerfile docker
docker run --rm -v "$PWD/godot:/out" godot411-arm64
```

The released binary was built this way; its SHA-256 is in `godot/godot411.linux.release.arm64.sha256`.
A rebuild may not be bit-identical, so update that checksum file if you replace the binary.

## Licenses

- Installer and stub: MIT (see `LICENSE`).
- The bundled Godot runtime: MIT, Copyright (c) 2014-present Godot Engine contributors and (c) 2007-2014
  Juan Linietsky, Ariel Manzur (see `licenses/LICENSE.txt`, and `licenses/COPYRIGHT.txt` for third-party
  components).
- *Buckshot Roulette* and all of its content are not covered by these licenses and are not included.

This is not legal advice. Check the game's and Steam's terms for your situation before sharing anything.
