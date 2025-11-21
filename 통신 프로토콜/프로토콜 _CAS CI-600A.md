# 명령어 모드 1 (현재 상지 하이텍에서 사용 중인 모드)

## 무게 데이터 요구 (6 bytes) 명령

   dd    (2 bytes) : // 장비 번호 
   RW    (2 bytes) : // Command
   CR LF (2 bytes) : //

## 무게 데이터 요구 명령에 대한 회신 : FORMAT 1 (카스의 22 바이트) 

   HDR1    (2 bytes) // US : 불안정,  ST : 안정,  OL : 과부하
   '.'     (1 byte) 
   HDR2    (2 bytes) // GS : 총중량, NT : 순중량
   '.'     (1 byte)
   장비번호 (1 byte) // 장비번호는 변환모드 F20 에서 설정
   램프상태 (1 byte) // Bt7(1), Bt6(안정), Bt5(1), Bt4(홀드), Bt3(프린트), Bt2(순중량), Bt1(용기), Bt0(영점))
   '.'     (1 byte)
   DATA    (8 bytes)
   SPACE   (1 byte)
   UNIT    (2 bytes) // kt/t
   CR LF   (2 bytes)

## 무게 데이터 요구 명령에 대한 회신 : FORMAT 2 (카스의 10 바이트)

   DATA    (8 bytes)
   CR LF   (2 bytes)

## 무게 데이터 요구 명령에 대한 회신 : FORMAT 3 (18 바이트 AND, FINE)

   HDR1    (2 bytes) // US : 불안정,  ST : 안정,  OL : 과부하
   '.'     (1 byte) 
   HDR2    (2 bytes) // GS : 총중량, NT : 순중량
   '.'     (1 byte)
   DATA    (8 bytes)
   UNIT    (2 bytes) // kt/t
   CR LF   (2 bytes)

## ZERO (6 bytes) 명령

   dd    (2 bytes) : // 장비 번호 
   MZ    (2 bytes) : // Command
   CR LF (2 bytes) : //

## ZERO 명령에 대한 회신

   dd    (2 bytes) : // 장비 번호 
   MZ    (2 bytes) : // Command
   CR LF (2 bytes) : //

## TATE (6 bytes) 명령

   dd    (2 bytes) : // 장비 번호 
   MT    (2 bytes) : // Command
   CR LF (2 bytes) : //

## TARE 명령에 대한 회신

   dd    (2 bytes) : // 장비 번호 
   MT    (2 bytes) : // Command
   CR LF (2 bytes) : //

## 명령을 수행하지 못하였을 경우의 회신

   '!'   (1 byte)
   CR LF (2 bytes)
                   
## 명령이 잘못되었을 경우의 회신

   '?'   (1 byte)
   CR LF (2 bytes)
                   
# 명령어 모드 2 <NT-570 Command>

   추후 구현 예정 

# 명령어 모드 3 <CI-5000>

   추후 구현 예정 

# 구현 해야될 기능

## 데이터 포맷 선택

## ZERO 명령에 대한 처리

## TATE 명령에 대한 처리    

