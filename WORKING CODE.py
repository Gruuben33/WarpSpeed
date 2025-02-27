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

prevDrive = 'stop'


# onboard led test
led = Pin("LED", Pin.OUT)
led.on()
GOOD_BOY_LED = Pin(17, Pin.OUT)

ssid = "Your Wi-Fi"
password = "Your Password"

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
print("Connecting to WiFi...")

# Wait for the connection
while not wlan.isconnected():
    GOOD_BOY_LED.off()
    sleep(1)
    print("Connecting to WiFi...")
print("IP Address:", wlan.ifconfig()[0])
GOOD_BOY_LED.on()

# Function to drive/steer robot
def drive(direction):
    global prevDrive  # Declare prevDrive as global

    if direction == 'stop':
        motor1_PWM.duty_u16(0)
        motor2_PWM.duty_u16(0)
        motor1_a.off()
        motor1_b.off()
        motor2_a.off()
        motor2_b.off()
        prevDrive = 'stop'  # Update prevDrive when stopping

    elif direction == 'forward':
        motor1_a.off()
        motor1_b.on()
        motor2_a.off()
        motor2_b.on()
        motor1_PWM.duty_u16(65536)
        motor2_PWM.duty_u16(63500)
        prevDrive = 'forward'  # Update prevDrive when moving forward

    elif direction == 'backward':
        motor1_a.on()
        motor1_b.off()
        motor2_a.on()
        motor2_b.off()
        motor1_PWM.duty_u16(65536)
        motor2_PWM.duty_u16(63500)

    elif direction == 'right':
        if prevDrive == 'stop':
            motor1_a.off()
            motor1_b.on()
            motor2_a.on()
            motor2_b.off()
            motor1_PWM.duty_u16(50000)
            motor2_PWM.duty_u16(50000)
        elif prevDrive == 'forward':
            motor1_a.off()
            motor1_b.on()
            motor2_a.off()
            motor2_b.on()
            motor1_PWM.duty_u16(65536)
            motor2_PWM.duty_u16(33000)

    elif direction == 'left':
        if prevDrive == 'stop':
            motor1_a.on()
            motor1_b.off()
            motor2_a.off()
            motor2_b.on()
            motor1_PWM.duty_u16(50000)
            motor2_PWM.duty_u16(50000)
        elif prevDrive == 'forward':
            motor1_a.off()
            motor1_b.on()
            motor2_a.off()
            motor2_b.on()
            motor1_PWM.duty_u16(35536)
            motor2_PWM.duty_u16(63000)


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
        .button.disabled {
            background-color: #d3d3d3;
            cursor: not-allowed;
        }
        .status {
            margin-top: 20px;
            font-size: 18px;
            color: green;
        }
        .error {
            margin-top: 20px;
            font-size: 18px;
            color: red;
        }
    </style>
</head>
<body>
    <h1>Motor Control</h1>
    <table>
    <tr>
        <th></th>
        <th><button id="forwardButton" class="button" onclick="moveForward()">Forward</button></th>
    </tr>
    <tr>
        <th><button id="leftButton" class="button" onclick="turnLeft()">Left</button></th>
        <th><button id="stopButton" class="button" onclick="stop()">Stop</button></th>
        <th><button id="rightButton" class="button" onclick="turnRight()">Right</button></th>
    </tr>
    <tr>
        <th></th>
        <th><button id="backwardButton" class="button" onclick="moveBackward()">Backward</button></th>
    </tr>
    </table>
    <div id="statusMessage" class="status"></div>
    <div id="errorMessage" class="error"></div>

    <script>
        async function updateStatus(message, isError = false) {
            const statusMessage = document.getElementById('statusMessage');
            const errorMessage = document.getElementById('errorMessage');
            if (isError) {
                errorMessage.textContent = message;
                statusMessage.textContent = '';
            } else {
                statusMessage.textContent = message;
                errorMessage.textContent = '';
            }
        }

        async function disableButtons() {
            document.getElementById('forwardButton').classList.add('disabled');
            document.getElementById('leftButton').classList.add('disabled');
            document.getElementById('stopButton').classList.add('disabled');
            document.getElementById('rightButton').classList.add('disabled');
            document.getElementById('backwardButton').classList.add('disabled');
        }

        async function enableButtons() {
            document.getElementById('forwardButton').classList.remove('disabled');
            document.getElementById('leftButton').classList.remove('disabled');
            document.getElementById('stopButton').classList.remove('disabled');
            document.getElementById('rightButton').classList.remove('disabled');
            document.getElementById('backwardButton').classList.remove('disabled');
        }

        async function fetchDirection(url) {
            try {
                disableButtons();
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                await updateStatus('Command executed successfully');
            } catch (error) {
                await updateStatus(`Error: ${error.message}`, true);
            } finally {
                enableButtons();
            }
        }

        function moveForward() {
            fetchDirection('/forward');
        }

        function moveBackward() {
            fetchDirection('/backward');
        }

        function turnLeft() {
            fetchDirection('/left');
        }

        function turnRight() {
            fetchDirection('/right');
        }

        function stop() {
            fetchDirection('/stop');
        }
    </script>
</body>
</html>
"""

# Create a socket to listen for incoming requests
addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

    # Send the HTML page only on the initial request (i.e., when the URL is '/')
    if 'GET / ' in request_str:  # Only handle the first request to load the page
        # Send the HTML page
        cl.send('HTTP/1.1 200 OK\r\n')
        cl.send('Content-Type: text/html\r\n')
        cl.send('Connection: close\r\n\r\n')
        cl.send(html)

    # Handle other actions like '/forward', '/backward', etc.
    elif '/forward' in request_str:
        drive('forward')
    elif '/backward' in request_str:
        drive('backward')
    elif '/left' in request_str:
        drive('left')
    elif '/right' in request_str:
        drive('right')
    elif '/stop' in request_str:
        drive('stop')

    cl.close()
