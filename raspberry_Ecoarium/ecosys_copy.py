import tkinter as tk
import imutils
import time
import cv2
import requests
import subprocess
from requests.exceptions import Timeout
from imutils.video import VideoStream
from pyzbar import pyzbar

server_addr = "http://192.168.99.42:8000"
server_addr_qrcode = server_addr + "/jt/QRCode"
server_addr_img = server_addr + "/jt/determine"
server_pw = "q1w2e3"
userId = "NaN"
nickname = "NaN"

def send_qr_to_server(qrcode):
    global userId, nickname
    # Function to send data to server
    print(qrcode + '-' + server_addr_qrcode)
    try:
        data = {'QRCode': qrcode, 'key': server_pw}  ################Example data
        response = requests.post(server_addr_qrcode, json=data, timeout=10)  # Set timeout to 10 seconds
        if response.status_code == 200:
            print("[INFO] Data sent successfully to the server.", response.status_code)
            result = response.json()
            userId = result['id']
            nickname = result['nickname']
            print(result)
            return response
        else:
            print("[ERROR] Failed to send data to the server. Status code:", response.status_code)
            return response  # Return response even if status code is not 200
    except Timeout:
        print("[ERROR] Connection to the server timed out. Please try again later.")
    except requests.exceptions.RequestException as e:
        print("[ERROR] An error occurred while sending data to the server:", e)

def upload_image(img_path, server_addr_img):
    global userId
    try:
        with open(img_path, 'rb') as file:
            files = {'file': file}  # 'file' 키에 파일 객체를 할당
            data = {'key': server_pw, 'userId': userId}  # 다른 데이터는 별도의 딕셔너리로 전달
            response = requests.post(server_addr_img, files=files, data=data)  # 파일 및 기타 데이터를 함께 전송
            if response.status_code == 200:
                print("[INFO] Image uploaded successfully.")
                return response.json()
            else:
                print("[ERROR] Failed to upload image. Status code:", response.status_code)
                return None
    except FileNotFoundError:
        print("[ERROR] Failed to open image file. File not found:", img_path)
        return None
    except Exception as e:
        print("[ERROR] An error occurred while uploading image:", e)
        return None

def show_login_success_window(nickname):
    # Function to show login success window
    login_success_window = tk.Toplevel()
    login_success_window.title("Login Success")
    
    # Display welcome message with nickname
    welcome_label = tk.Label(login_success_window, text="Welcome, " + nickname + "!", font=("Helvetica", 16))
    welcome_label.pack(pady=10)

    # Create and place Close button
    close_button = tk.Button(login_success_window, text="Close", command=login_success_window.destroy, width=20, height=2)
    close_button.pack(pady=10)

    # Close the window after few seconds
    login_success_window.after(3000, login_success_window.destroy)

def show_login_error_window(message):
    # Function to show login error window
    login_error_window = tk.Toplevel()
    login_error_window.title("Login Error")
    
    # Display error message
    error_label = tk.Label(login_error_window, text=message, font=("Helvetica", 16))
    error_label.pack(pady=10)

    # Create and place Close button
    close_button = tk.Button(login_error_window, text="Close", command=login_error_window.destroy, width=20, height=2)
    close_button.pack(pady=10)

def capture_image():
    # 현재 시간 정보 가져오기
    current_time = time.strftime("%Y%m%d-%H%M%S")
    
    # 이미지 파일 이름 구성
    image_name = f"img-{current_time}.jpg"

    # 콘솔 명령어 실행하여 사진 촬영
    command = f"libcamera-still -o /home/pi/dir/img/{image_name} --shutter 2222"
    subprocess.run(command, shell=True)

    # 이미지 파일의 전체 경로 반환
    return f"/home/pi/dir/img/{image_name}"

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
                response = send_qr_to_server(barcodeData)
                if response:  # Check if response is not None
                    if response.text == '1':
                        show_login_error_window("[ERROR CODE 1]User identification error")
                        # Clean up
                        print("[INFO] Cleaning up...")
                        cv2.destroyAllWindows()
                        vs.stop()
                        return 0  # Return 0 on failed login
                    elif response.text == '2':
                        show_login_error_window("[ERROR CODE 2]QR code mismatch.")
                        # Clean up
                        print("[INFO] Cleaning up...")
                        cv2.destroyAllWindows()
                        vs.stop()
                        return 0  # Return 0 on failed login
                    elif response.text == '3':
                        show_login_error_window("[ERROR CODE 3]Login timeout.")
                        # Clean up
                        print("[INFO] Cleaning up...")
                        cv2.destroyAllWindows()
                        vs.stop()
                        return 0  # Return 0 on failed login
                    else:
                        try: ####################LOGIN SUCCESS
                            '''
                            user_data = response.json()  # Parse JSON response
                            show_login_success_window(user_data['nickname'])  # Show login success window with nickname
                            '''
                            # Clean up
                            print("[INFO] Cleaning up...")
                            cv2.destroyAllWindows()
                            vs.stop()
                            return 1  # Return 1 on successful login
                        except ValueError:
                            print("[ERROR] Invalid JSON format received from the server.")
                            # Clean up
                            print("[INFO] Cleaning up...")
                            cv2.destroyAllWindows()
                            vs.stop()
                            return 0  # Return 0 on failed login

        # Show the output frame
        cv2.imshow("Barcode Scanner", frame)
        key = cv2.waitKey(1) & 0xFF
        
        # Check if 10 seconds have passed
        if time.time() - start_time > 10:
            # Clean up
            print("[INFO] Cleaning up...")
            cv2.destroyAllWindows()
            vs.stop()
            return 0  # Return 0 on failed login

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
    qr_button = tk.Button(root, text="QR Login", command=handle_qr_login, width=20, height=5)
    qr_button.place(relx=0.5, rely=0.5, anchor="center")
    
    # Start event loop
    root.mainloop()

# handle_qr_login 함수 내에서 호출하여 이미지 업로드 수행
def handle_qr_login():
    global nickname
    # Handle QR code login
    login_result = qr_login()
    if login_result == 1:
        # If login successful, capture image
        time.sleep(4)
        img_path = capture_image()
        time.sleep(4)
        # 이미지를 서버로 업로드
        uploaded_url = upload_image(img_path, server_addr_img)
        if uploaded_url:
            print("Uploaded image RESPONSE:", uploaded_url)
        else:
            print("Failed to upload image.")

if __name__ == "__main__":
    main()