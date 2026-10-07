#!/usr/bin/env bash
# tools/ghidra/headless.sh <Project>: starts the GhidraMCP headless server for one Ghidra
# project (ghidra_projects/<Project>.gpr: Monet, Peintre, Ring, Gilbert, Grumpa), if it is not
# already running. Each project has its own port, so several can serve at once and the
# bridge sees them all. Safe to call repeatedly: an already-listening port is a success.
#
# The Ghidra MCP bridge discovers this
# server by scanning 127.0.0.1:8089..8104, so nothing here needs to tell it where
# the server is.
#
# No program is opened at boot. The bridge runs with
# GHIDRA_MCP_REQUIRE_PROGRAM_SELECTORS=1, so every tool call names its program
# anyway.
#
# Build the JAR first (once, and after any Java change):
#   cd tools/ghidra/mcp && mvn clean package -P headless -DskipTests
set -euo pipefail

NAME="${1:-${GHIDRA_PROJECT:-}}"
[ -n "$NAME" ] || { echo "usage: headless.sh <Monet|Peintre|Ring|Gilbert|Grumpa|...>"; exit 0; }
case "$NAME" in # one fixed port per project: the port says which project answers
  Monet) PORT=8089 ;; Peintre) PORT=8090 ;; Ring) PORT=8091 ;; Gilbert) PORT=8092 ;; Grumpa) PORT=8093 ;; CryOmni3D) PORT=8094 ;;
  *) PORT="${GHIDRA_MCP_PORT:-8095}" ;;
esac
GHIDRA_HOME="${GHIDRA_HOME:-C:/ghidra}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
JAR="$REPO/tools/ghidra/mcp/target/GhidraMCP-7.0.0.jar"
PROJECT="$REPO/ghidra_projects/$NAME.gpr"
[ -f "$PROJECT" ] || { echo "ghidra-headless: no $PROJECT" >&2; exit 1; }
LOG_DIR="$REPO/logs"
LOG="$LOG_DIR/ghidra-headless-$NAME.log"

# Already up? Nothing to do. curl is the check rather than a pid file because the
# question is "can the bridge reach a server", not "did this script start one" —
# a server started by hand last week must count.
if curl -fsS --max-time 2 "http://127.0.0.1:$PORT/check_connection" >/dev/null 2>&1; then
  echo "ghidra-headless: $NAME already serving on $PORT"
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
CP_FILE="$LOG_DIR/.ghidra-headless-classpath-$NAME.txt"
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

echo "ghidra-headless: starting $NAME on 127.0.0.1:$PORT (log: $LOG)"
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
    echo "ghidra-headless: $NAME ready on $PORT"
    exit 0
  fi
  sleep 2
done

echo "ghidra-headless: did not come up within 120s — see $LOG" >&2
exit 1
