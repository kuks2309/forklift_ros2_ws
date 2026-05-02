# 기술 부채 방지 원칙

기술 부채를 누적하지 않기 위해 지키는 원칙의 단일 근원(SSOT).

## 핵심 원칙: 정공법 우선

- 시간이 더 걸리더라도 **근본 원인 해결**(정공법) 을 선택한다.
- workaround / monkey-patch / 우회 코드 / 임시 hack 은 기본적으로 금지.
- 정공법이 명백히 비현실적인 경우(외부 의존성 버그 등) 에 한해 우회를 제안하되, 다음을 **모두** 만족할 때만 적용:
  1. 정공법의 비용/리스크와 우회 방식을 함께 제시
  2. 사용자 명시 승인
  3. 우회 사유 + 정리 일정을 [issues_and_fixes/issues_and_fixes.md](../issues_and_fixes/issues_and_fixes.md) 또는 ADR Open Question 에 기록

## 시간 트레이드오프 보고 의무

- 정공법으로 추가 시간이 발생할 것이 예상되면 **착수 전** 사용자에게 보고한다.
- "빠른 수정" 을 사용자가 명시 요청하지 않은 이상 정공법을 기본으로 한다.

## 임시·진단 코드 정리

- 디버그 print, 임시 로그, 진단 stub 은 동일 작업 완료 시 같은 작업 단위에서 제거한다.
- 다음 작업으로 미루는 경우 [issues_and_fixes/issues_and_fixes.md](../issues_and_fixes/issues_and_fixes.md) 에 due 항목 등록 후에만 허용.

## TODO 코멘트 정책

- 새 TODO 코멘트 추가 시 [issues_and_fixes/issues_and_fixes.md](../issues_and_fixes/issues_and_fixes.md) 에 대응 엔트리를 동시에 작성한다.
- TODO 만 남기고 작업을 종료하지 않는다.

## ADR Open Question 관리

- ADR 의 OQ(미해결) 항목은 작성 시점부터 **30 일** 내 재평가하여 결정 보완 또는 OQ 닫기 처리한다.
- 30 일 경과 OQ 는 [issues_and_fixes/issues_and_fixes.md](../issues_and_fixes/issues_and_fixes.md) 에 회수 항목으로 등록.

## 적용 우선순위

본 규칙과 [coding.md](coding.md) "지시사항 회피 대안 제시 절대 금지" 가 충돌하면 **본 규칙이 우선한다** (우회 = 지시 회피의 일종으로 본다).
