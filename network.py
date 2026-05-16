import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine
import rp2
import sys


def connect():
    #Connect to WLAN
    print(f'disconnecting')
    wlan = network.WLAN(network.STA_IF)
    wlan.disconnect() #clear previous connections
    wlan.active(False)
    sleep(1) #ensure disconnection runs

    wlan.active(True)
    wlan.connect("WILL 1996", "12345678")
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
    pico_led.on()
    return ip

def open_socket(ip):
    address=(ip, 80)
    connection=socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def webpage(temperature, state):
    html = f'''
            <!DOCTYPE html>
            <html>            
            <body style=background-color:#767676;color:#F9F9F9;>
            <h1 style=background-image:linear-gradient(#323232,#5F5F5F);text-align:center;font-size:32px;padding:50px>WCS Project</h1>
            <p>LED: {state}</p>
            <p>Temperature is {temperature}</p>
            <div>
            <form action="./lighton">
            <input type="submit" value="Light on" />
            </form>
            <form action="./lightoff">
            <input type="submit" value="Light off" />
            </form>
            <form action="./close">
            <input type="submit" value="Stop server" />
            </form>
            </body>
            </html>
            '''
    return str(html)
def serve(connection):
    #Start a web server
    state = 'OFF'
    pico_led.off()
    temperature = 0
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
        elif request == '/close?':
            sys.exit()
        temperature = pico_temp_sensor.temp
        html = webpage(temperature, state)
        client.send(html)
        client.close()


ip=connect()
connection=open_socket(ip)
serve(connection)
