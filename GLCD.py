import RPi.GPIO as GPIO
import time

RS_p = 7
RW_p = 8
E_p = 9
CS1_p = 18
CS2_p = 19
DATA_p = [0] * 8
SetPg = 0
SetCol = 0

def __main():
    PinsInit(20, 7, 8, 9, 18, 19, 10, 11, 12, 13, 14, 15, 16, 17)
    GLCDInit()
    GLCDDisplayClear()
    SelectIC(2)
    SetPage(7)
    SetAddress(63)
    WriteData(0xFF)
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        GPIO.cleanup()

def PinsInit(rst, rs, rw, enable, cs1, cs2, d0, d1, d2, d3, d4, d5, d6, d7):
    GPIO.setmode(GPIO.BCM)

    #データピンの番号セット
    DATA_p[0] = d0
    DATA_p[1] = d1
    DATA_p[2] = d2
    DATA_p[3] = d3
    DATA_p[4] = d4
    DATA_p[5] = d5
    DATA_p[6] = d6
    DATA_p[7] = d7
    #制御ピンの番号をセット
    RS_p = rs
    RW_p = rw
    E_p = enable
    CS1_p = cs1
    CS2_p = cs2
    #指定の制御ピンをデジタル出力に設定
    GPIO.setup(RS_p, GPIO.OUT)
    GPIO.setup(RW_p, GPIO.OUT)
    GPIO.setup(E_p, GPIO.OUT)
    GPIO.setup(CS1_p, GPIO.OUT)
    GPIO.setup(CS2_p, GPIO.OUT)
    #指定のデータピンをデジタル出力に設定
    for i in range(8):
        GPIO.setup(DATA_p[i], GPIO.OUT)
    #信号線をLOWに設定しておく
    GPIO.output(RS_p, GPIO.LOW)
    GPIO.output(RW_p, GPIO.LOW)
    GPIO.output(E_p, GPIO.LOW)
    GPIO.output(CS1_p, GPIO.LOW)
    GPIO.output(CS2_p, GPIO.LOW)
    #LCDモジュールのリセットを解除する
    GPIO.setup(rst, GPIO.OUT)
    GPIO.output(rst, GPIO.HIGH)

def GLCDInit():
    #30ms待機
    time.sleep(0.03)
    #左側ICを初期化
    SelectIC(1)
    command(0xC0, GPIO.LOW)
    command(0x3F, GPIO.LOW)
    #左側ICを初期化
    SelectIC(2)
    command(0xC0, GPIO.LOW)
    command(0x3F, GPIO.LOW)

def GLCDDisplayClear():
    for i in [1, 2]:
        SelectIC(i)
        for y in range(8):
            SetPage(y)
            SetAddress(0)
            for x in range(64):
                WriteData(0)

def SelectIC(value):
    if value == 1:
        GPIO.output(CS1_p, GPIO.HIGH)
        GPIO.output(CS2_p, GPIO.LOW)
    else:
        GPIO.output(CS1_p, GPIO.LOW)
        GPIO.output(CS2_p, GPIO.HIGH)

def SetPage(value):
    command(0xB8|(value&0x07), GPIO.LOW)

def SetAddress(value):
    command(0x40|(value&0x3F), GPIO.LOW)

def WriteData(value):
    command(value, GPIO.HIGH)

def command(value, mode):
    GPIO.output(RS_p, mode)
    for i in range(8):
        GPIO.output(DATA_p[i], (value >> i) & 0x01)
    GPIO.output(E_p, GPIO.HIGH)
    GPIO.output(E_p, GPIO.LOW)

__main()


