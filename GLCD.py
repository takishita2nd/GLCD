import RPi.GPIO as GPIO
import Font as Font
import time

RS_p = 7
RW_p = 8
E_p = 9
CS1_p = 18
CS2_p = 19
DATA_p = [0] * 8
SetPg = 0
SetCol = 0
EWAIT = 0.00003

def __main():
    PinsInit(20, 7, 8, 9, 18, 19, 10, 11, 12, 13, 14, 15, 16, 17)
    GLCDInit()
    GLCDDisplayClear()
    GLCDBox(0, 0, 127, 63)

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        GLCDDisplayClear()
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

def GLCDBox(Xp0, Yp0, Xp1, Yp1):
    for i in range(Xp0, Xp1 + 1):
        GLCDPutPixel(i, Yp0)
        GLCDPutPixel(i, Yp1)
    for i in range(Yp0 + 1, Yp1):
        GLCDPutPixel(Xp0, i)
        GLCDPutPixel(Xp1, i)

def GLCDPutPixel(Xp, Yp):
    #ラインの選択処理
    L = 1 << (Yp % 8)
    #LCDに表示するアドレスの位置をセットする
    SetLocation(Xp, Yp)
    #LCD画面の現在表示内容に指定位置のビット(L)をON(OR)させ、そのデータをLCDに送る
    L = ReadData() | L
    SetAddress(SetCol)
    WriteData(L)

def GLCDPuts(Xp, Yp, text):
    x = Xp
    for s in text:
        GLCDPutc(x, Yp, s)
        x += 6

def GLCDPutc(Xp, Yp, c):
    code = ord(c)
    #ページ内のラインを選択
    L = Yp % 8
    #８×５のキャラクター文字を描画する
    for i in range(5):
        SetLocation(Xp + i, Yp)
        f = Font.Array[code - 0x20][i] << L
        WriteData(f)
        if (L != 0) & (SetPg < 7):
            SetPage(SetPg + 1)
            SetAddress(SetCol)
            f = Font.Array[code - 0x20][i] >> (8 - L)
            WriteData(f)


def SetLocation(Xp, Yp):
    global SetPg
    global SetCol
    cs = 0
    #チップの選択とカラムのアドレスの処理を行う
    if Xp < 64:
        #左側(IC1)を選択
        cs = 1
        SetCol = Xp
    else:
        #右側(IC2)を選択
        cs = 2
        SetCol = Xp - 64
    #ページとラインの選択
    SetPg = Yp // 8
    #LCDに描画するアドレスの位置を設定
    SelectIC(cs)
    SetPage(SetPg)
    SetAddress(SetCol)

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

def ReadData():
    #データピンを入力に設定
    for i in range(8):
        GPIO.setup(DATA_p[i], GPIO.IN)
    #読み込みモードにする
    GPIO.output(RW_p, GPIO.HIGH)
    GPIO.output(RS_p, GPIO.HIGH)
    #データを読み込む
    GPIO.output(E_p, GPIO.HIGH)
    time.sleep(EWAIT)
    GPIO.output(E_p, GPIO.LOW)
    ans = 0
    GPIO.output(E_p, GPIO.HIGH)
    time.sleep(EWAIT)
    for i in range(8):
        ans = ans | (GPIO.input(DATA_p[i]) << i)
    GPIO.output(E_p, GPIO.LOW)
    #書き込みモードにする
    GPIO.output(RW_p, GPIO.LOW)
    #データピンを出力に設定
    for i in range(8):
        GPIO.setup(DATA_p[i], GPIO.OUT)
    return ans

def command(value, mode):
    GPIO.output(RS_p, mode)
    for i in range(8):
        GPIO.output(DATA_p[i], (value >> i) & 0x01)
    GPIO.output(E_p, GPIO.HIGH)
    time.sleep(EWAIT)
    GPIO.output(E_p, GPIO.LOW)

__main()


