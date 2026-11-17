#!/usr/bin/env bash
# dup-signature.sh — 중복 함수명/시그니처를 코드에서 재도출 (⟦CI:dup-signature⟧).
# 같은 함수명이 **모듈 최상위**에 2곳 이상 정의되면 차단(휴리스틱). .dup-allow(한 줄당 함수명) 예외.
#
# 보는 범위를 좁게 둔 이유(실측 2026-11-17, 설치본 4곳):
#   - 생성물·외부 코드(build/ install/ log/ node_modules/ .venv/ site-packages/ __pycache__/ .pio/)를
#     세면 rosidl 생성 함수(`*_fini_function`·`__max_serialized_size`)가 목록을 통째로 먹는다.
#   - `.claude/` 는 하네스 상태다 — 그 안에 세션 작업 트리를 두는 프로젝트가 있어
#     같은 저장소 사본이 여러 벌 잡혔다(실측 Ford-CATL-setup: 중복 파일 633개가
#     `.claude/worktrees` 아래, 전체 4844개 이름).
#   - 설치된 가이드라인 번들(claude_guideline/)은 그 프로젝트의 코드가 아니다 — 번들 훅들이
#     `main`·`rule_active`·`added_texts` 를 공유해, **번들을 설치한 모든 프로젝트에서 이 검사가
#     영구히 빨갰다**(차단 이빨이 프로젝트 코드와 무관한 이유로 늘 빨가면 아무도 보지 않는다).
#   - 들여쓴 `def` 는 메서드다 — `__init__`·`__enter__`·`closeEvent` 는 설계상 반복된다.
#     최상위 `def` 만 센다(C/C++ 는 원래 열 0 만 봤다).
#   실측: Divine 40→4 · TM_Robot_UI 158→16 · Cobot-Humanoid 764→66 · HY7-Humanoids 2783→117.
#   남는 것은 패키지 사이에 실제로 복제된 최상위 함수다 — 큰 기존 작업공간에서는 여전히 수십 건이라
#   **그대로 차단 이빨로 쓰면 커밋이 서므로** 프로젝트가 `.dup-allow` 기준선을 깔거나 범위를 staged
#   파일로 좁혀야 한다. 그 결정은 프로젝트 몫이고, 본 검사는 숫자를 정직하게 낸다.
# 설계상 반복되는 이름은 기본 허용: main(스크립트 진입점) ·
#   generate_launch_description / generate_test_description(ROS2 launch 규약).
set -uo pipefail

TARGET="${1:-.}"
ALLOW="$TARGET/.dup-allow"
EXDIR=(--exclude-dir=.git --exclude-dir=build --exclude-dir=install --exclude-dir=log
       --exclude-dir=node_modules --exclude-dir=__pycache__ --exclude-dir=.venv
       --exclude-dir=venv --exclude-dir=site-packages --exclude-dir=.pio
       --exclude-dir=.claude --exclude-dir=claude_guideline)
names=$(mktemp); allow=$(mktemp)
trap 'rm -f "$names" "$allow"' EXIT

printf 'main\ngenerate_launch_description\ngenerate_test_description\n' > "$allow"
# 줄 주석·뒤따르는 주석·여백을 걷는다 — 함수명에 `#` 는 못 들어가므로 안전하다
[ -f "$ALLOW" ] && sed -E 's/#.*//; s/[[:space:]]+//g' "$ALLOW" | grep -vE '^$' >> "$allow"

# Python: 모듈 최상위 def name(  — 들여쓴 것은 메서드이므로 보지 않는다
grep -rhE '^def[[:space:]]+[A-Za-z_][A-Za-z0-9_]*[[:space:]]*\(' --include=*.py "${EXDIR[@]}" "$TARGET" 2>/dev/null \
  | sed -E 's/^def[[:space:]]+([A-Za-z_][A-Za-z0-9_]*).*/\1/' >> "$names"

# C/C++: <type> name(args) (정의 줄, 열 0), 제어문 제외
grep -rhE '^[A-Za-z_][A-Za-z0-9_<>:\*&[:space:]]+[[:space:]][A-Za-z_][A-Za-z0-9_]*[[:space:]]*\([^;]*\)[[:space:]]*\{?[[:space:]]*$' \
  --include=*.c --include=*.cc --include=*.cpp "${EXDIR[@]}" "$TARGET" 2>/dev/null \
  | grep -vE '^[[:space:]]*(return|if|while|for|switch|else|do)\b' \
  | sed -E 's/.*[[:space:]]([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*\(.*/\1/' >> "$names"

dups=$(LC_ALL=C sort "$names" | uniq -d | grep -vxF -f "$allow" 2>/dev/null || true)
dups=$(printf '%s\n' "$dups" | grep -v '^[[:space:]]*$' || true)

if [ -n "$dups" ]; then
  n=$(printf '%s\n' "$dups" | grep -c .)
  echo "✗ [dup] 중복 함수명(최상위 정의 $n 개 이름):"
  printf '%s\n' "$dups" | head -20 | sed 's/^/   - /'
  [ "$n" -gt 20 ] && echo "   … 외 $((n - 20)) 개"
  echo "  (정당한 오버로드/재정의면 .dup-allow 에 함수명 추가. 생성물·외부 코드·설치된 번들은 세지 않는다)"
  exit 1
fi
echo "✓ 중복 함수 시그니처 없음"
exit 0
