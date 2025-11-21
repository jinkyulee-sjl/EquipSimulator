# AND GP Series 통신 프로토콜

## 1. 통신 사양 (Communication Specifications)

*   **전송 방식 (Transmission System)**: EIA RS-232C
*   **전송 형태 (Transmission Form)**: 비동기식, 양방향, 반이중 (Asynchronous, bi-directional, half duplex)
*   **전송 속도 (Baud Rate)**: 600, 1200, 2400, 4800, 9600, 19200 bps (기본값: 2400 bps)
*   **데이터 비트 (Data Bits)**: 7 bits 또는 8 bits (기본값: 7 bits)
*   **패리티 (Parity)**: Even, Odd (Data bits 7일 때) / None (Data bits 8일 때) (기본값: Even)
*   **스톱 비트 (Stop Bit)**: 1 bit
*   **코드 (Code)**: ASCII
*   **터미네이터 (Terminator)**: CR LF (CR: 0Dh, LF: 0Ah)

## 2. 핀 배열 (Pin Assignment)

D-Sub 25 pin 커넥터 (DCE)

| Pin No. | Signal Name | Direction | Description |
| :--- | :--- | :--- | :--- |
| 1 | FG | - | Frame Ground |
| 2 | RXD | Input | Receive Data |
| 3 | TXD | Output | Transmit Data |
| 4 | RTS | Input | Ready to Send |
| 5 | CTS | Output | Clear to Send |
| 6 | DSR | Output | Data Set Ready |
| 7 | SG | - | Signal Ground |
| 18 | PRINT | Input | External contact input (Same as PRINT key) |
| 19 | RE-ZERO | Input | External contact input (Same as RE-ZERO key) |

## 3. 데이터 포맷 (Data Format)

### A&D Standard Format
*   **길이**: 터미네이터(CR LF)를 제외하고 15문자
*   **구조**:
    ```
    [Header(2)][,][Data(9)][Unit(3)][Terminator(2)]
    ```
    *   **Header**: 데이터의 상태를 나타내는 2문자
        *   `ST`: Stable (안정)
        *   `US`: Unstable (불안정)
        *   `OL`: Overload (과부하, 범위 초과)
    *   **Data**: 부호 포함 9문자 (우측 정렬, 빈칸은 공백, 소수점 포함)
        *   예: `+0012.345`
    *   **Unit**: 단위 3문자
        *   `_g_`: gram (스페이스 g 스페이스)
        *   `kg_`: kilogram
        *   `pcs`: pieces
    *   **Terminator**: CR LF

## 4. 명령어 목록 (Command List)

명령어는 대문자로 전송하며, 터미네이터(CR LF)를 붙여야 합니다.

### 데이터 요청 명령어 (Query Weighing Data)
| Command | Description |
| :--- | :--- |
| **Q** | 즉시 계량 데이터 요청 (Requests the weighing data immediately) |
| **S** | 안정 시 계량 데이터 요청 (Requests the weighing data when stabilized) |
| **SI** | 즉시 계량 데이터 요청 (Requests the weighing data immediately) |
| **SIR** | 연속 계량 데이터 요청 (Requests the weighing data continuously) |
| **C** | S 또는 SIR 명령어 취소 (Cancels the S or SIR command) |

### 제어 명령어 (Control Balance)
| Command | Description |
| :--- | :--- |
| **CAL** | 캘리브레이션 수행 (Same as CAL key) |
| **OFF** | 디스플레이 끄기 (Turns the display off) |
| **ON** | 디스플레이 켜기 (Turns the display on) |
| **P** | 디스플레이 켜기/끄기 토글 (Same as ON:OFF key) |
| **PRT** | 프린트 수행 (Same as PRINT key) |
| **R** | 영점 수행 (Same as RE-ZERO key) |
| **SMP** | 샘플링 수행 (Same as SAMPLE key) |
| **U** | 모드 변경 (Same as MODE key) |

### 설정 및 메모리 명령어 (Settings & Memory)
| Command | Description |
| :--- | :--- |
| **UN:mm** | 단위 질량 메모리 호출 (mm: 01-50) |
| **?UN** | 메모리된 단위 질량 번호 요청 |
| **UW:******. * g** | 단위 질량 값 변경 (예: `UW:+002000.0 g`) |
| **?UW** | 단위 질량 값 요청 |
| **CN:mm** | 상/하한값 메모리 호출 (mm: 01-20) |
| **?CN** | 선택된 상/하한값 코드 번호 요청 |
| **HI:******. * g** | 상한값 설정 (예: `HI:+002000.0 g`) |
| **LO:******. * g** | 하한값 설정 (예: `LO:+001000.0 g`) |
| **?HI** | 상한값 요청 |
| **?LO** | 하한값 요청 |
| **PN:mm** | 용기(Tare) 값 메모리 호출 (mm: 01-20) |
| **?PN** | 선택된 용기 번호 요청 |
| **PT:******. * g** | 용기 값 설정 (예: `PT:+001000.0 g`) |
| **?PT** | 용기 값 요청 |
| **MCL** | 모든 메모리 데이터 삭제 |
| **MD:nnn** | 데이터 번호 nnn 삭제 |
| **?MA** | 메모리의 모든 계량 데이터 출력 |
| **?MQnnn** | 데이터 번호 nnn의 데이터 출력 |
| **?MX** | 메모리의 데이터 개수 출력 |

## 5. 응답 코드 (Acknowledge & Error Codes)

`Serial interface function (5if)` 파라미터가 `erCd 1`로 설정된 경우:

*   **<AK> (06h)**: 명령어가 정상적으로 수신 및 수행됨 (Acknowledge)
*   **EC, Exx**: 에러 코드 (명령어 수행 불가 또는 통신 에러)
    *   `EC, E01`: Undefined command (정의되지 않은 명령어)
    *   `EC, E02`: Not ready (준비되지 않음)
    *   `EC, E03`: Timeout (타임아웃)
    *   `EC, E04`: Excess characters (문자 초과)
    *   `EC, E06`: Format error (포맷 에러)
    *   `EC, E07`: Parameter setting error (파라미터 설정 에러)
    *   `EC, E11`: Stability error (안정 에러)
    *   `EC, E20`: Calibration weight error (분동 에러)
    *   `EC, E21`: Calibration weight error (분동 에러)
