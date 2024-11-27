import cv2
import numpy as np
from flask import Flask, render_template, Response, jsonify
from pyzbar import pyzbar
import serial
import time

app = Flask(__name__)

detected_results = []  # Keep track of all detected results
detected_barcodes = set()  # Track barcodes already sent to the frontend
detected_commands = set()  # To keep track of sent commands
ser = serial.Serial('COM3', 9600)  # Initialize serial communication with Arduino

last_detected_barcode = None  # Track the last detected barcode

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sort')
def sort():
    return render_template('sort.html')



def detect_color(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define color ranges in HSV
    colors = {
        "Red": [(0, 120, 70), (10, 255, 255), (170, 120, 70), (180, 255, 255)],
        "Green": [(35, 50, 50), (85, 255, 255)],
        "Blue": [(100, 150, 0), (140, 255, 255)]
    }

    for color_name, ranges in colors.items():
        if len(ranges) == 4:
            lower1, upper1, lower2, upper2 = ranges
            mask1 = cv2.inRange(hsv, lower1, upper1)
            mask2 = cv2.inRange(hsv, lower2, upper2)
            mask = mask1 + mask2
        else:
            lower, upper = ranges
            mask = cv2.inRange(hsv, lower, upper)

        if cv2.countNonZero(mask) > 500:
            return color_name
    return "Unknown"

def read_barcodes(frame):
    barcodes = pyzbar.decode(frame)
    for barcode in barcodes:
        barcode_data = barcode.data.decode("utf-8")
        return barcode_data
    return None

def send_to_arduino(command):
    """Send command to Arduino to control the motor"""
    if command and command not in detected_commands:
        ser.write((command + '\n').encode())  # Send the command to Arduino
        detected_commands.add(command)  # Mark this command as sent
        print(f"Sent command to Arduino: {command}")  # Debugging line

def process_detection(barcode, color):
    """Process the barcode and color to determine the motor action"""
    if barcode == "12345":
        command = "LEFT"
    elif barcode == "67890":
        command = "RIGHT"
    elif barcode == "987654":
        command = "STOP"
    else:
        command = None

    # Send the command to Arduino if any
    send_to_arduino(command)
    print(command)

    # Return the result for updating the table
    return {"barcode": barcode, "color": color, "direction": command}

def generate_frames():
    global last_detected_barcode
    camera = cv2.VideoCapture(1)
    while True:
        success, frame = camera.read()
        if not success:
            break

        barcode = read_barcodes(frame)
        color = detect_color(frame)

        if barcode:
            # Check if the current barcode is different from the last detected barcode
            if barcode != last_detected_barcode:
                # Process detection and send to Arduino
                result = process_detection(barcode, color)

                # Add the detection result for updating the table
                detected_results.append(result)

                # Update the last detected barcode
                last_detected_barcode = barcode

        # Display barcode and color on frame
        cv2.putText(frame, f"Barcode: {barcode}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, f"Color: {color}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_sorted_products')
def get_sorted_products():
    global detected_results
    return jsonify(detected_results)

if __name__ == '__main__':
    app.run(debug=True)
