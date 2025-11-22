# CAS ED-H / EC-D 통신 프로토콜

## 1. 통신 사양 (Communication Specifications)

*   **인터페이스 (Interface)**: RS-232C
*   **전송 속도 (Baud Rate)**: 1200, 2400, 4800, 9600 bps (기본값: 9600)
*   **데이터 비트 (Data Bits)**: 8 bits
*   **패리티 (Parity)**: None
*   **스톱 비트 (Stop Bit)**: 1 bit
*   **코드 (Code)**: ASCII

## 2. 핀 배열 (Pin Assignment)

### RS-232C (9 Pin D-Sub Connector)
| Pin No. | Signal | Description |
| :--- | :--- | :--- |
| 2 | RXD | Input (Receive Data) |
| 3 | TXD | Output (Transmit Data) |
| 5 | GND | Signal Ground |

## 3. 데이터 포맷 (Data Format)

### Stream Mode (Continuous Output) - Au on
데이터는 22 Byte로 구성되며, CR(0Dh) LF(0Ah)로 끝납니다.

```
[HEAD1(2)][,][HEAD2(2)][,][DATA(8)][UNIT(4)][CR][LF]
```

*   **HEAD 1 (2 Bytes)**: 상태 정보
    *   `OL`: Overload (과부하)
    *   `ST`: Stable (안정)
    *   `US`: Unstable (불안정)
*   **HEAD 2 (2 Bytes)**: 모드 정보
    *   `NT`: Net Weight (순중량)
    *   `GS`: Gross Weight (총중량)
*   **DATA (8 Bytes)**: 중량 데이터 (부호, 소수점 포함)
    *   예: `+  100.0` (우측 정렬, 빈 공간은 공백)
    *   `2D(Hex)`: `-` (Minus)
    *   `20(Hex)`: ` ` (Space)
    *   `2E(Hex)`: `.` (Decimal Point)
*   **UNIT (4 Bytes)**: 단위
    *   `g   `: `20 67 20 20`
    *   `kg  `: `20 6B 67 20`
    *   `lb  `: `20 6C 62 20`
    *   `oz  `: `20 6F 7A 20`

**예시 (Example):**
*   안정, 총중량, +0.876g:
    `ST,GS,+  0.876 g  ` (CR LF)
*   불안정, 순중량, -1.568lb:
    `US,NT,-  1.568 lb  ` (CR LF)
*   과부하:
    `OL,NT,-------- oz  ` (CR LF)

## 4. 명령어 목록 (Command List)

PC에서 저울로 명령을 보낼 때 사용합니다. (Command Mode)

| Command (ASCII) | Hex | Description | 비고 |
| :--- | :--- | :--- | :--- |
| **L** 또는 **l** | 0x4C / 0x6C | 짐 0 (Load 0?) | Zero와 유사 기능 추정 |
| **C** 또는 **c** | 0x43 / 0x63 | 용기 (Tare) | 용기 설정 |
| **R** 또는 **r** | 0x52 / 0x72 | 순중량/총중량 전환 | Gross / Net 전환 |
| **U** 또는 **u** | 0x55 / 0x75 | 단위 변환 (Unit) | kg, g, lb 등 전환 |
| **M** 또는 **m** | 0x4D / 0x6D | M+ / Exit | 누적 또는 나가기 |
| **P** 또는 **p** | 0x50 / 0x70 | 인쇄 (Print) | 현재 중량 전송 요청 |
| **Z** 또는 **z** | 0x5A / 0x7A | 영점 (Zero) | 영점 잡기 |
| **T** 또는 **t** | 0x54 / 0x74 | 용기 (Tare) | 용기 설정 |
| **H** 또는 **h** | 0x48 / 0x68 | 홀드 (Hold) | 홀드 기능 |

> **참고**: 매뉴얼 상 `L`과 `Z`, `C`와 `T`가 유사한 기능으로 설명되어 있으나, 일반적으로 `Z`가 Zero, `T`가 Tare로 사용됩니다. `P` 명령 전송 시 현재 중량 데이터를 응답합니다.
