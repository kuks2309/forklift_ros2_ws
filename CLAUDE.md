# Claude 작업 지침

## 1. 핵심 원칙
1. 사용자가 지시한 사항만 수행한다
2. 임의로 기능을 추가하거나 변경하지 않는다
3. 코딩 전 구조를 먼저 제시하고 승인받는다
4. 증거 없이 "동일합니다" 말하지 않는다
5. 코딩 작업전에 충분히 기존 파일 확인하고 중복함수, 중복 변수, 중복 로직 없도록 확인

---

## 2. 문서 작업 규칙 (먼저 읽기)

작업 영역에 따라 **시작 전 반드시** 해당 README 를 먼저 읽고 규칙을 따른다. 규칙은 각 파일이 단일 근원(SSOT) 이며 본 CLAUDE.md 에 복제하지 않는다.

### Claude 작업 지침 (메타 규칙)

- 진입점 → [docs/claude_guideline/README.md](docs/claude_guideline/README.md)
  - GitHub 워크플로 → [docs/claude_guideline/github.md](docs/claude_guideline/github.md)
  - 코드 작업 규칙 → [docs/claude_guideline/coding.md](docs/claude_guideline/coding.md)
  - 작업 절차 체크리스트 → [docs/claude_guideline/workflow.md](docs/claude_guideline/workflow.md)
  - 문서 작성 방법 → [docs/claude_guideline/documentation.md](docs/claude_guideline/documentation.md)
  - 기술 부채 방지 → [docs/claude_guideline/tech_debt.md](docs/claude_guideline/tech_debt.md)
  - 프로젝트별 override → [docs/claude_guideline/local/](docs/claude_guideline/local/)

규칙 변경이 필요하면 해당 README 수정 여부를 먼저 사용자에게 문의한다.

---

## 3. 아키텍처 원칙 (절대 위반 금지) — 프로젝트 고유

### UI와 로직 분리
| 파일 | 역할 | 금지 사항 |
|------|------|----------|
| `main_window.py` | UI 이벤트 핸들링, 표시 업데이트 | 비즈니스 로직 작성 금지 |
| `services/*.py` | 비즈니스 로직, 데이터 처리 | UI 직접 조작 금지 |
| `job_executor.py` | Job 실행 엔진 | UI 직접 조작 금지 |

---

## 4. 프로젝트 고유 추가 규칙 (forklift_ros2_ws)

`docs/claude_guideline/` 의 메타 규칙에 추가로 본 프로젝트에서 적용한다.

### 추가 금지 사항 (coding.md 보강)
- 빌드 설정 수정 금지 (tasks.json, CMakeLists.txt)

### 작업 종료 보고 추가 항목 (workflow.md 보강)

`workflow.md` 의 기본 체크리스트와 보고 형식 외에 본 프로젝트에서 추가로 확인할 항목:

```markdown
- [ ] 증거 없이 "동일합니다" 말하지 않았는가?
- [ ] 아키텍처 원칙 준수 (UI/로직 분리)
- [ ] (ROS 변환 시) 제어 루프 순서 동일한가?
- [ ] (파일 수정 시) git add 로 staging 했는가?
```
