import time
import smbus

i2c = smbus.SMBus(1)
address = 0x5c

loop = True
block = []
while loop:
    try:
        i2c.write_i2c_block_data(address, 0x00,[])
        i2c.write_i2c_block_data(address, 0x03,[0x00, 0x04])

        time.sleep(0.05)

        block = i2c.read_i2c_block_data(address, 0, 6)
        loop = False
    except IOError:
        pass

hum = block[2] << 8 | block[3]
temp = block[4] << 8 | block[5]

print('hum : ' + format( hum/10) + ' %Rh')
print('temp: ' + format(temp/10) + ' digC')

