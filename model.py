import cv2
from pyzbar import pyzbar
import serial
import time


ser = serial.Serial('COM3', 9600)  

def read_barcode_and_color(frame):
    barcodes = pyzbar.decode(frame)
    for barcode in barcodes:
        barcode_data = barcode.data.decode('utf-8')
        (x, y, w, h) = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, barcode_data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return barcode_data, frame
    
    return None, frame

def identify_color(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    lower_red = (0, 120, 70)
    upper_red = (10, 255, 255)
    lower_blue = (110, 50, 50)
    upper_blue = (130, 255, 255)

    mask_red = cv2.inRange(hsv, lower_red, upper_red)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    if cv2.countNonZero(mask_red) > cv2.countNonZero(mask_blue):
        return "Red"
    else:
        return "Blue"

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    barcode, frame = read_barcode_and_color(frame)
    if barcode:
        color = identify_color(frame)
        if barcode == "12345":
            ser.write(b'LEFT')
            print(barcode)
        elif barcode == "987654":
            ser.write(b'RIGHT')
            print(barcode)
        
        cv2.putText(frame, color, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
