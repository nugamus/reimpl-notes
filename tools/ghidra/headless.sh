#!/usr/bin/env bash
# Starts the GhidraMCP headless server for the Monet project, if it is not
# already running. Safe to call repeatedly: an already-listening port is a
# success, not an error, which is what makes it usable from a SessionStart hook.
#
# The MCP bridge (`claude mcp list`, local scope for this repo) discovers this
# server by scanning 127.0.0.1:8089..8104, so nothing here needs to tell it where
# the server is.
#
# No program is opened at boot. The bridge runs with
# GHIDRA_MCP_REQUIRE_PROGRAM_SELECTORS=1, so every tool call names its program
# anyway, and the project holds 13 of them.
#
# Build the JAR first (once, and after any Java change):
#   cd tools/ghidra/mcp && mvn clean package -P headless -DskipTests
set -euo pipefail

PORT="${GHIDRA_MCP_PORT:-8089}"
GHIDRA_HOME="${GHIDRA_HOME:-C:/ghidra}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
JAR="$REPO/tools/ghidra/mcp/target/GhidraMCP-7.0.0.jar"
PROJECT="$REPO/ghidra_projects/Monet.gpr"
LOG_DIR="$REPO/logs"
LOG="$LOG_DIR/ghidra-headless.log"

# Already up? Nothing to do. curl is the check rather than a pid file because the
# question is "can the bridge reach a server", not "did this script start one" —
# a server started by hand last week must count.
if curl -fsS --max-time 2 "http://127.0.0.1:$PORT/check_connection" >/dev/null 2>&1; then
  echo "ghidra-headless: already serving on $PORT"
  exit 0
fi

if [ ! -f "$JAR" ]; then
  echo "ghidra-headless: $JAR missing — run: cd tools/ghidra/mcp && mvn clean package -P headless -DskipTests" >&2
  exit 1
fi

# Windows java.exe wants Windows-shaped paths and ';' between classpath entries,
# even when invoked from Git Bash. The list is far past the command-line length
# limit, so it goes in an @argfile instead of on the command line.
winpath() { printf '%s' "$1" | sed -E 's|^/([a-zA-Z])/|\1:/|'; }

mkdir -p "$LOG_DIR"
CP_FILE="$LOG_DIR/.ghidra-headless-classpath.txt"
{
  printf -- '-classpath "'
  printf '%s;' "$(winpath "$JAR")"
  for jar in "$GHIDRA_HOME"/Ghidra/Framework/*/lib/*.jar \
             "$GHIDRA_HOME"/Ghidra/Features/*/lib/*.jar \
             "$GHIDRA_HOME"/Ghidra/Processors/*/lib/*.jar; do
    [ -f "$jar" ] && printf '%s;' "$(winpath "$jar")"
  done
  printf '"\n'
} > "$CP_FILE"

echo "ghidra-headless: starting on 127.0.0.1:$PORT (log: $LOG)"
nohup java \
  -Xmx4g -XX:+UseG1GC \
  "-Dghidra.home=$(winpath "$GHIDRA_HOME")" \
  -Dapplication.name=GhidraMCP \
  "@$(winpath "$CP_FILE")" \
  com.xebyte.headless.GhidraMCPHeadlessServer \
  --bind 127.0.0.1 --port "$PORT" \
  --project "$(winpath "$PROJECT")" \
  >> "$LOG" 2>&1 &

# Wait for it rather than returning immediately: a hook that "succeeded" while
# the server was still 40 seconds from listening is indistinguishable from one
# that failed, and the bridge would report no instances either way.
for _ in $(seq 1 60); do
  if curl -fsS --max-time 2 "http://127.0.0.1:$PORT/check_connection" >/dev/null 2>&1; then
    echo "ghidra-headless: ready on $PORT"
    exit 0
  fi
  sleep 2
done

echo "ghidra-headless: did not come up within 120s — see $LOG" >&2
exit 1
