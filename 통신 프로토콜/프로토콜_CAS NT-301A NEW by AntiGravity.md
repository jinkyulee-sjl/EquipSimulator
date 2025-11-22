# CAS NT-301A NEW 통신 프로토콜

## 1. 통신 사양 (Communication Specifications)

*   **인터페이스 (Interface)**:
    *   RS-232C (Standard)
    *   Current Loop (Standard)
    *   RS-422 / RS-485 (Option)
*   **전송 속도 (Baud Rate)**: 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 76800, 115200 bps (F31)
*   **데이터 비트 (Data Bits)**: 8 bits
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
| 1 | RXD | Current Loop Input |
| 2 | RXD | Current Loop Input |

## 3. 데이터 포맷 (Data Format)

### Format 1 (18 Bytes) - F35=0 or 1
```
[Header1(2)][,][Header2(2)][,][Data(8)][Unit(2)][CR][LF]
```
*   **Header 1**: `OL` (Overload), `ST` (Stable), `US` (Unstable)
*   **Header 2**: `NT` (Net Weight), `GS` (Gross Weight)
*   **Data**: 8자리 (부호, 소수점 포함). 예: `+000.190`
*   **Unit**: `kg`, `g_`

### Format 2 (22 Bytes) - F35=2 (CAS Format)
```
[Header1(2)][,][Header2(2)][,][Lamp(1)][Data(8)][Space(1)][Unit(2)][CR][LF]
```
*   **Header 1**: `OL`, `ST`, `US`
*   **Header 2**: `NT`, `GS`
*   **Lamp**: 1 byte status (Bit mapped: Stable, Hold, Print, Gross, Tare, Zero)
*   **Data**: 8자리 (부호, 소수점 포함)
*   **Unit**: `kg`, `g_`

## 4. 명령어 목록 (Command List)

### 단순 명령 모드 (Simple Command Mode) - F33=5
장비번호(`dd`)는 2자리 ASCII (예: 01 -> `30h 31h`)

| Command | Description | Response |
| :--- | :--- | :--- |
| **dd RW** | 중량 데이터 요청 | 설정된 포맷으로 데이터 전송 |
| **dd MZ** | 영점 (Zero) | `dd MZ` Echo |
| **dd MT** | 용기 (Tare) | `dd MT` Echo |
| **dd PN 00** | 품번 변경 (01~99) | `dd PN 00` Echo |

### 복합 명령 모드 (Complex Command Mode) - F33=1
Format: `[STX][ID(2)][COMMAND(4)][BCC(2)][ETX]` (BCC 사용 시)
Response: `[STX][ID(2)][COMMAND(4)][ACK][BCC(2)][ETX]`

| Command | Description |
| :--- | :--- |
| **RCWT** | 현재 중량 요청 |
| **WZER** | 영점 (Zero) |
| **WTAR** | 용기 (Tare) |
| **WTRS** | 용기 리셋 |
| **WPRT** | 프린트 실행 |
| **RGRD** | 총계 데이터 요청 |
| **RSUB** | 소계 데이터 요청 |
| **WTIM + HHMMSS(6)** | 시간 변경 |
| **WDAT + YYMMDD(6)** | 날짜 변경 |
| **WCNO + 코드값(6)** | 코드 변경 |
| **WPNO + 품번값(2)** | 품번 변경 |

* 복합 명령에 대한 회신
    - 현재 중량 요청에 대한 회신 :
     "TX(1) ID(2) 명령어(4) 상태1(2) 상태2(2) 부호(1) 중량(소수점포함)(7) 단위(2) ACK(1) ETX(1)"
     총 23 바이트 (BCC 사용 안하는 경우)
