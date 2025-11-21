# CAS NT-302A 통신 프로토콜

## 1. 통신 사양 (Communication Specifications)

*   **인터페이스 (Interface)**:
    *   RS-232C (Standard)
    *   Current Loop (Standard)
    *   RS-422 / RS-485 (Option)
*   **전송 속도 (Baud Rate)**: 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 76800, 115200 bps (F31)
*   **데이터 비트 (Data Bits)**: 7 or 8 bits
*   **패리티 (Parity)**: None, Odd, Even (F30)
*   **스톱 비트 (Stop Bit)**: 1 bit
*   **코드 (Code)**: ASCII

## 2. 핀 배열 (Pin Assignment)

### RS-232C (9 Pin D-Sub Connector)
| Pin No. | Signal | Description |
| :--- | :--- | :--- |
| 2 | RXD | Receive Data |
| 3 | TXD | Transmit Data |
| 5 | GND | Ground |

### Current Loop
| Pin No. | Signal | Description |
| :--- | :--- | :--- |
| 1 | 20mA | Current Loop Output (High) |
| 2 | 0mA | Current Loop Output (Low) |

## 3. 데이터 포맷 (Data Format)

### Format 1 (18 Bytes) - F35=0 or 1
```
[Header1(2)][,][Header2(2)][,][Data(8)][Unit(2)][CR][LF]
```
*   **Header 1**: `OL` (Overload), `ST` (Stable), `US` (Unstable)
*   **Header 2**: `NT` (Net Weight), `GS` (Gross Weight)
*   **Data**: 8자리 (부호, 소수점 포함). 예: `+000.190`
*   **Unit**: `kg`

### Format 2 (22 Bytes) - F35=2 (CAS Format)
```
[Header1(2)][,][Header2(2)][,][Lamp(1)][Data(8)][Space(1)][Unit(2)][CR][LF]
```
*   **Header 1**: `OL`, `ST`, `US`
*   **Header 2**: `NT`, `GS`
*   **Lamp**: 1 byte status (Bit mapped: Stable, Hold, Print, Gross, Tare, Zero)
*   **Data**: 8자리 (부호, 소수점 포함)
*   **Unit**: `kg`

## 4. 명령어 목록 (Command List)

*   **Command Mode** (F33=1)가 지원되나, 매뉴얼 상에 상세 명령어 리스트가 명시되어 있지 않음.
*   일반적으로 CAS 표준 프로토콜(`RW`, `MZ`, `MT` 등)을 따를 가능성이 높음.
