# TR-AFL-SES-001 Rev. v4 검토 — 회로도 IN-28587 대조

- **검토 대상**: `CLARK_SES_Modify_v4.pdf` (TR-AFL-SES-001 (가) Rev. v4, 2026-11-17, 13쪽)
- **검토일**: 2026-11-17
- **대조 1차 source**: CLARK IN-28587 Wiring Diagram SRX14/16 Rev E, page 1 (`References/clark/srx14-16/clark_srx14-16_IN-28587_wiring-diagram_revE.pdf` — OEM 정비 자료라 이 저장소에는 넣지 않았다. 상위 `Ford-fork-lift/` 로컬에 있음)
  - 300 DPI 렌더(같은 폴더의 `…_revE_300dpi.png`, 저장소 미포함)를 구역별로 확대해 직접 읽었다.
  - 위치 표기 `p1 F12` = 도면 page 1 의 테두리 격자 Zone F12 (행 M(위)~A(아래), 열 12(왼쪽)~1(오른쪽)).
- **보조 1차 source**: [MEAN WELL RSD-60 series SPEC (File 2026-07-09), page 2 · page 7](../../../References/meanwell/rsd-60/RSD-60-SPEC.pdf) — 제조사 공식 PDF(`meanwell.com/Upload/PDF/RSD-60/RSD-60-SPEC.PDF`, accessed 2026-11-17)
- **참고(파생 문서)**: `docs/clark/srx14-16/IN-28587_wiring_diagram_controllers.md`(상위 `Ford-fork-lift/` 로컬, 저장소 미포함) — 같은 도면의 기존 판독. 이 검토에 인용한 결선은 모두 원본 이미지에서 다시 확인했다.
- **검증 등급**: **✓** 도면·datasheet 에서 직접 확인 / **⚠** 추론·일반 지식(확인 필요). 다른 보고만 옮긴 **ⓦ** 항목은 없다.
- **한계**: 도면은 SR14-16(표제 모델 SRX14/16)용 **Sheet 2 of 2** 뿐이다. SES 실제 도면과 다를 수 있으므로 아래 핀 번호·결선 지적은 모두 "SR14-16 기준"이다. ZAPI 제어기의 입력 문턱·알람 반응은 도면에 없어 전부 ⚠ 이다.

---

## 0. 요약

v4 의 CAN 단자 표(4p)와 퓨즈·정격 값은 도면과 대체로 맞는다. 다만 회로도와 맞대 보면 개조 개념에 큰 공백이 5개 있다.

| # | 등급 | 지적 | 근거 |
|---|---|---|---|
| 1 | 중대 | **안전정지가 LC(Line Contactor)만 끊으면 멈추지 않는 계통이 남는다.** EPS(Electric Power Steering) 동력(40A)은 LC 앞, MHYRIO 전원(F9/F10)은 상시 버스다. 3p·5p 개념도는 EPS 를 LC 뒤에 그려 이 문제가 드러나지 않는다. | ✓ p1 F12, L11–L10 |
| 2 | 중대 | **AUTO 주행에 필요한 하드와이어 허가 입력이 빠졌다.** ACC. ENABLE SW(TRACTION A13), SEAT(A6), PEDAL BRAKE(PUMP A13)가 없고 DEAD MAN(A10)은 TBC 다. 운전자 감지 입력을 우회하면 OEM(Original Equipment Manufacturer) 안전 인터록이 해제되므로, 우회는 PC·모드 릴레이가 아니라 Safety PLC(Programmable Logic Controller)가 맡아야 한다. | ✓ p1 E8–B7, D6 |
| 3 | 중대 | **조향 K3 + COUNTER 방식은 도면과 맞지 않는다.** EPS 조향 입력은 펄스가 아니라 영구자석 2상 스텝모터(4선)다. | ✓ p1 G8 |
| 4 | 중대 | **밸브 K4 + AO(Analog Output) 방식은 도면상 성립하기 어렵고 CAN(Controller Area Network) 유압 경로와 겹친다.** 출력이 밸브 11개·경보 릴레이 1개로 단자 20개(공통 + 8, − 12)이고, 코일 구동 전류와 펌프 모터 지령이 빠져 있다. | ✓ p1 E3–B2 |
| 5 | 주요 | **CREVIS 신호의 레벨·기준 전위가 원 신호와 다르다.** FWD/REV 는 48V(KEY OUT), SEAT·ACC ENABLE 은 −BATT 로 당기는 접점, 가속은 PPOT(+12V) 기준 전압이다. 절연된 24V 계통의 DO(Digital Output)/AO 를 그대로 넣으면 레벨이 맞지 않고, 절연 계통이 배터리 − 에 묶인다. | ✓ p1 E8, C8, B7 / datasheet p2 |

그 밖에 릴레이 코일 구동 논리의 문서 내 모순(§2-6), CAN 게이트웨이의 TILLER 메시지 대체 범위(§2-7), MANUAL 모드에서 Safety PLC 동작(§2-8), DC-DC 인입·용량(§2-9)이 있다. 문서 표기 오류 13건은 §1 표에 정리했다.

---

## 1. 도면 대조 — 사실 확인표

| # | v4 위치 | v4 기술 | 도면 내용 | 등급·근거 | 조치 |
|---|---|---|---|---|---|
| 1 | 3p·5p 동력 블록 | BATTERY → LINE CONTACTOR → FUSE 300A ×2 · **FUSE 40A(EPS)** | EPS 40A 퓨즈는 **LC 앞**에서 분기한다(배터리 + 직결). LC 뒤에는 PUMP·TRACTION 300A 2개만 있다. 퓨즈박스 상시 버스도 LC 앞에서 받는다. | ✓ p1 F12–F11(EPS 40A 분기), E12(LC) | 그림 수정. §2-1 과 직결 |
| 2 | 3p 제어 전원 | M 계통 FUSE F4·F6·F7·F8·**F20**·F23 | F20 5A 는 DISPLAY 전용 DC-DC 의 12V 출력 쪽(선번 49 → F20 → (E) → DISPLAY 1번)이다. M 버스 퓨즈는 F23·F6·F7·F8·F4·F5 다. | ✓ p1 L9–K9 | F20 → F5 |
| 3 | 3p | KEY SWITCH 블록에 "KEY OUT" | 키 체인은 F24 → 비상SW P1 → (L) → KEY SWITCH → (N) → MAIN RELAY 코일이다. 도면의 "KEY SWITCH OUT(48V)" 라인은 M 버스 F4 → 선번 18 → (K) 로 나온다. | ✓ p1 K10–J10, L8, E5 | KEY OUT 을 M 계통 F4 아래로 이동 |
| 4 | 3p | DC-DC CONVERTER "**로직 전원** 12V (F5 10A)" | F5 → 48V/12V DC-DC → 선번 100 → F11~F22(작업등·경광등·혼·경보·팬·카메라)다. 제어기 로직 전원은 각 KEY 입력 48V(F6·F7·F8)다. | ✓ p1 L8–K7, L6–L1 | "12V 액세서리 전원"으로 수정 |
| 5 | 3p 주석 | "M 계통 → … MHYRIO CB 전원" | MHYRIO BATT+ B2 는 **상시 버스 F9·F10**(키·비상SW 와 무관)이고, M 계통은 +KEY B1(K1 = KEY OUT)만이다. | ✓ p1 L11–L10, E1, B1 | 수정. §2-1 과 직결 |
| 6 | 3p·4p | CAN TILLER "10–30VDC, 200mA 출력" | 이 문구는 TILLER 에 연결된 PNP(Positive-Negative-Positive) 근접센서의 사양 표기다. TILLER 정격이 아니다. | ✓ p1 B3 | 삭제 또는 "PNP 센서 사양" |
| 7 | 3p | JOYSTICK "H/SW · FWD/REV는 TRACTION 직결" | FWD/REV 버튼(B11–B12) → (T)(T1) → TRACTION A4 는 맞다. H/SW(B9–B10)는 (H1)(H2) → HORN RELAY 로 간다. | ✓ p1 B5, K5 | "H/SW 는 혼 릴레이" |
| 8 | 3p·4p | 종단 표기 "CAN ENCODER 120R" | CAN ENCODER 내부 120R 은 CANTH(C4) 단자에 외부 결선이 없다. 종단 표기는 EPS A6–A14 사이 120Ω 1/4W 와 MHYRIO B14–B9 점퍼(MB9) 두 곳이다. | ✓ p1 G2, G7, E2 | "종단 = EPS·MHYRIO 2곳(⚠ 추정), ENCODER 미사용"으로 쓰고 키 OFF 상태에서 CAN H–L 60Ω 실측 |
| 9 | 6p·9p | FWD/REV SWITCH "방향 선택 (디지털)" | 조이스틱의 **모멘터리 푸시버튼 1개** → TRACTION A4 **단일 입력**이다. 전진·후진 2입력 구조가 아니다. 누를 때마다 방향을 바꾸는지 등 동작 의미는 도면에 없다. | ✓ p1 B5, E8 / 의미 ⚠ | DO 1점으로 방향을 고를 수 없을 수 있음 → CLARK 질문 추가(§3) |
| 10 | 3p | VALVES "PR1/PR3 PROP, S1–S4" | 그 외 SV1–SV4(TILTING·SIDESHIFT·FORK POS.·STACKING), PR2, T/ALARM 릴레이까지 출력 12개다. | ✓ p1 E3–B2 | 목록 보완 |
| 11 | 전체 | "ACO EPS" | 도면 표기는 "EPS AC0"(숫자 0)다. | ✓ p1 H8 | 오탈자 |
| 12 | 3p | FUSE 300A | 회로에는 300A ×2 로 그려져 있으나 하단 테두리에 "FUSE 350Ax2" 문구가 있다. | ✓ p1 하단 테두리 11열 | 실차 확인 항목에 추가 |
| 13 | 4p | PIN CODE CAN 2/3 | 핀 라벨(2 = CANH, 3 = CANL)은 맞다. 다만 선번 P2 가 W(흰색), P3 가 R(빨강)으로, 다른 노드의 관례(CAN H = R, CAN L = W)와 반대다. | ✓ p1 G6 / 의미 ⚠ | SES 하네스에서 선 색 확인 |
| 14 | 4p "자율화 관점 핵심" | "CAN 운전 지령: CAN TILLER → 유압(MHYRIO CB)" | 도면에는 데이터 흐름 표기가 없다. 유압에는 펌프 모터 회전(ACE2 PUMP)도 필요하다. | ⚠ | "추정" 표기 + PUMP 포함 |
| 15 | 11p | 부품 인증 "확인 필요" | 도면 Note 1: "MUST BE AN UNDERWRITERS LABORATORIES INC. LISTED OR RECOGNIZED COMPONENT AND BE SO MARKED" | ✓ p1 M3–M1 | 추가 부품의 판단 기준으로 이 Note 를 인용 |

**도면과 일치(수정 불요)** ✓:
- 4p CAN 단자 전체: TRACTION A21/A20, PUMP A21/A20, EPS A14/A6, DISPLAY 3/2, PIN CODE 2/3, ENCODER C7/C6, TILLER B4/B1, MHYRIO B13/B4, CAN T B9, CANH OUT B14 (p1 G7–E2)
- 정격: 450Arms ×2, 45Arms, 모터 7.2kW·14.8kW·400W, DISPLAY 12/24V 10W
- F24 2A · F1 15A · F5 10A
- LC 코일 = TRACTION NLC(A16) + 비상SW P2 직렬 (p1 D8–D7)
- Note 3: CAN 선은 실드 트위스트, 실드는 MAIN GROUND 접속 (p1 M3–M1)

---

## 2. 설계 검토 — 회로도 기준 지적

### 2-1. [중대] 안전정지: LC 만 끊으면 멈추지 않는 계통이 남는다

**도면 사실** ✓
- OEM 비상스위치는 2접점이다.
  - P1 = 키 체인(F24 → P1 → KEY SWITCH → MAIN RELAY 코일)을 끊는다 → M 버스 전체(모든 제어기 KEY, KEY OUT, MHYRIO +KEY)가 꺼진다 (p1 K10–J10).
  - P2 = LC 코일 경로(NLC A16 ↔ A17 공통 노드)를 직렬로 끊는다 (p1 D8–D7).
- EPS 동력은 LC 앞 40A 퓨즈에서 받는다 (p1 F12).
- MHYRIO BATT+ 는 상시 버스 F9/F10 에서 받는다 (p1 L11–L10).
- 브레이크 코일은 3개다: 주행 EM(Electro-Magnetic) BRAKE(TRACTION A18), 로드휠 EM-RH/LH(PUMP A16/A18) (p1 D8, C6).

**v4 의 공백**
- 7p 는 Safety PLC 출력을 "LC 차단 · TRACTION ENABLE 해제 · 브레이크" 로만 정의한다.
- LC 를 끊어도 MHYRIO 전원은 살아 있어 밸브를 계속 구동할 수 있다 ✓(결선). 하강(PR1)이 펌프 없이 자중으로 동작하는 유압 회로라면 안전정지 중에도 포크가 내려갈 수 있다 ⚠(유압 회로 미확인).
- EPS 동력단도 살아 있다 ✓(결선).

**제안** (⚠ CLARK 확인 전제)
- E-STOP 은 **OEM 비상스위치와 같은 두 경로**로 끊는다. Safety PLC 안전출력 접점을 P1 경로(선번 10–10A)와 P2 경로(선번 16 ↔ A17 노드)에 각각 직렬로 넣는다. OEM 이 이미 쓰는 차단 지점이라 제어기의 반응(알람·브레이크)이 검증된 경로를 그대로 쓰게 된다.
- Safety LiDAR·Bumper 보호정지는 매번 키 체인을 끊으면 재기동이 필요하다. 단계 정지를 검토한다: ① 주행 허가 해제(§2-2 의 DEAD MAN 라인 차단 → 컨트롤러 설정대로 감속) → ② 지연 후 P2 경로로 LC 차단. 유압 정지 방법(MHYRIO +KEY 차단 등)도 함께 정한다.
- 브레이크 코일을 외부에서 직접 끊으면 주행 중 급제동, 제어기 출력 이상 알람이 날 수 있다 ⚠. 제어기가 브레이크를 걸게 하는 허가 해제 방식을 우선하고, 직접 차단은 CLARK 확인 뒤에 정한다.
- 3p·5p 그림에서 EPS 위치를 고쳐야 이 논의가 문서에 드러난다.

### 2-2. [중대] AUTO 주행 허가 입력 누락 — 운전자 감지 우회는 Safety PLC 몫

**도면 사실** ✓ (p1 E8–B7, F8–F7, D6)

| 입력 | 결선 | v4 반영 |
|---|---|---|
| TRACTION A10 DEAD MAN SW | EPS SAFETY CONTACTS(A5→A4) → "ELECTROMECHANICAL BRAKE & TRACTION ENABLE" 라인 → 데드맨 SW → A10 | TBC 로만 언급 |
| TRACTION A6 SEAT | 시트 SW → −BATT(TA9B) | 13p ③ 에 "시트" 언급만 |
| TRACTION A13 ACC. ENABLE SW | 가속 허가 SW → −BATT(TA9A) | **없음** |
| PUMP A13 PEDAL BRAKE | KEY OUT → 페달 브레이크 SW → A13 | **없음** |

- 운전자가 없는 AUTO 에서는 이 입력들이 "주행 불가" 상태일 가능성이 크다 ⚠(입력 극성·반응은 ZAPI 파라미터 의존).
- K1(가속 CPOT)만 절환하면 주행이 안 되거나, 가속 허가–포텐셔미터 순서 검사에 걸릴 수 있다 ⚠.
- DEAD MAN·SEAT 를 우회하는 접점은 OEM 운전자 감지 인터록을 무력화한다. 따라서 안전기능으로 다뤄야 할 가능성이 크다 ⚠(판정은 컨설턴트). 이는 v4 의 "Safety PLC 는 모드 스위치와 연결 없음" 원칙과 충돌하므로 결정이 필요하다.
- **결선 제안**: 우회 접점은 **데드맨 스위치에만 병렬**로 두고, EPS SAFETY CONTACTS(A4)는 직렬로 남긴다. 그래야 EPS 이상 시 주행 허가가 끊기는 OEM 기능이 보존된다.

### 2-3. [중대] 조향(K3 + COUNTER) — 입력 형태가 펄스가 아니다

- **도면** ✓ (p1 G8): EPS 조향 입력 "STEPPER MOTOR" 는 영구자석 회전자(N/S 기호) + 중간탭 2상 권선이고, 4선이다 — A10 BLACK GND, A9 RED(DL), A8 BLUE(QL), A11 WHITE.
- **해석** ⚠: 핸들에 물린 스텝모터를 돌릴 때 생기는 2상 교류 전압을 EPS 가 읽는 구조로 보인다(ZAPI EPS-AC0 매뉴얼로 확인 필요). 이 경우:
  - CREVIS COUNTER 는 입력 계측 채널이라 이 신호를 만들어 낼 수 없다. 회전 속도·방향에 맞춰 2상 교류를 생성하는 전용 신호 발생기가 필요하다.
  - EPS 가 권선 단선을 검출한다면 릴레이 절환 순간에도 알람이 날 수 있다.
- **대안** (모두 ⚠):
  - (a) 조향 컬럼에 기계식 구동기 부착 — 전기 결선 무개조
  - (b) EPS 의 CAN 조향 지령 기능 유무 확인 — 파라미터 변경이 필요하면 CLARK 승인
  - (c) 스텝모터 신호 모사기 — 가장 어렵다
- 13p CLARK 질문에 "조향 입력 방식과 대체 방법"을 추가할 것을 권한다(§3).

### 2-4. [중대] 밸브(K4 + AO) — 도면상 성립하기 어렵고 CAN 경로와 겹친다

- 5p ① "유압: CAN SWITCH 경유" 와 ② "밸브: CREVIS IO + K4" 가 한 문서에 함께 있다 → 유압 지령 경로가 2개다.
- **도면** ✓ (p1 E3–B2): MHYRIO 출력은 밸브 11개(PR1·PR2·PR3·S1–S4·SV1–SV4)와 경보 릴레이 1개다. 코일 (+) 공통선 8개(C2·C5·C8·C13·C16·C17·C18·C20)와 (−) 개별선 12개다. → K4 "1개"가 아니라 20극 수준의 절환이 필요하다. 코일 정격은 24V(시스템 48V)다.
- ⚠:
  - AO(전압 지령)로는 코일 전류를 구동할 수 없다(v4 도 앰프 TBC).
  - MHYRIO 에서 코일을 떼면 단선 검출 알람이 날 수 있다.
  - 밸브만 열고 펌프(ACE2 PUMP) 회전 지령이 없으면 상승은 안 되고 하강만 된다 — 위험한 쪽으로 기운다.
- **제안**: K4·밸브 AO 를 삭제하고 유압은 CAN(TILLER 대체) 경로 하나로 통일한다. 6p 그림·9p 매핑표를 함께 고친다.

### 2-5. [주요] CREVIS 신호 레벨·기준 전위·절연

**도면** ✓
- FWD/REV A4 = KEY OUT 48V 를 버튼으로 넣는 입력 (p1 E8, B5)
- SEAT A6 · ACC. ENABLE A13 = −BATT 로 당기는 입력 (p1 C8)
- ACC POTI = PPOT(+12) A2 / CPOT A3 / −BATT A9 의 3선 (p1 B7)

**datasheet** ✓: RSD-60L-24 는 입력–출력 절연(I/P-O/P 4KVDC)이다 [page 2](../../../References/meanwell/rsd-60/RSD-60-SPEC.pdf) → 24V 계통(PC·IO)은 배터리와 전기적으로 떠 있다.

**문제** ⚠
- 24V DO 로 48V 레벨 입력(A4)을 구동하면 입력 문턱이 맞는지 알 수 없다.
- AO 를 CPOT 에 넣으려면 AO 기준을 −BATT(A9)에 묶어야 한다 → 절연된 24V 계통이 배터리 − 와 이어진다. 11p 의 "배터리 계통 floating 유지" 와 함께 접지 설계를 정의해야 한다.

**제안**
- 디지털 입력(A4·A6·A13·A10·PUMP A13)에는 DO 전압을 넣지 말고, **릴레이 무전압 접점으로 원래 전원(KEY OUT 48V 또는 −BATT)을 그대로 스위칭**한다. 레벨과 기준 전위가 원 신호와 같아지고 "ZAPI 무변경" 원칙에도 맞는다.
- 가속은 절연형 AO, 또는 PPOT 에 비례하는(ratiometric) 출력 회로로 만든다 ⚠.
- 절환 릴레이는 저전류 신호용 접점(금도금 등)으로 고른다 ⚠.

### 2-6. [주요] 절환 릴레이 코일 구동 논리가 문서 안에서 모순

- 9p: "K1–K4 코일은 MODE 키 스위치 신호로 구동 — 무여자 시 MANUAL"
- 7p·8p: "PC HEARTBEAT 손실 → 릴레이 무여자 → MANUAL 측 복귀"
- → 코일이 키 스위치로만 구동되면 하트비트를 잃어도 무여자가 되지 않는다. 코일 경로에 감시 접점(게이트웨이 워치독 또는 Safety PLC)을 직렬로 넣어야 한다.
- FAULT 시 목표가 "MANUAL 복귀"인지 "정지"인지 정해야 한다. 무인 상태에서 MANUAL 로 돌아가면 페달 0·데드맨 열림이 되어 결과적으로 정지하는 구조인지, §2-2 와 함께 확정한다 ⚠.
- 릴레이를 하나씩 절환하면 일부만 AUTO 인 혼합 상태가 생길 수 있다 → 강제가이드 접점·접점 상태 피드백을 검토한다 ⚠. 절환은 정지·LC 개방 상태에서만 허용한다(8p "정지 시 전환(안)" 유지).

### 2-7. [주요] CAN 스위치 — TILLER 는 버스 중간 분기, 송신 메시지 전부 대체 필요

- **도면** ✓ (p1 E4): TILLER 는 버스 중간에서 분기(EA6D/EA14D)한다. 종단은 EPS·MHYRIO 양 끝이다.
- 게이트웨이를 넣으면 TILLER 분기를 잘라 별도 구간으로 만들게 된다 → 그 구간 양끝에도 종단이 필요하다(v4 10p ② 에 반영됨).
- **도면** ✓ (p1 E4–B3): TILLER 는 조이스틱 4축 외에 디지털·센서 입력 11점(DI1·DI2·6 FUNC.PB·HYD FILTER·SS CENTER·FLS(OPT)·BATT_REMOVER·SS CENT.·FLS(N.O)·REACH SPEED 1/2)을 받는다.
- AUTO 에서 TILLER 를 "차단"하면 이 정보도 끊긴다 ⚠. 대응은 둘 중 하나다:
  - PC 가 TILLER 송신 전부(입력 상태·노드 감시 메시지 포함)를 대체한다.
  - 조이스틱 신호만 치환하고 나머지는 통과시킨다.
  - 끊긴 채 두면 다른 노드에서 통신 이상 알람이 날 수 있다 ⚠.
- **워치독**: PC 가 죽으면 게이트웨이가 마지막 프레임을 반복하지 않고 중립(0) 프레임을 내보내거나 전부 차단해야 한다 — 하강 지령이 남아 있는 상황을 막기 위해서다 ⚠. 8p FAULT 정의에 명시한다.
- ZAPI 핸드셋(CAN ENCODER D 커넥터) 진단·플래시 트래픽을 통과시키는 조건도 게이트웨이 사양에 넣는다.

### 2-8. [주요] Safety PLC 와 MANUAL 모드

- "모드 스위치와 연결 없음"이면 MANUAL(유인 운전) 중에도 Safety LiDAR·Bumper 가 차량을 세운다 → 랙 근처 작업에서 오정지가 잦을 수 있다 ⚠.
- 반대로 MANUAL 에서 무효화하려면 모드 신호가 안전 입력이 되어야 한다(이중 채널 키 스위치 등).
- 주행 속도에 따라 보호필드를 바꾸지 않고 고정 필드를 쓰면 최고속 제동거리 기준의 큰 필드가 필요하다 ⚠ → 안전 속도 입력을 둘지 결정한다.
- Safety PLC 전원 출처·퓨즈가 정해지지 않았다. 전원을 잃으면 출력이 열려 정지(페일세이프)하도록 설계하면 MANUAL 도 멈춘다 → 의도로 명시한다.

### 2-9. [주요] DC-DC 전원 인입·용량

- **datasheet** ✓ [page 2, page 7](../../../References/meanwell/rsd-60/RSD-60-SPEC.pdf):
  - RSD-60L-24: 입력 18~72VDC 연속, 출력 24V / 2.5A / 60W
  - 입력 전압에 따른 감액은 5V 모델만 해당하고 24V 모델은 전 범위 100% 부하
  - 주위온도가 55℃ 를 넘으면 감액(70℃ 에서 60%, page 2·7)
  - UL 62368-1 approved, I/P-O/P 4KVDC
  - → 48V 배터리 입력 범위에는 맞는다 ✓. 다만 배터리 실측 최고(충전 중)·최저 전압은 확인한다 ⚠.
- **인입 지점**: 5p 그림은 BATTERY 에서 직결로 그려져 있어 인입 지점·퓨즈·키 연동이 정해지지 않았다.
  - 상시 버스에 전용 퓨즈를 추가하고, 키/메인 릴레이 연동 여부(키 OFF 시 암전류)를 정한다.
  - LC 뒤(300A 동력단, p1 E12–A11)에 물리면 보호정지 때마다 PC 가 꺼진다 ✓(결선).
- **용량** ⚠: 산업용 PC + 3D LiDAR + 카메라 + Safety LiDAR + HMI(Human-Machine Interface) + IO + Safety PLC 를 60W 로 감당하기 어려울 수 있다 → 10p "부하 합계 TBC" 를 1순위로 부하표를 만든다.

---

## 3. 13p 검토 질문 추가 권고

**CLARK USA**
- ⑦ FWD/REV 단일 입력(A4)의 동작 방식(누를 때 토글/누르는 동안 유지)과 SES 동일 여부
- ⑧ 조향 입력(스텝모터)의 대체 방법 — EPS 의 CAN 조향 지령 지원 여부
- ⑨ AUTO 에서 ACC. ENABLE·SEAT·DEAD MAN·PEDAL BRAKE 를 대체할 때 허용되는 방식
- ⑩ 외부 안전정지 삽입 지점으로 P1/P2 경로를 써도 되는지, 유압 하강 정지 방법
- ⑪ TILLER CAN 메시지를 대체할 때 다른 노드의 노드 감시(통신 타임아웃) 동작

**인증 컨설턴트**
- ⑥ 운전자 감지(DEAD MAN·SEAT) 우회를 안전기능으로 분류할지, 요구 PL(Performance Level)
- ⑦ MANUAL 모드에서 Safety LiDAR·Bumper 처리(무효화 허용 여부와 조건)

---

## 4. 문서 형식

- 각 쪽 하단 "참조 도면" 꼬리말은 좋다. 도면이 **Sheet 2 of 2** 라는 점과 표제 모델 **SRX14/16** 을 함께 적기를 권한다.
- 7p 하단의 "IPC·모드 스위치·CREVIS IO 와 연결 없음" 원칙은 §2-2·§2-8 결정 뒤에 갱신한다.
- 12p 적용 규격에 ANSI/ITSDF B56.1(유인 지게차 기본 규격, 개조 관련 조항 포함 여부) 검토를 권한다 ⚠ — 원문 미확인.

---

## 5. 검증 기록

- **직접 판독 구역** (300 DPI 원본 확대): 동력·LC·EPS 퓨즈(F12–A9), 퓨즈박스·키 체인(L12–J6), TRACTION 커넥터(E8–B7), EPS AC0(H8–F6), 데드맨 라인(F8–E7), PUMP(E6–B5), CAN TILLER·조이스틱(E5–B3), MHYRIO(E3–B1), CAN ENCODER·종단(G4–E2), PIN CODE·DISPLAY(G6–G5)
- **datasheet**: 제조사 PDF 를 `References/meanwell/rsd-60/` 에 보관하고 `pdftotext` 변환본을 함께 두었다. 사양표(page 2), 감액 곡선(page 7, 렌더 이미지로 확인).
- **남은 ⚠** — 실차·OEM 자료로 확인할 것:
  1. ZAPI 입력 문턱·알람 반응(A4·A6·A10·A13·PUMP A13)
  2. 스텝모터 조향 신호 형태
  3. 유압 하강의 펌프 의존 여부
  4. CAN 종단 실측(60Ω)
  5. TILLER 메시지 정의·노드 감시
  6. PIN CODE 선 색
  7. 메인 퓨즈 300A/350A
  8. 배터리 전압 범위
  9. 24V 부하 합계
  10. SES 실제 도면과의 차이 전부
