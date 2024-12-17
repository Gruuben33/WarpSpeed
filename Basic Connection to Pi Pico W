import network
import socket
import time
from machine import Pin

# Set up the onboard LED (GPIO 25)
led = Pin(15, Pin.OUT)

# Motor pins
# motor1_a = Pin(2, Pin.OUT)
# motor1_b = Pin(3, Pin.OUT)
# motor1_PWM = Pin(0, Pin.OUT)
# motor2_a

# WiFi credentials
ssid = "CYBERTRON"
password = "Mr.LamYo"

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
print("Connected to WiFi")

while not wlan.isconnected():
    time.sleep(1)
    print("Connecting to WiFi...")
print("IP Address:", wlan.ifconfig()[0])



# HTML page for the web interface
html = """
<!DOCTYPE html>
<html lang="en">
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
    <h1>Control LED on Raspberry Pi Pico W</h1>
    <button class="button" onclick="toggleLED()">Toggle LED</button>
    <script>
        function toggleLED() {
            fetch('/toggle');
        }
    </script>
</body>
</html>
"""

# Create a socket to listen for incoming requests
addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]
s = socket.socket()
s.bind(addr) 
s.listen(1)
print('Listening on', addr)

# Serve the web page and handle requests
while True:
    cl, addr = s.accept()
    print('Client connected from', addr)
    request = cl.recv(1024)
    request_str = str(request)

    # Toggle LED based on the /toggle route
    if '/toggle' in request_str:
        led.value(not led.value())
        print("LED toggled")

    # Send the HTML page
    cl.send('HTTP/1.1 200 OK\r\n')
    cl.send('Content-Type: text/html\r\n')
    cl.send('Connection: close\r\n\r\n')
    cl.send(html)

    cl.close()


