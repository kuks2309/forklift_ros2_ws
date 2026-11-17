#!/usr/bin/env bash
# dup-signature.sh 회귀 시험 — **무엇을 세고 무엇을 안 세는가**를 고정한다.
# 이 검사는 한때 설치된 번들·생성물까지 세어 모든 프로젝트에서 영구히 빨갰다(실측
# HY7-Humanoids 2783개 이름). 그 범위가 다시 넓어지면 아래가 깨진다.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHK="$(dirname "$HERE")/dup-signature.sh"
PASS=0; FAIL=0
ok(){ echo "  PASS $1"; PASS=$((PASS+1)); }
no(){ echo "  FAIL $1: ${2:-}"; FAIL=$((FAIL+1)); }

ROOT="$(mktemp -d)"
trap 'rm -rf "$ROOT"' EXIT

# tree <이름> — 빈 작업 트리를 만들고 경로를 돌려준다
tree(){ local d="$ROOT/$1"; mkdir -p "$d"; printf '%s' "$d"; }
# run <트리> — 검사를 돌려 exit code 를 돌려준다
run(){ bash "$CHK" "$1" >"$ROOT/out" 2>&1; echo $?; }
out(){ cat "$ROOT/out"; }

echo "== 세는 것 =="
d=$(tree t1); mkdir -p "$d/a" "$d/b"
printf 'def helper(x):\n    return x\n' > "$d/a/x.py"
printf 'def helper(y):\n    return y\n' > "$d/b/y.py"
r=$(run "$d")
{ [ "$r" = 1 ] && out | grep -q 'helper'; } && ok 최상위_중복_차단 || no 최상위_중복_차단 "exit=$r $(out | head -2)"

d=$(tree t2); mkdir -p "$d/a" "$d/b"
printf 'int compute(int a)\n{\n    return a;\n}\n' > "$d/a/x.cpp"
printf 'int compute(int b)\n{\n    return b;\n}\n' > "$d/b/y.cpp"
r=$(run "$d")
{ [ "$r" = 1 ] && out | grep -q 'compute'; } && ok C_최상위_중복_차단 || no C_최상위_중복_차단 "exit=$r"

echo "== 세지 않는 것 =="
d=$(tree t3); mkdir -p "$d/a" "$d/b"
printf 'class A:\n    def __init__(self):\n        pass\n' > "$d/a/x.py"
printf 'class B:\n    def __init__(self):\n        pass\n' > "$d/b/y.py"
r=$(run "$d"); [ "$r" = 0 ] && ok 들여쓴_메서드_통과 || no 들여쓴_메서드_통과 "exit=$r $(out|head -3)"

d=$(tree t4); mkdir -p "$d/build/g1" "$d/build/g2"
printf 'def gen_fini(x):\n    pass\n' > "$d/build/g1/x.py"
printf 'def gen_fini(y):\n    pass\n' > "$d/build/g2/y.py"
r=$(run "$d"); [ "$r" = 0 ] && ok 생성물_build_통과 || no 생성물_build_통과 "exit=$r $(out|head -3)"

d=$(tree t4b); mkdir -p "$d/a" "$d/.claude/worktrees/w1/a"
printf 'def only_here(x):\n    pass\n' > "$d/a/x.py"
printf 'def only_here(x):\n    pass\n' > "$d/.claude/worktrees/w1/a/x.py"
r=$(run "$d"); [ "$r" = 0 ] && ok 세션트리_사본_통과 || no 세션트리_사본_통과 "exit=$r $(out|head -3)"

d=$(tree t5); mkdir -p "$d/docs/claude_guideline/coding/hooks" "$d/docs/claude_guideline/git_workflow/hooks"
printf 'def rule_active(cwd):\n    pass\n' > "$d/docs/claude_guideline/coding/hooks/a.py"
printf 'def rule_active(cwd):\n    pass\n' > "$d/docs/claude_guideline/git_workflow/hooks/b.py"
r=$(run "$d"); [ "$r" = 0 ] && ok 설치된_번들_통과 || no 설치된_번들_통과 "exit=$r $(out|head -3)"

d=$(tree t6); mkdir -p "$d/a" "$d/b"
printf 'def main():\n    pass\n' > "$d/a/x.py"
printf 'def main():\n    pass\n' > "$d/b/y.py"
printf 'def generate_launch_description():\n    pass\n' > "$d/a/l1.py"
printf 'def generate_launch_description():\n    pass\n' > "$d/b/l2.py"
r=$(run "$d"); [ "$r" = 0 ] && ok 기본허용_main_launch_통과 || no 기본허용_main_launch_통과 "exit=$r $(out|head -3)"

d=$(tree t7); mkdir -p "$d/a" "$d/b"
printf 'def helper(x):\n    pass\n' > "$d/a/x.py"
printf 'def helper(y):\n    pass\n' > "$d/b/y.py"
printf '# 정당한 재정의\nhelper   # 양쪽 패키지가 각자 가진다\n' > "$d/.dup-allow"
r=$(run "$d"); [ "$r" = 0 ] && ok dup_allow_주석허용_통과 || no dup_allow_주석허용_통과 "exit=$r $(out|head -3)"

d=$(tree t8); mkdir -p "$d/a"
printf 'def only_once(x):\n    pass\n' > "$d/a/x.py"
r=$(run "$d"); [ "$r" = 0 ] && ok 중복_없음_통과 || no 중복_없음_통과 "exit=$r"

d=$(tree t9)
r=$(run "$d"); [ "$r" = 0 ] && ok 빈_트리_통과 || no 빈_트리_통과 "exit=$r"

echo "-- 결과: PASS=$PASS FAIL=$FAIL --"
[ "$FAIL" = 0 ]
