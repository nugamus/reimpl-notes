#!/bin/bash
# tools/lint.sh <engine>: the checks a ScummVM reviewer makes, run on C:\scummvm-dev\<engine>.
# Prints findings only, then a summary line; exit 1 when a hard rule is broken.
#   hard: GPL header on every file, no STL / exceptions / C++14+, commit subjects
#         "<ENGINE>: ..." with an Assisted-by trailer, no DEV-only code outside the DEV commit
#   soft: cppcheck (warning, portability, performance) and clang-format against ScummVM's
#         .clang-format, counted per file (ScummVM does not require clang-format, but
#         reviewers ask for its style: tabs, braces on the same line, `Type *name`)
set -o pipefail
ENGINE=${1:?usage: lint.sh <engine>}
if [ "$MSYSTEM" != UCRT64 ]; then
	exec /c/msys64/usr/bin/env MSYSTEM=UCRT64 CHERE_INVOKING=1 /c/msys64/usr/bin/bash -lc \
		"bash '$(cygpath -u "$0")' $ENGINE"
fi
git() { "/c/Program Files/Git/cmd/git.exe" "$@"; }
cd /c/scummvm-dev/"$ENGINE" || exit 1
DIR=engines/$ENGINE
hard=0
fail() { echo "HARD $*"; hard=$((hard + 1)); }
files=$(git ls-files "$DIR" | grep -E '\.(cpp|h)$')

# GPL header (ScummVM's exact opening line).
for f in $files; do
	head -3 "$f" | grep -q 'ScummVM - Graphic Adventure Engine' || fail "$f: missing the ScummVM GPL header"
done

# Language and library rules: ScummVM builds without the STL, exceptions or RTTI and holds
# engines to C++11 (CI also builds with g++ 4.8).
grep -nE '#include <(vector|string|map|set|list|memory|iostream|sstream|fstream|algorithm|functional|unordered_map|thread|mutex|regex|cstdio|cstdlib|cstring)>' $files |
	while read -r l; do echo "HARD $l: standard library header (use common/)"; done | tee /tmp/lint-hard
grep -nE '\bstd::|\bthrow\b|\btry *\{|\bcatch *\(|dynamic_cast<|typeid\(' $files |
	grep -vE '^[^:]*:[0-9]+:\s*//' | grep -vE 'std::(initializer_list|nullptr_t)\b' | while read -r l; do echo "HARD $l: STL, exceptions or RTTI"; done | tee -a /tmp/lint-hard
grep -nE "\b0[bB][01]+\b|[0-9]'[0-9]{3}|\[\]\(auto|decltype\(auto\)|std::make_unique" $files |
	while read -r l; do echo "HARD $l: C++14 or later"; done | tee -a /tmp/lint-hard
grep -nE '\b(printf|fprintf|puts)\(' $files | while read -r l; do echo "soft $l: use debug()/warning()"; done
hard=$((hard + $(wc -l < /tmp/lint-hard)))

# Commits on the dev branch that would be published (everything but the DEV commit).
while read -r sha subject; do
	case "$subject" in DEV:*) continue ;; esac
	echo "$subject" | grep -qE '^[A-Z0-9_]+: ' || fail "$sha \"$subject\": subject must start with ENGINE: "
	git log -1 --format=%B "$sha" | grep -q '^Assisted-by: ' || fail "$sha \"$subject\": no Assisted-by trailer"
	git log -1 --format=%B "$sha" | grep -qi '^Co-Authored-By: .*claude' && fail "$sha: AI listed as co-author"
done < <(git log --format='%h %s' "origin/master..HEAD")

# Harness code must stay in the DEV commit: the clean branch may not mention it.
if git rev-parse -q --verify "$ENGINE" > /dev/null; then
	git grep -nE '"dev_[a-z_]+"|\bdev[A-Z][A-Za-z]*\(' "$ENGINE" -- "$DIR" | head -5 |
		while read -r l; do echo "HARD clean branch $l: harness code outside the DEV commit"; done | tee /tmp/lint-dev
	hard=$((hard + $(wc -l < /tmp/lint-dev)))
fi

# cppcheck: real defects only (ScummVM's macros make style checks noisy), in this engine's
# files; config.h and a platform define get it past scummsys.h.
cppcheck -j"$(nproc)" --quiet --std=c++11 --language=c++ --enable=warning,portability,performance \
	--inline-suppr --suppress=missingIncludeSystem --suppress=missingInclude --suppress=unknownMacro \
	--include=config.h -DWIN32 -D__MINGW32__ -Dscumm_va_copy=va_copy \
	--template='{file}:{line}: {severity}: {message} [{id}]' -I . -I engines "$DIR" 2>&1 |
	sed 's#\\#/#g' | grep "^$DIR/" | sort -u | sed 's/^/soft /' | head -60

# clang-format: lines that would change, per file.
fmt=0
for f in $files; do
	n=$(clang-format --style=file "$f" | diff "$f" - | grep -c '^>')
	[ "$n" -gt 0 ] && { fmt=$((fmt + 1)); [ "$n" -gt 20 ] && echo "soft $f: $n lines differ from .clang-format"; }
done

echo "$ENGINE lint: $hard hard, $fmt of $(echo $files | wc -w) files off clang-format"
[ "$hard" -eq 0 ]
