# TR-AFL-SES-001 v4 → v5 변경 목록

- 결과물: [CLARK_SES_Modify_v5.pdf](CLARK_SES_Modify_v5.pdf) (17쪽 = 본문 13쪽 + 변경 이력 3쪽(14–16p) + 개정 이력 요약 1쪽(17p, Rev 표 + 분류 12개별 정리))
- 원본: `CLARK_SES_Modify_v4.pdf` — 수정하지 않음 (상위 `Ford-fork-lift/` 로컬, 저장소 미포함)
- 근거: [TR-AFL-SES-001_v4_review.md](TR-AFL-SES-001_v4_review.md) (회로도 IN-28587 Rev E 대조 검토, 2026-11-17)
- 반영 범위(사용자 결정 2026-11-17): 도면과 다른 표기는 **수정**, 설계 지적은 결정하지 않고 **검토(안)** / TBC 로 추가
- 방식: 원본 .pptx 가 없어 PDF 위에서 직접 고쳤다. 고칠 줄의 글자를 지우고 같은 자리에 새 글자를 썼다(PyMuPDF redaction + 글자 삽입). 원래 글꼴(맑은 고딕)이 없어 고친 글자는 나눔고딕이다.
- 표시:
  - 바뀐 글자 = 보라색
  - 바뀐 곳 = 보라 점선 테두리 + 번호 꼬리표 (아래 표의 # 와 같음)
  - 쪽마다 오른쪽 위에 "v5 수정 (회로도 대조)" 범례
  - 보라색은 기존 범례(빨강 동력 · 주황 12V · 파랑 CAN · 녹색 신규)와 겹치지 않게 골랐다
- 구분: 번호 붙은 69건 = 수정 30 · 검토(안) 31 · 추가 8 (표의 구분 열 기준) + 공통 1건
- 이 표는 PDF 14–16p 변경 이력과 같은 내용이다.

| # | 쪽 | 구분 | v4 | v5 |
|---|---|---|---|---|
| 공통 | 전 쪽 | 수정 | 꼬리말 Rev. v4 · 본문 ‘ACO’ | Rev. v5 · ‘AC0’(숫자 0, 도면 표기 EPS AC0) |
| 1 | 1p | 수정 | Rev. v4 · 2026-11-17 | Rev. v5 · 회로도 IN-28587 대조 검토 반영 |
| 2 | 2p | 추가 | BASE TRUCK: SR14-16 도면 참조 | 표제 모델 SRX14/16 · Sheet 2 of 2 (Sheet 1 미확보) 명시 |
| 3 | 2p | 검토(안) | 개조 내용 요약 | v5 검토(안) 항목 요약 추가 (5–9p) |
| 4 | 3p | 수정 | EPS FUSE 40A 가 LINE CONTACTOR 뒤에 연결 | EPS FUSE 40A 는 LC 앞 배터리 직결 (도면 F12–F11) |
| 5 | 3p | 수정 | KEY SWITCH / KEY OUT | KEY SWITCH → MAIN RELAY 코일 (KEY OUT 은 M 계통 F4) |
| 6 | 3p | 수정 | M 계통 FUSE F4·F6·F7·F8·F20·F23 | F4·F5·F6·F7·F8·F23 (F20 은 DISPLAY용 12V 쪽) |
| 7 | 3p | 수정 | DC-DC 로직 전원 12V (F5 10A) | 12V 액세서리 전원 (F5 10A) — 제어기 로직은 KEY 48V |
| 8 | 3p | 추가 | 12V 부하 (F11–F22) | ※ F20 = DISPLAY용 DC-DC 12V 출력 퓨즈 |
| 9 | 3p | 수정 | M 계통 → 컨트롤러 KEY(A1), DISPLAY, MHYRIO CB 전원 | M 계통 → KEY(TRACTION·PUMP A1, EPS A7) · F4 → KEY SWITCH OUT 48V · F23 → DISPLAY DC-DC · MHYRIO BATT+(B2) 는 상시 F9/F10 |
| 10 | 3p | 수정 | CAN ENCODER 120R 표기 | 내부 120R (CANTH 미결선 — 종단 아님) |
| 11 | 3p | 수정 | CAN TILLER 10–30VDC, 200mA 출력 | 조이스틱·스위치·PNP 센서 입력 (해당 문구는 PNP 센서 사양) |
| 12 | 3p | 수정 | H/SW · FWD/REV는 TRACTION 직결 | FWD/REV 버튼 → TRACTION A4 직결 · H/SW → 혼 릴레이 |
| 13 | 3p | 수정 | VALVES 24V (PR1/PR3 PROP, S1–S4) | VALVES 24V (PR1–PR3, S1–S4, SV1–SV4) |
| 14 | 3p | 수정 | 종단 표기: EPS 120Ω, CAN ENCODER 120R, MHYRIO CAN T | 종단 = EPS AC0 120Ω(외부) · MHYRIO B14–B9 점퍼, ENCODER 미결선 → 60Ω 실측 |
| 15 | 3p | 추가 | FUSE 300A | 도면 하단 'FUSE 350Ax2' 문구 → 실차 확인 |
| 16 | 4p | 수정 | CAN ENCODER: 120R 표기 | 내부 120R (CANTH 미결선) |
| 17 | 4p | 수정 | CAN TILLER: 10–30VDC, 200mA (출력) | – (10–30VDC 200mA 는 PNP 센서 사양) |
| 18 | 4p | 수정 | CAN TILLER 역할: … 스위치 입력, PNP 출력 | … 유압 지령(추정), 스위치·PNP 센서 입력 11점 |
| 19 | 4p | 수정 | 종단 관련 표기: EPS 120Ω, CAN ENCODER 120R, MHYRIO CAN T | 종단: EPS AC0 120Ω(외부) · MHYRIO B14–B9 점퍼 / ENCODER 미결선 → 60Ω 실측 |
| 20 | 4p | 수정 | 자율화 관점 핵심 3개 항목 | CAN 지령 → PUMP·MHYRIO(추정) / ACC ENABLE·SEAT·PEDAL BRAKE 직결 추가 / 조향 = 2상 STEPPER 4선 |
| 21 | 4p | 검토(안) | – | 조향은 COUNTER 로 대체 불가 · 밸브는 CAN 경로로 통일 검토 |
| 22 | 5p | 수정 | EPS FUSE 40A 가 LINE CONTACTOR 뒤에 연결 | EPS FUSE 40A 는 LC 앞 배터리 직결 |
| 23 | 5p | 검토(안) | SAFETY PLC OUT: LC · 트랙션 · 브레이크 | + P1 키 체인 차단 검토(안) |
| 24 | 5p | 검토(안) | ② 가속·방향·조향·밸브: CREVIS IO + K1–K4 | + 밸브 K4 는 ①과 중복 → 삭제 검토(안) |
| 25 | 5p | 검토(안) | 운전자 조작 입력: ACC PEDAL · FWD/REV · STEERING | + ACC ENABLE · SEAT · DEAD MAN · PEDAL BRAKE (AUTO 대체 TBC) |
| 26 | 5p | 검토(안) | DC-DC → 24V (절연) PC · 센서 · IO 전원 | + 인입 지점 · 전용 퓨즈 TBC · 60W 부하 합계 확인 |
| 27 | 5p | 검토(안) | CREVIS: AO · 가속 페달 · 밸브 | AO · 가속 (밸브 삭제 검토) |
| 28 | 5p | 검토(안) | CREVIS: CNT · 스티어링 입력 | CNT · 조향 (방식 재검토) |
| 29 | 5p | 검토(안) | CAN SWITCH: 통과 · 차단 · PC 지령 주입 | + TILLER 송신 전체 대체 범위 TBC |
| 30 | 6p | 수정 | FWD/REV SWITCH · 방향 선택 (디지털) | FWD/REV 버튼(조이스틱) · A4 단일 입력, 동작 TBC |
| 31 | 6p | 수정 | STEERING INPUT · STEPPER MOTOR | 2상 STEPPER (4선 A8–A11) |
| 32 | 6p | 수정 | MHYRIO CB 밸브 출력 · PR1/PR3 PROP · S1–S4 | PR1–PR3 · S1–S4 · SV1–SV4 |
| 33 | 6p | 검토(안) | K4 밸브 / AO 밸브 지령 | 삭제 검토(안) — 유압은 CAN 경로 (출력 20단자 · 코일 전류 · 펌프 지령 부재) |
| 34 | 6p | 검토(안) | DO · 전진/후진 | DO → 릴레이 코일, 접점이 KEY OUT 48V 를 A4 에 인가 (안) |
| 35 | 6p | 검토(안) | COUNTER · 스티어링 입력 | 방식 재검토 — COUNTER 는 입력 채널, 2상 스텝모터 신호 생성 불가 |
| 36 | 6p | 검토(안) | AO · 가속 지령 전압 | + AO 기준 -BATT(A9) · 접지 설계 TBC |
| 37 | 6p | 검토(안) | 모드 신호 → 릴레이 코일 · 무여자 = MANUAL (안) | + 코일 경로에 워치독 · Safety PLC 접점 직렬 (안) |
| 38 | 6p | 검토(안) | – | 주행 허가 입력(ACC ENABLE·SEAT·DEAD MAN·PEDAL BRAKE) 미반영 → Safety PLC 제어 검토(안) |
| 39 | 7p | 수정 | LC 차단: TRACTION NLC(A16) 코일 경로 | P2 경로 직렬 (LC 코일 ↔ A17) |
| 40 | 7p | 수정 | TRACTION ENABLE 해제 (결선 TBC) | DEAD MAN 라인(EPS A4 → A10) 차단 (안) |
| 41 | 7p | 수정 | 브레이크 작동: 전자 브레이크 적용 (방식 TBC) | 주행 EM(A18) · 로드휠 EM(PUMP A16/A18) — 제어기 경유 우선 |
| 42 | 7p | 검토(안) | – | P1 키 체인 차단 추가 — LC 만으로는 EPS(LC 앞)·MHYRIO(상시 F9/F10) 전원 유지 |
| 43 | 7p | 검토(안) | 결정 필요 3. AUTO 모드 DEAD MAN | 3. AUTO 운전자 감지 입력 4종 우회 = Safety PLC 제어 (안) |
| 44 | 7p | 검토(안) | – | 결정 필요 5. 안전정지 차단 범위 / 6. MANUAL 모드 처리 |
| 45 | 7p | 검토(안) | IPC · 모드 스위치 · CREVIS IO 와 연결 없음 | 원칙은 결정 3 · 6 후 갱신 |
| 46 | 8p | 검토(안) | AUTO: CREVIS IO(가속·방향·조향·밸브) | CREVIS IO(가속·방향·조향) · 밸브 K4 삭제 검토(안) |
| 47 | 8p | 검토(안) | AUTO 시 DEAD MAN / 운전자 감지 처리 TBC | 운전자 감지 4종 처리 TBC + TILLER 송신 전체(입력 11점) 대체 범위 TBC |
| 48 | 8p | 검토(안) | – | 게이트웨이 워치독: 마지막 프레임 반복 금지 · 중립 프레임 (안) |
| 49 | 9p | 수정 | DO 행: FWD/REV 스위치 / CREVIS DO → 릴레이 NO / 접점·전압 레벨 TBC | FWD/REV 푸시버튼 → A4 / DO → 릴레이 코일, 접점이 KEY OUT 48V 인가 (안) / A4 단일 입력 동작 TBC |
| 50 | 9p | 검토(안) | AO 가속 비고: 전압 범위 · 원 페달 신호 동일 사양 모사 | + AO 기준 -BATT(A9) 접지 설계 · ACC ENABLE(A13) 동시 처리 |
| 51 | 9p | 검토(안) | AO 밸브 행 (PR1/PR3 PROP · S1–S4) | 밸브 PR1–PR3·S1–S4·SV1–SV4 / AUTO: 삭제 검토(안) — 유압은 CAN 경로 |
| 52 | 9p | 검토(안) | COUNTER 비고: 펄스 방식 · 모듈 역할 TBC | 2상 스텝모터 입력 → COUNTER(입력)로 생성 불가, 방식 재검토(안) |
| 53 | 9p | 검토(안) | K1–K4 코일은 MODE 키 스위치 신호로 구동 | + 코일 경로에 워치독 · Safety PLC 접점 직렬 (안) |
| 54 | 9p | 수정 | 신호 레벨 … 조향 COUNTER 방향/출력 · 밸브 AO 앰프 … | … 조향 입력 대체 방법 · 접지(절연 계통 ↔ -BATT) … |
| 55 | 9p | 검토(안) | – | 주행 허가 입력 4종 매핑 추가 (AUTO 대체 방식 TBC) |
| 56 | 10p | 검토(안) | CAN SWITCH 비고: 모델 미정 (TBC) | + TILLER 대체 범위 · 워치독 중립 출력 TBC |
| 57 | 10p | 수정 | DC-DC: RSD-60L-24 → 24V 2.5A, 60W, 절연 / 부하 합계 · 퓨즈 TBC | + 입력 18–72VDC(datasheet) / 인입 지점 · 퓨즈 · 부하 합계 TBC |
| 58 | 10p | 검토(안) | 절환 릴레이: 가속·FWD/REV·조향·밸브 | + (K4 삭제 검토(안)) |
| 59 | 10p | 수정 | 2. 120Ω 종단: 실제 종단 위치 확인 | 종단 = EPS 외부 120Ω · MHYRIO 점퍼 (ENCODER 미결선) → 60Ω 실측 |
| 60 | 10p | 수정 | 4. ZAPI 파라미터: … 시트/데드맨 | … 시트 · 데드맨 · ACC ENABLE · PEDAL BRAKE |
| 61 | 10p | 수정 | 5. 조향 COUNTER 방향/출력 역할, 밸브 AO 앰프 … | 조향: 2상 스텝모터 신호 대체 방법 · 밸브: CAN 경로 통일 검토(안) |
| 62 | 10p | 검토(안) | 6. AUTO 모드 DEAD MAN 처리 … | AUTO 운전자 감지 입력 처리 · 차단 범위(P1/P2) … |
| 63 | 10p | 추가 | – | 8. 24V 전원: DC-DC 인입 지점 · 퓨즈 · 60W 부하 합계 |
| 64 | 11p | 수정 | DC-DC 인증 등급: 확인 필요 | UL 62368-1 approved (datasheet) · UL 583 적합성 확인 필요 |
| 65 | 11p | 추가 | – | 도면 Note 1: 추가 부품은 UL Listed / Recognized 및 표시 필요 |
| 66 | 12p | 검토(안) | – | ANSI/ITSDF B56.1 행 추가 (원문 미확인) |
| 67 | 13p | 추가 | CLARK 질문 ①–⑥ | ⑦–⑪ 추가 (FWD/REV · 조향 · 주행 허가 입력 · P1/P2 · TILLER) |
| 68 | 13p | 추가 | 컨설턴트 질문 ①–⑤ | ⑥ 운전자 감지 우회 분류·PL ⑦ MANUAL 모드 Safety LiDAR 처리 |
| 69 | 13p | 추가 | 참고 페이지 | + 14–16p 변경 이력 · 17p 개정 이력 요약 |
