# Changelog

## 1.2.0 — 2026-05-01

- `tech_debt.md` 신규 추가 — 기술 부채 방지 원칙 (정공법 우선)
  - 핵심 원칙: 시간이 더 걸리더라도 근본 원인 해결, workaround 금지
  - 우회 사용 시 3가지 조건 (비용/리스크 제시 + 사용자 승인 + 정리 일정 기록) 모두 만족 필수
  - 시간 트레이드오프 보고 의무
  - 임시·진단 코드 정리 / TODO 코멘트 정책 / ADR Open Question 30일 재평가 정책
  - `coding.md` "회피 대안 절대 금지" 와 충돌 시 본 규칙 우선
- `README.md`: 진입점 표에 `tech_debt.md` 행 추가

## 1.1.0 — 2026-04-30

- `github.md`: "커밋·푸쉬는 작업 단위로 분리" 섹션 추가
  - 작업 단위 = 커밋 단위 = push 단위 원칙
  - staged 범위 검증 절차 (`git status --short`, `git diff --cached --name-only`)

## 1.0.0 — 2026-04-30

- 초기 릴리스
- `claude_guideline/` 5 개 파일 추가: `README`, `github`, `coding`, `workflow`, `documentation`
- `install.sh`, `update.sh`, `VERSION`, `CHANGELOG.md` 추가
- `templates/CLAUDE.md.template` 추가 (프로젝트별 CLAUDE.md 골격)

## 정책

- **major** (X.0.0): 기존 규칙과 호환 안 됨, 수동 마이그레이션 필요
- **minor** (X.Y.0): 규칙 추가, 호환됨
- **patch** (X.Y.Z): 오탈자, 표현 수정
