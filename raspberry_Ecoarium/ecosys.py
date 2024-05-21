import tkinter as tk
import imutils
import time
import cv2
import requests
import subprocess
from requests.exceptions import Timeout
from imutils.video import VideoStream
from pyzbar import pyzbar

# Location INFO
location = "JT_0"

# Server INFO
server_addr = "http://172.20.10.10:8000"
server_addr_qrcode = server_addr + "/jt/QRCode"
server_addr_img = server_addr + "/jt/determine"
server_pw = "q1w2e3"

# USER INFO
userId = "NaN"
nickname = "NaN"

# DEF: Send QRCODE
def req_qr(qrcode):
    global userId, nickname
    # Function to send data to server
    print(qrcode + '-' + server_addr_qrcode)
    try:
        data = {'QRCode': qrcode, 'key': server_pw }  ################Example data
        response = requests.post(server_addr_qrcode, json=data, timeout=10)  # Set timeout to 10 seconds
        if response.status_code == 200:
            print("[INFO] Data sent successfully to the server.", response.status_code)
            result = response.json()
            print(result)
            return response
        else:
            print("[ERROR] Failed to send data to the server. Status code:", response.status_code)
            return response  # Return response even if status code is not 200
    except Timeout:
        print("[ERROR] Connection to the server timed out. Please try again later.")
    except requests.exceptions.RequestException as e:
        print("[ERROR] An error occurred while sending data to the server:", e)

# DEF: Send IMG
def req_image(img_path):
    global server_addr_img, userId
    try:
        with open(img_path, 'rb') as file:
            files = {'file': file}  # 'file' 키에 파일 객체를 할당
            data = {'key': server_pw, 'userId': userId, 'location': location } 
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
    

def show_msg_window(message, callback=None):
    # Create the message window
    msg_window = tk.Toplevel()
    msg_window.title("Message")
    
    # Create a Label to measure the text width
    temp_label = tk.Label(msg_window, text=message, font=("Helvetica", 24))
    temp_label.pack()

    # Update the window to get the correct size of the text
    msg_window.update_idletasks()
    
    # Get the size of the text
    text_width = temp_label.winfo_width()
    text_height = temp_label.winfo_height()
    
    # Destroy the temporary label
    temp_label.destroy()

    # Calculate the window size based on the text size
    window_width = max(text_width + 40, 800)  # Add some padding
    window_height = max(text_height + 80, 480)  # Add some padding for the button

    text_label = tk.Label(msg_window, text=message, font=("Helvetica", 24), wraplength=window_width - 40)
    text_label.place(relx=0.5, rely=0.3, anchor="center")

    if callback:
        # If a callback function is provided, execute it when the close button is clicked
        close_button = tk.Button(msg_window, text="OK", command=lambda: on_window_close(msg_window, callback), width=20, height=2, font=("Helvetica", 14))
    else:
        close_button = tk.Button(msg_window, text="OK", command=msg_window.destroy, width=20, height=2, font=("Helvetica", 14))
    close_button.place(relx=0.5, rely=0.7, anchor="center")  # Adjusted y-position for the button

    # Get the screen size
    screen_width = 800
    screen_height = 480

    # Calculate the position for the window to be centered
    position_x = (screen_width // 2) - (window_width // 2)
    position_y = (screen_height // 2) - (window_height // 2)

    # Set the geometry of the message window
    msg_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    # Make sure the window is above the main window
    msg_window.transient()

    # Focus on the message window
    msg_window.grab_set()
    msg_window.focus()

    # Make the window full screen
    msg_window.attributes("-fullscreen", True)

# DEF: WINDOW CLOSE
def on_window_close(window, callback):
    window.destroy()
    if callback:
        callback()

# DEF: IMG CAPTURE
def capture_image():
    # 현재 시간 정보 가져오기
    current_time = time.strftime("%Y%m%d-%H%M%S")
    
    # 이미지 파일 이름 구성
    image_name = f"img-{current_time}.jpg"

    # 콘솔 명령어 실행하여 사진 촬영
    command = f"libcamera-still -o /home/pi/Ecoarium/img/{image_name}"
    subprocess.run(command, shell=True)

    # 이미지 파일의 전체 경로 반환
    return f"/home/pi/Ecoarium/img/{image_name}"

def read_qr():
    # Function to handle QR code login
    print("[INFO] Trying to login...")
    # Initialize video stream and allow camera sensor to warm up
    print("[INFO] Starting video stream...")
    vs = VideoStream(src=0).start()  # Use USB webcam
    time.sleep(1.0)
    
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
                # Clean up
                print("[INFO] Cleaning up...")
                cv2.destroyAllWindows()
                vs.stop()
                return barcodeData
            
        # Show the output frame
        cv2.imshow("Barcode Scanner", frame)
        key = cv2.waitKey(1) & 0xFF
        
        # Check if 10 seconds have passed
        if time.time() - start_time > 15:
            # Clean up
            print("[INFO] Cleaning up...")
            cv2.destroyAllWindows()
            vs.stop()
            return 3  # TimeOut

# DEF: LOGIN
def login():
    global nickname, userId, login_button
    login_button.config(state="disabled")  # 로그인 버튼 비활성화
    barcodeData = read_qr()
    if barcodeData == 3:
        show_msg_window("[ERROR CODE 3] Login timeout")
        login_button.config(state="normal")
        return 3
    response = req_qr(barcodeData)
    # 정상적으로 응답이 오면 response에는 userdata가 담김
    if response:  # Check if response is not None
        if response.text == '1':
            show_msg_window("[ERROR CODE 1]User identification error")
            login_button.config(state="normal")
            return 1
        elif response.text == '2':
            show_msg_window("[ERROR CODE 2]QR code mismatch")
            login_button.config(state="normal")
            return 2
        elif response.text == '3':
            show_msg_window("[ERROR CODE 3]Login timeout")
            login_button.config(state="normal")
            return 3
        else:
            # 로그인 성공
            try:
                user = response.json()
                userId = user['id']
                nickname = user['nickname']
                show_msg_window("Welcome, " + nickname + "!", place_cup_open)
            except ValueError:
                print("[ERROR] Invalid JSON format received from the server.")
                login_button.config(state="normal")
                return 4

def door_open():
    time.sleep(0.5)
    command = f"sudo /home/pi/Ecoarium/ecosys_door o"
    subprocess.run(command, shell=True)

def door_close():
    time.sleep(0.5)
    command = f"sudo /home/pi/Ecoarium/ecosys_door c"
    subprocess.run(command, shell=True)

# DEF: After Login, Open the door
def place_cup_open():
    ### DOOR OPEN 작업 필요###### DOOR OPEN 작업 필요###### DOOR OPEN 작업 필요###### DOOR OPEN 작업 필요###### DOOR OPEN 작업 필요###### DOOR OPEN 작업 필요###### DOOR OPEN 작업 필요###
    door_open()
    show_msg_window("[INFO] Place the cup in the machine", place_cup_close)
    pass

# DEF: After placing the cup in machine, Close the door and capture img
def place_cup_close():
    ### DOOR CLOSE 작업 필요###### DOOR CLOSE 작업 필요###### DOOR CLOSE 작업 필요###### DOOR CLOSE 작업 필요###### DOOR CLOSE 작업 필요###### DOOR CLOSE 작업 필요###### DOOR CLOSE 작업 필요###
    door_close()
    show_msg_window("[INFO] Take a picture of the cup.", capture_send_img)
    pass

# DEF:
def bring_cup_open():
    ### DOOR OPEN 작업 필요###### DOOR OPEN 작업 필요###### DOOR OPEN 작업 필요###### DOOR OPEN 작업 필요###### DOOR OPEN 작업 필요###### DOOR OPEN 작업 필요###### DOOR OPEN 작업 필요###
    door_open()
    show_msg_window("[INFO] Bring the cup back", door_close)
    login_button.config(state="normal")
    pass

# DEF: capture img and send img
def capture_send_img():
    img_path = capture_image()
    response = req_image(img_path)
    if response:
        score = float(response.strip())
        if score > 0.5:
            show_msg_window("[INFO] This is not a suitable cup.", bring_cup_open)
            print("[INFO] Image Uploaded. RESPONSE:", response)
        else:
            show_msg_window("[INFO] Stamp save complete!")
            login_button.config(state="normal")
            print("[INFO] Image Uploaded. RESPONSE:", response)
    else:
        show_msg_window("[ERROR] Failed to upload image.")
        login_button.config(state="normal")
        print("[ERROR] Failed to upload image.")
    pass

def close_all_toplevels():
    global root
    # Tkinter에서 열려진 모든 Toplevel 창을 닫는 함수
    for window in root.winfo_children():
        if isinstance(window, tk.Toplevel):
            window.destroy()

def refresh():
    global root
    # 현재 윈도우를 닫고 프로그램을 다시 실행
    close_all_toplevels()  # 열려진 모든 Toplevel 창을 닫음
    root.destroy()
    main()

def show_admin_buttons():
    global open_button, close_button
    
    # Create and place OPEN button
    open_button = tk.Button(root, text="DOPEN", command=door_open, font=("Helvetica", 14), width=10, height=2)
    open_button.place(relx=0.95, rely=0.35, anchor="ne")
    
    # Create and place CLOSE button
    close_button = tk.Button(root, text="DCLOSE", command=door_close, font=("Helvetica", 14), width=10, height=2)
    close_button.place(relx=0.95, rely=0.5, anchor="ne")

def main():
    global root, login_button
    # Create main window
    root = tk.Tk()
    root.title("Ecoarium")
    
    # Set window size and position
    root.attributes('-fullscreen', True)
    window_width = 800
    window_height = 400
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = int((screen_width / 2) - (window_width / 2))
    y_coordinate = int((screen_height / 2) - (window_height / 2))
    root.geometry("%dx%d+%d+%d" % (window_width, window_height, x_coordinate, y_coordinate))
    
    # Display "Ecoarium" text
    label = tk.Label(root, text="Ecoarium", font=("Helvetica", 32))
    label.place(relx=0.5, rely=0.2, anchor="center")
    
    # QR Login Button
    login_button = tk.Button(root, text="Login!", command=login, font=("Helvetica", 24), width=18, height=5)
    login_button.place(relx=0.5, rely=0.5, anchor="center")
    
    # Quit Button
    quit_button = tk.Button(root, text="Quit", command=root.destroy, font=("Helvetica", 14), width=10, height=2)
    quit_button.place(relx=0.95, rely=0.05, anchor="ne")
    
    # Refresh Button
    refresh_button = tk.Button(root, text="Refresh", command=refresh, font=("Helvetica", 14), width=10, height=2)
    refresh_button.place(relx=0.95, rely=0.20, anchor="ne")
    
    # Admin Button
    admin_button = tk.Button(root, text="ADMIN", command=show_admin_buttons, font=("Helvetica", 14), width=10, height=2)
    admin_button.place(relx=0.95, rely=0.35, anchor="ne")
    
    # Start event loop
    root.mainloop()

if __name__ == "__main__":
    main()