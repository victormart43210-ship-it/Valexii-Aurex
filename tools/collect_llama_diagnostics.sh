#!/usr/bin/env bash
# Run on the Chromebook, not Work. No model data or credential environment dumped.
set -eu
if [ "$#" -ne 2 ]; then
  echo "Usage: bash tools/collect_llama_diagnostics.sh /path/to/llama-cli /path/to/llama-source" >&2
  exit 2
fi
binary=$(realpath "$1")
source_dir=$(realpath "$2")
output="llama-diagnostics-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir "$output"
uname -a > "$output/kernel.txt"
lscpu > "$output/cpu.txt"
file "$binary" > "$output/binary.txt"
sha256sum "$binary" > "$output/binary.sha256"
git -C "$source_dir" rev-parse HEAD > "$output/source-sha.txt"
# Cache options and linked library paths identify stale/unsupported build artifacts.
find "$source_dir" -maxdepth 3 -name CMakeCache.txt -exec grep -E 'GGML_|CMAKE_(C|CXX)_FLAGS|CMAKE_BUILD_TYPE' {} \; > "$output/build-options.txt"
ldd "$binary" > "$output/linked-libraries.txt" 2>&1 || true
# --version avoids loading private GGUF data. If that does not fault, record that fact.
if command -v gdb >/dev/null; then
  timeout 30 gdb --batch -ex 'set pagination off' -ex run -ex 'x/12i $pc-16' -ex 'info registers' -ex bt --args "$binary" --version > "$output/gdb-version.txt" 2>&1 || true
fi
printf 'Collected %s\n' "$output"
