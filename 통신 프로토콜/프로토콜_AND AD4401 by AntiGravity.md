# AND AD4401 통신 프로토콜

## 1. 통신 사양 (Communication Specifications)

*   **인터페이스 (Interface)**:
    *   Standard Serial Output (20mA Current Loop)
    *   OP-03 (RS-422/485)
    *   OP-04 (RS-232C)
*   **전송 속도 (Baud Rate)**: 600, 1200, 2400, 4800, 9600, 19200 bps
*   **데이터 비트 (Data Bits)**: 7 bits 또는 8 bits
*   **패리티 (Parity)**: Even, Odd, None
*   **스톱 비트 (Stop Bit)**: 1 bit 또는 2 bits
*   **터미네이터 (Terminator)**: CR 또는 CR LF
*   **코드 (Code)**: ASCII

## 2. 핀 배열 (Pin Assignment)

### OP-04 (RS-232C)
D-Sub 25 pin (Not included, user provided)
*   일반적인 RS-232C 핀맵을 따름 (TxD, RxD, SG 등). 매뉴얼에 상세 핀맵 그림은 없으나 표준 결선 권장.

## 3. 데이터 포맷 (Data Format)

### A&D Standard Format
```
[Header1(2)][,][Header2(2)][,][Data(8)][Unit(2)][Terminator]
```
*   **Header 1**:
    *   `ST`: Stable (안정)
    *   `US`: Unstable (불안정)
    *   `OL`: Overload (오버로드)
*   **Header 2**:
    *   `GS`: Gross Weight (총중량)
    *   `NT`: Net Weight (순중량)
    *   `TR`: Tare Value (용기중량)
*   **Data**: 8자리 (부호, 소수점 포함). 우측 정렬. 빈 자리는 Space(20h).
    *   예: `+00123.45`
*   **Unit**: 2자리 (예: `kg`, `g_`)
*   **Terminator**: CR LF 또는 CR

**예시**:
```
ST,GS,+0012345kg[CR][LF]  (Stable, Gross, 12345 kg)
US,NT,+0010000kg[CR][LF]  (Unstable, Net, 10000 kg)
OL,GS,+       .  kg[CR][LF]  (Overload, Gross)
```

### Accumulation Data Format
```
[Header(2)][,][Data(8)][Unit(2)][Terminator]
```
*   **Header**:
    *   `TW`: Total Weight (누적 중량)
    *   `TN`: Total Number (누적 횟수)

**예시**:
```
TW,+0123456.78kg[CR][LF]
TN,+0123456789  [CR][LF]
```

## 4. 명령어 목록 (Command List)

명령어 모드(Command Mode)에서 사용 가능합니다.

| Command | Name | Function |
| :--- | :--- | :--- |
| **RW** | Request Weight | 현재 중량 데이터 요청 (A&D Standard Format 응답) |
| **MZ** | Make Zero | 영점 처리 (Zero) |
| **MT** | Make Tare | 용기 처리 (Tare) |
| **CT** | Clear Tare | 용기 제거 (Tare Clear) |
| **MG** | Make Gross | 총중량(Gross) 모드로 전환 |
| **MN** | Make Net | 순중량(Net) 모드로 전환 |
| **BB** | Begin Batch | 배합(Batching) 시작 |
| **HB** | Halt Batch | 배합 비상 정지 |
| **BD** | Batch Discharged | 배출 시작 (Discharging) |
| **RF** | Request Final | 최종 결과(Weighing result) 요청 |
| **RT** | Request Total | 누적 데이터(Total) 요청 |
| **DT** | Delete Total | 누적 데이터 삭제 |
| **SS** | Set Setpoints | 설정값(Setpoint) 설정 |
| **RS** | Request Setpoint | 설정값(Setpoint) 요청 |

*   **응답 (Response)**:
    *   정상 수신 시: 명령어를 그대로 반송 (Echo)하거나 데이터 응답.
    *   에러 시: `IE` (Impossible), `VE` (Value Error), `?E` (Format Error).
