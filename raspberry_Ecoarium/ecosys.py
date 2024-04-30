import tkinter as tk
import imutils
import time
import cv2
import requests
from requests.exceptions import Timeout
from imutils.video import VideoStream
from pyzbar import pyzbar

def send_data_to_server(qrcode):
    # Function to send data to server
    url = "http://192.168.34.42:8000/admin/test"
    print(qrcode + '-' + url)
    try:
        data = {'QRCode': qrcode, 'key': 2019}  ################Example data
        response = requests.post(url, json=data, timeout=10)  # Set timeout to 10 seconds
        if response.status_code == 200:
            print("[INFO] Data sent successfully to the server.", response.status_code)
            result = response.json()
            print(result)
        else:
            print("[INFO] Failed to send data to the server. Status code:", response.status_code)
    except Timeout:
        print("[ERROR] Connection to the server timed out. Please try again later.")
    except requests.exceptions.RequestException as e:
        print("[ERROR] An error occurred while sending data to the server:", e)

def qr_login():
    # Function to handle QR code login
    print("[INFO] Trying to login...")
    # Initialize video stream and allow camera sensor to warm up
    print("[INFO] Starting video stream...")
    vs = VideoStream(src=0).start()  # Use USB webcam
    time.sleep(2.0)
    
    start_time = time.time()  # Get the start time
    
    # Loop over frames from the video stream
    while True:
        # Grab the frame from the video stream and resize it
        frame = vs.read()
        frame = imutils.resize(frame, width=400)
        
        # Find and decode barcodes in the frame
        barcodes = pyzbar.decode(frame)

        # Loop over detected barcodes
        for barcode in barcodes:
            # Decode barcode data and type
            barcodeData = barcode.data.decode("utf-8")
            
            # Check if barcodeData is not empty
            if barcodeData.strip():
                # Print barcode data to console
                print("[INFO] Barcode Data:", barcodeData)
                # Send barcode data to the server
                send_data_to_server(barcodeData)
                # Clean up
                print("[INFO] Cleaning up...")
                cv2.destroyAllWindows()
                vs.stop()
                return

        # Show the output frame
        cv2.imshow("Barcode Scanner", frame)
        key = cv2.waitKey(1) & 0xFF
        
        # Check if 10 seconds have passed
        if time.time() - start_time > 10:
            # Clean up
            print("[INFO] Cleaning up...")
            cv2.destroyAllWindows()
            vs.stop()
            return


def main():
    # Create main window
    root = tk.Tk()
    root.title("Ecoarium")
    
    # Set window size and position
    root.attributes('-fullscreen', True)
    window_width = 800
    window_height = 400
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = (screen_width / 2) - (window_width / 2)
    y_coordinate = (screen_height / 2) - (window_height / 2)
    root.geometry("%dx%d+%d+%d" % (window_width, window_height, x_coordinate, y_coordinate))
    
    # Display "Ecoarium" text
    label = tk.Label(root, text="Ecoarium", font=("Helvetica", 24))
    label.place(relx=0.5, rely=0.3, anchor="center")
    
    # Create and place Quit button
    quit_button = tk.Button(root, text="Quit", command=root.destroy)
    quit_button.place(relx=0.95, rely=0.05, anchor="ne")
    
    # Create and place QR Login button
    qr_button = tk.Button(root, text="QR Login", command=qr_login, width=20, height=5)
    qr_button.place(relx=0.5, rely=0.5, anchor="center")
    
    # Start event loop
    root.mainloop()

if __name__ == "__main__":
    main()
