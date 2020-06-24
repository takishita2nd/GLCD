import RPi.GPIO as GPIO
import time
import datetime
import GLCD

def __main():
    GLCD.PinsInit(20, 7, 8, 9, 18, 19, 10, 11, 12, 13, 14, 15, 16, 17)
    GLCD.GLCDInit()
    GLCD.GLCDDisplayClear()

    try:
        while True:
            GLCD.GLCDPuts(1, 8, "Date :")
            GLCD.GLCDPuts(10, 16, datetime.datetime.now().strftime('%Y:%m:%d %A'))
            GLCD.GLCDPuts(1, 40, "Time        :" + datetime.datetime.now().strftime('%H:%M:%S'))
            time.sleep(0.1)
    except KeyboardInterrupt:
        GLCD.GLCDDisplayClear()
        GPIO.cleanup()

__main()
