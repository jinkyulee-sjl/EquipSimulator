# Sartorius CPA Series 통신 프로토콜

## 1. 통신 사양 (Communication Specifications)

*   **인터페이스 (Interface)**: RS-232C-S / V24-V28
*   **전송 속도 (Baud Rate)**: 150, 300, 600, 1200, 2400, 4800, 9600, 19200 bps
*   **데이터 비트 (Data Bits)**: 7 bits
*   **패리티 (Parity)**: Even, Odd, Mark, Space
*   **스톱 비트 (Stop Bit)**: 1 bit 또는 2 bits
*   **핸드쉐이크 (Handshake)**: Software (XON/XOFF), Hardware (CTS/DTR)
*   **터미네이터 (Terminator)**: CR LF (CR: 0Dh, LF: 0Ah)

## 2. 핀 배열 (Pin Assignment)

D-Sub 25 pin Female Connector (DB25S)

| Pin No. | Signal Name | Direction | Description |
| :--- | :--- | :--- | :--- |
| 1 | Signal Ground | - | Signal Ground |
| 2 | TxD | Output | Data Output |
| 3 | RxD | Input | Data Input |
| 4 | GND | - | Internal Ground |
| 5 | CTS | Input | Clear to Send |
| 7 | GND | - | Internal Ground |
| 8 | GND | - | Internal Ground |
| 12 | Reset_Out | Output | Hardware restart |
| 14 | GND | - | Internal Ground |
| 20 | DTR | Output | Data Terminal Ready |

## 3. 데이터 포맷 (Data Format)

데이터 출력은 16문자 포맷 또는 22문자 포맷(ID 포함)을 사용합니다.

### 기본 포맷 (16 Characters)
```
[Sign(1)][Space(1)][Data(8)][Space(1)][Unit(3)][CR][LF]
```
*   **Pos 1 (Sign)**: `+`, `-`, 또는 ` ` (space)
*   **Pos 2**: Space 또는 Bracket `[` (Non-verified digits)
*   **Pos 3-10 (Data)**: 계량 데이터 (8자리), 우측 정렬, 빈칸은 공백, 소수점 포함
*   **Pos 11**: Space 또는 Bracket `]`
*   **Pos 12-14 (Unit)**: 단위 (예: `g__`, `kg_`)
*   **Pos 15**: CR
*   **Pos 16**: LF

### ID 포함 포맷 (22 Characters)
기본 포맷 앞에 6자리의 ID 코드가 추가됩니다.
```
[ID(6)][Sign(1)][Space(1)][Data(8)][Space(1)][Unit(3)][CR][LF]
```
*   **Pos 1-6 (ID)**: ID 코드 (예: `Stat__`, `N_____`)

### 예시
```
+  123.56 g  [CR][LF]  (16 char)
N     +  123.56 g  [CR][LF]  (22 char)
```

### 상태 및 에러 코드 (Special & Error Codes)
*   **Stat H**: Overload (과부하)
*   **Stat L**: Underload (부하 부족)
*   **Err ###**: 에러 코드 (예: `Err 01`, `Err 02`)

## 4. 명령어 목록 (Command List)

명령어는 `ESC` (ASCII 27) 문자로 시작하며, `CR LF`로 종료합니다.

### 포맷 1: `ESC` + `Command` + `CR` + `LF`
| Command | Description |
| :--- | :--- |
| **ESC P** | 프린트 (Print) / Auto Print 활성화/비활성화 |
| **ESC T** | 용기/영점 (Tare/Zero) |
| **ESC K** | 환경 설정: 매우 안정 (Very stable) |
| **ESC L** | 환경 설정: 안정 (Stable) |
| **ESC M** | 환경 설정: 불안정 (Unstable) |
| **ESC N** | 환경 설정: 매우 불안정 (Very unstable) |
| **ESC O** | 키 잠금 (Block keys) |
| **ESC R** | 키 잠금 해제 (Release keys) |
| **ESC S** | 재시작 (Restart / Self-test) |
| **ESC Z** | 내부 캘리브레이션 (Internal Calibration) |

### 포맷 2: `ESC` + `Command` + `#` + `_` + `CR` + `LF`
| Command | Description |
| :--- | :--- |
| **ESC f 0 _** | Function key (F) |
| **ESC f 1 _** | Function key (CAL) |
| **ESC s 3 _** | Clear Function key (CF) |
| **ESC x 0 _** | 내부 캘리브레이션 수행 |
| **ESC x 1 _** | 모델명 출력 |
| **ESC x 2 _** | 시리얼 번호 출력 |
