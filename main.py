from machine import Pin, I2C, SPI
from ssd1306 import SSD1306_I2C
from webpage import webpage
import network
import socket
from time import sleep
import ustruct
from picozero import pico_temp_sensor, pico_led
import rp2
import sys
import _thread
WIDTH =128 
HEIGHT= 32
i2c=I2C(0,scl=Pin(5),sda=Pin(4),freq=200000)
oled = SSD1306_I2C(WIDTH,HEIGHT,i2c)

xcs=Pin(13, Pin.OUT)
xdcs=Pin(17, Pin.OUT)
dreq=Pin(16, Pin.IN)
rst=Pin(18, Pin.OUT)
xcs.value(1)
xdcs.value(1)

rst.value(0)
sleep(0.1)
rst.value(1)
sleep(0.1)

stations=[["FuseFM","streaming.radio.co","/s53051f118/listen"],["BBC Radio 4", "lsn.lv", "/bbcradio.m3u8?station=bbc_radio_fourfm\"&bitrate=320000"]] #2D array, parameters are: Name, Host, Path,
currentStation=1

spi=SPI(1, baudrate=1000000, polarity=0, phase=0,
        firstbit=SPI.MSB,
        sck=Pin(10), mosi=Pin(11), miso=Pin(12))

def reg_write(spi, cs, reg, data):
    msg=bytearray()
    msg.append(0x00 | reg)
    msg.append(data)
    
    cs.value(0)
    spi.write(msg)
    cs.value(1)

def reg_read(spi, cs, reg, nbytes=1):
    if nbytes<1:
        return bytearray()
    elif nbytes==1:
        mb=0
    else:
        mb=1
    msg=bytearray()
    msg.append(0x80 | mb<<6 | reg)
    
    cs.value(0)
    spi.write(msg)
    data=spi.read(nbytes)
    cs.value(1)
    
    return data

display=0
def updateOLED(display):
    global stations, currentStation, ip
    oled.fill(0)
    if display==0:
        oled.text("Connected on", 0, 10)
        oled.text(f"{ip}", 0, 20)
    elif display==1:
        oled.text(stations[currentStation][0], 0, 20)
    oled.show()
    return
            
    
    

def connect():
    #Connect to WLAN
    global ip
    print(f'disconnecting')
    oled.fill(0)
    oled.text("Disconnecting", 0, 20)
    oled.show()
    wlan = network.WLAN(network.STA_IF)
    wlan.disconnect() #clear previous connections
    wlan.active(False)
    sleep(1) #ensure disconnection runs

    wlan.active(True)
    wlan.connect("WILL 1996", "12345678")
    oled.fill(0)
    oled.text("Connecting", 0, 20)
    oled.show()
    while wlan.isconnected() == False:
        if rp2.bootsel_button() == 1:
            sys.exit()
        print('Waiting for connection...')
        pico_led.on()
        sleep(0.5)
        pico_led.off()
        sleep(0.5)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    """oled.fill(0)
    oled.text("Connected on", 0, 10)
    oled.text(f"{ip}", 0, 20)
    oled.show()"""
    updateOLED(0)
    pico_led.on()
    return ip

def open_socket(ip):
    address=(ip, 80)
    connection=socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def serve(connection):
    #Start a web server
    global currentStation
    global stations
    state = 'OFF'
    pico_led.off()
    temperature = 0
    station="Hello"
    print(len(stations))
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        print(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/lighton?':
            pico_led.on()
            state = 'ON'
        elif request =='/lightoff?':
            pico_led.off()
            state ='OFF'
        elif request =='/nextstation?':
                if currentStation==(len(stations)-1):
                    currentStation=0
                    updateOLED(1)
                else:
                    currentStation+=1
                    updateOLED(1)
        elif request =='/prevstation?':
            currentStation-=1
            updateOLED(1)
        elif request == '/close?':
            sys.exit()
        temperature = pico_temp_sensor.temp
        station=stations[currentStation][0]
        #station="hi"
        html = webpage(temperature, state, station)
        client.send(html)
        client.close()




ip=connect()
connection=open_socket(ip)

#host = "streaming.radio.co"
#path = "/s53051f118/listen"
_thread.start_new_thread(serve, (connection,))


def sci_write(addr, value):
    while not dreq.value():
        pass
    xcs.value(0)
    spi.write(bytearray([0x02, addr, value >> 8, value & 0xFF]))
    xcs.value(1)
    
def send_data(data):
    idx = 0
    while idx < len(data):
        while not dreq.value():
            pass
        
        chunk = data[idx:idx+32]  # 32 bytes typical
        xdcs.value(0)
        spi.write(chunk)
        xdcs.value(1)
        
        idx += len(chunk)
# Init VS1053b
sci_write(0x03, 0x6000)  # CLOCKF
sci_write(0x0B, 0x2020)  # volume

spi.init(baudrate=5000000)
import socket

addr = socket.getaddrinfo(stations[currentStation][1], 80)[0][-1]
s = socket.socket()
s.connect(addr)
"""oled.fill(0)
oled.text(stations[currentStation][0], 0, 20)
oled.show()"""
updateOLED(1)

# request stream
request = "GET {} HTTP/1.1\r\nHost: {}\r\n\r\n".format(stations[currentStation][2], stations[currentStation][1])
s.send(request.encode())

# skip headers
while True:
    if s.readline() == b"\r\n":
        break

# stream audio
while True:
    data = s.read(512)
    if not data:
        break
    send_data(data)