#!/usr/bin/env bash
# test_fix_chain.sh — fix-chain.sh 계약 테스트 (독립 샌드박스, 생성·정리 자체 수행)
set -uo pipefail
CHK="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/fix-chain.sh"
PASS=0; FAIL=0
ok(){ echo "  ✓ $1"; PASS=$((PASS+1)); }
ng(){ echo "  ✗ $1"; FAIL=$((FAIL+1)); }

mkrepo(){  # 새 샌드박스 repo + fix-chain.sh 를 checks/ 위치 관례로 배치
  R="$(mktemp -d)"
  git -C "$R" init -q
  git -C "$R" config user.email t@t; git -C "$R" config user.name T
  mkdir -p "$R/docs/claude_guideline/coding/checks"
  cp "$CHK" "$R/docs/claude_guideline/coding/checks/fix-chain.sh"
  echo base > "$R/f"; git -C "$R" add f; git -C "$R" commit -qm "chore(x): base"
}
cmt(){ echo "$RANDOM" >> "$R/f"; git -C "$R" add f; git -C "$R" commit -qm "$1"; }
run(){ ( cd "$R" && bash docs/claude_guideline/coding/checks/fix-chain.sh >/dev/null 2>&1 ); RC=$?; }
fin(){ rm -rf "$R"; }

echo "V1 같은 scope 연속 fix 2회 → 통과"
mkrepo; cmt "fix(mod): a"; cmt "fix(mod): b"; run
[ "$RC" = 0 ] && ok "rc=0" || ng "rc=$RC (기대 0)"; fin

echo "V2 연속 fix 3회 → 차단"
mkrepo; cmt "fix(mod): a"; cmt "fix(mod): b"; cmt "fix(mod): c"; run
[ "$RC" = 1 ] && ok "rc=1 (재검토 요구)" || ng "rc=$RC (기대 1)"; fin

echo "V3 3회지만 연쇄 안에 재검토 결론 존재 → 통과"
mkrepo; cmt "fix(mod): a"; cmt "fix(mod): b"
echo x >> "$R/f"; git -C "$R" add f
git -C "$R" commit -qm "fix(mod): c" -m "아키텍처 재검토: 개별 결함으로 판정 — 설계 이상 없음"
run; [ "$RC" = 0 ] && ok "rc=0 (재검토 인정)" || ng "rc=$RC (기대 0)"; fin

echo "V4 fix·fix 후 feat 가 연쇄 리셋 → 이후 fix 1회는 통과"
mkrepo; cmt "fix(mod): a"; cmt "fix(mod): b"; cmt "feat(mod): 재설계"; cmt "fix(mod): c"; run
[ "$RC" = 0 ] && ok "rc=0 (feat 리셋)" || ng "rc=$RC (기대 0)"; fin

echo "V5 다른 scope 커밋이 끼어도 같은 scope 연쇄는 이어짐 → 3회 차단"
mkrepo; cmt "fix(mod): a"; cmt "fix(other): x"; cmt "fix(mod): b"; cmt "feat(other): y"; cmt "fix(mod): c"; run
[ "$RC" = 1 ] && ok "rc=1 (모듈별 독립 연쇄)" || ng "rc=$RC (기대 1)"; fin

echo "V6 HEAD 가 비-fix → 판정 대상 아님(통과)"
mkrepo; cmt "fix(mod): a"; cmt "fix(mod): b"; cmt "fix(mod): c"; cmt "docs(mod): 정리"; run
[ "$RC" = 0 ] && ok "rc=0" || ng "rc=$RC (기대 0)"; fin

echo "V7 pre-commit 탈출구 FIX_CHAIN_REVIEWED=1 → 통과"
mkrepo; cmt "fix(mod): a"; cmt "fix(mod): b"; cmt "fix(mod): c"
( cd "$R" && FIX_CHAIN_REVIEWED=1 bash docs/claude_guideline/coding/checks/fix-chain.sh >/dev/null 2>&1 ); RC=$?
[ "$RC" = 0 ] && ok "rc=0" || ng "rc=$RC (기대 0)"; fin

echo
if [ "$FAIL" -eq 0 ]; then echo "✓ 전체 통과 ($PASS)"; exit 0
else echo "✗ 실패 $FAIL / 통과 $PASS"; exit 1; fi
