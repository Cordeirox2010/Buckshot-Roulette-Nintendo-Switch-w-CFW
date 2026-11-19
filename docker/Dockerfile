# Cross-compiles Godot 4.1.1 (template_release) for linux arm64 (aarch64).
# Usage (from the package folder):
#   docker build -t godot411-arm64 -f docker/Dockerfile docker
#   docker run --rm -v "$PWD/godot:/out" godot411-arm64
# The result is /out/godot411.linux.release.arm64
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential pkg-config python3 python3-pip curl ca-certificates \
        gcc-aarch64-linux-gnu g++-aarch64-linux-gnu \
    && pip3 install --no-cache-dir scons==4.5.2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
RUN curl -fsSL https://github.com/godotengine/godot/archive/refs/tags/4.1.1-stable.tar.gz \
    | tar -xz --strip-components=1

# lto=none avoids running out of memory at link time. X11/ALSA/etc. are not linked: Godot 4.1
# uses "sowrap" (dlopen at runtime), so no arm64 sysroot is needed.
CMD ["bash", "-c", "scons -j$(nproc) platform=linuxbsd arch=arm64 target=template_release \
      CC=aarch64-linux-gnu-gcc CXX=aarch64-linux-gnu-g++ \
      lto=none optimize=speed module_mono_enabled=no \
    && aarch64-linux-gnu-strip bin/godot.linuxbsd.template_release.arm64 \
    && cp -v bin/godot.linuxbsd.template_release.arm64 /out/godot411.linux.release.arm64"]
