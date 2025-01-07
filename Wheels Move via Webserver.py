import network
import socket
import time
from time import sleep
from machine import Pin, PWM

# Initialize PWM and motor pins
motor1_a = Pin(2, Pin.OUT)
motor1_b = Pin(3, Pin.OUT)
motor1_PWM = PWM(Pin(0))  # Initialize PWM on pin 0 (GPIO 0)
motor2_a = Pin(4, Pin.OUT)
motor2_b = Pin(5, Pin.OUT)
motor2_PWM = PWM(Pin(1))  # Initialize PWM on pin 1 (GPIO 1)
motor1_PWM.freq(1000)
motor2_PWM.freq(1000)

# WiFi credentials
ssid = "CYBERTRON"
password = "Mr.LamYo"

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
print("Connecting to WiFi...")

while not wlan.isconnected():
    sleep(1)
    print("Connecting to WiFi...")
print("IP Address:", wlan.ifconfig()[0])

# Function to drive/steer robot
def drive(direction):
    if direction == 'stop':
        motor1_PWM.duty_u16(0)  # Turn off PWM signal
        motor2_PWM.duty_u16(0)
        motor1_a.off()
        motor1_b.off()
        motor2_a.off()
        motor2_b.off()

    elif direction == 'forward':
        motor1_a.on()
        motor1_b.off()
        motor2_a.on()
        motor2_b.off()
        # Gradual speed increase for forward direction
        if speed == 0:
            speed = 512
        motor1_PWM.duty_u16(speed)
        motor2_PWM.duty_u16(speed)
        time.sleep(0.5)
        if speed < 513:
            speed = 767
        motor1_PWM.duty_u16(speed)
        motor2_PWM.duty_u16(speed)
        time.sleep(0.5)
        if speed < 768:
            speed = 1023
        motor1_PWM.duty_u16(speed)
        motor2_PWM.duty_u16(speed)

    elif direction == 'backward':
        motor1_a.off()
        motor1_b.on()
        motor2_a.off()
        motor2_b.on()
        motor1_PWM.duty_u16(512)
        motor2_PWM.duty_u16(512)
        time.sleep(0.5)
        motor1_PWM.duty_u16(1023)
        motor2_PWM.duty_u16(1023)

    elif direction == 'left':
        motor1_a.on()
        motor1_b.off()
        motor2_a.on()
        motor2_b.off()
        motor1_PWM.duty_u16(700)
        motor2_PWM.duty_u16(1023)
        speed = 0

    elif direction == 'right':
        motor1_a.on()
        motor1_b.off()
        motor2_a.on()
        motor2_b.off()
        motor1_PWM.duty_u16(1023)
        motor2_PWM.duty_u16(700)
        speed = 0

# HTML page for the web interface
html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pico W Web Control</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
        }
        .button {
            padding: 20px;
            font-size: 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
        }
        .button:active {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <h1>Motor Control</h1>
    <table>
    <tr>
        <th></th>
        <th><button class="button" onclick="moveForward()">Forward</button></th>
    </tr>
    <tr>
        <th><button class="button" onclick="turnLeft()">Left</button></th>
        <th><button class="button" onclick="stop()">Stop</button></th>
        <th><button class="button" onclick="turnRight()">Right</button></th>
    </tr>
    <tr>
        <th></th>
        <th><button class="button" onclick="moveBackward()">Backward</button></th>
    </tr>
    </table>
    <script>
        function moveForward() {
            fetch('/forward')
        }
        function moveBackward(){
            fetch('/backward')
        }
        function turnLeft(){
            fetch('/left')
        }
        function turnRight(){
            fetch('/right')
        }
        function stop(){
            fetch('/stop')
        }
    </script>
</body>
</html>
"""

# Create a socket to listen for incoming requests
addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SOL_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
print('Listening on', addr)

# Serve the web page and handle requests
while True:
    cl, addr = s.accept()
    print('Client connected from', addr)
    request = cl.recv(1024)
    request_str = str(request)
    print(request_str)

    # Extract the direction from the URL, e.g., /forward, /backward, etc.
    if '/forward' in request_str:
        drive('forward')
    elif '/backward' in request_str:
        drive('backward')
    elif '/left' in request_str:
        drive('left')
    elif '/right' in request_str:
        drive('right')
    elif '/stop' in request_str:
        drive('stop')

    # Send the HTML page
    cl.send('HTTP/1.1 200 OK\r\n')
    cl.send('Content-Type: text/html\r\n')
    cl.send('Connection: close\r\n\r\n')
    cl.send(html)

    cl.close()

