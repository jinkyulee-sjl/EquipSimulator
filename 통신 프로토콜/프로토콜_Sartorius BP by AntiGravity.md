# Sartorius BP Series 통신 프로토콜

## 1. 통신 사양 (Communication Specifications)

*   **인터페이스 (Interface)**: RS-232C-S / V24-V28
*   **전송 속도 (Baud Rate)**: 150, 300, 600, 1200, 2400, 4800, 9600, 19200 bps
*   **데이터 비트 (Data Bits)**: 7 bits
*   **패리티 (Parity)**: Even, Odd, Mark, Space (기본값: Even)
*   **스톱 비트 (Stop Bit)**: 1 bit 또는 2 bits (기본값: 1 bit)
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
| 6 | - | - | Internally Connected |
| 7 | GND | - | Internal Ground |
| 8 | GND | - | Internal Ground |
| 12 | Reset_Out | Output | Hardware restart |
| 14 | GND | - | Internal Ground |
| 20 | DTR | Output | Data Terminal Ready |
| 21 | GND | - | Internal Ground |

## 3. 데이터 포맷 (Data Format)

데이터 출력은 기본적으로 16문자 포맷을 사용합니다. (ID 코드가 포함된 경우 22문자)

### 기본 포맷 (16 Characters)
```
[Sign(1)][Space/Digit(10)][Unit(3)][CR][LF]
```
*   **Sign**: `+`, `-`, 또는 ` ` (space)
*   **Data**: 우측 정렬, 빈칸은 공백, 소수점 포함
*   **Unit**: 단위 (예: `g__`, `kg_`)
*   **CR LF**: Terminator

### 예시
```
+    123.45 g  [CR][LF]
```

### 특수 상태 코드 (Special Codes)
데이터 대신 상태 코드가 출력될 수 있습니다. (1~4번째 문자)
*   `Stat`: 상태 코드 시작
*   `High`: Overload (과부하)
*   `Low`: Underload (부하 부족)

## 4. 명령어 목록 (Command List)

명령어는 `ESC` (ASCII 27) 문자로 시작하며, `CR LF`로 종료합니다.

### 제어 명령어 (Control Commands)
| Command | ASCII Code | Description |
| :--- | :--- | :--- |
| **ESC P** | 27 80 | 프린트 (Print) / Auto Print 활성화/비활성화 |
| **ESC T** | 27 84 | 용기/영점 (Tare/Zero) |
| **ESC K** | 27 75 | 환경 설정: 매우 안정 (Very stable) |
| **ESC L** | 27 76 | 환경 설정: 안정 (Stable) |
| **ESC M** | 27 77 | 환경 설정: 불안정 (Unstable) |
| **ESC N** | 27 78 | 환경 설정: 매우 불안정 (Very unstable) |
| **ESC O** | 27 79 | 키 잠금 (Block keys) |
| **ESC R** | 27 82 | 키 잠금 해제 (Release keys) |
| **ESC S** | 27 83 | 재시작 (Restart / Self-test) |
| **ESC Z** | 27 90 | 내부 캘리브레이션 (Internal Calibration) |

### 기타 명령어
*   **ESC x 1 _**: 모델명 출력
*   **ESC x 2 _**: 시리얼 번호 출력
