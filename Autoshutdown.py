import time
import tkinter as tk
import cv2
from threading import Thread, Lock
from pynput import keyboard, mouse
import os
import webbrowser

# Waktu idle dalam detik sebelum shutdown (misalnya 30 menit)
IDLE_TIME_LIMIT = 30 * 60  # 30 menit

# Path ke model Haar Cascade
HAAR_CASCADE_PATH = r'C:\Users\Angga\Downloads\MobileLegends_BF\MobileLegends\data\haarcascade_frontalface_default.xml'

last_activity_time = time.time()
shutdown_warning_shown = False
warning_window = None
face_not_detected_time = time.time()
ACTIVITY_CHECK_INTERVAL = 10  # Cek aktivitas setiap 10 detik
NO_ACTIVITY_LIMIT = 5 * 60  # 5 menit tanpa aktivitas sebelum shutdown

# Lock untuk mencegah konflik antara thread
activity_lock = Lock()

# Flag untuk menghentikan skrip
stop_script = False

def on_key_press(key):
    global last_activity_time
    with activity_lock:
        last_activity_time = time.time()
    update_status("Pengguna masih mengetik.")

def on_mouse_move(x, y):
    global last_activity_time
    with activity_lock:
        last_activity_time = time.time()
    update_status("Pengguna masih menggerakkan kursor.")

def show_warning_window():
    global shutdown_warning_shown
    global warning_window

    shutdown_warning_shown = True
    warning_window = tk.Toplevel()
    warning_window.title("Shutdown Warning")
    warning_window.geometry("300x150")
    
    label = tk.Label(warning_window, text="Tidak ada aktivitas terdeteksi.\nKomputer akan segera dimatikan.", padx=10, pady=10)
    label.pack()

    button = tk.Button(warning_window, text="OK", command=close_warning_window)
    button.pack()

    # Set timer to automatically shut down after 10 seconds if no input is detected
    warning_window.after(10000, shutdown_computer)

def close_warning_window():
    global shutdown_warning_shown
    global warning_window
    shutdown_warning_shown = False
    if warning_window:
        warning_window.destroy()

def check_idle_time():
    global last_activity_time
    global face_not_detected_time
    global stop_script

    while not stop_script:
        current_time = time.time()
        idle_time = current_time - last_activity_time
        
        if idle_time >= IDLE_TIME_LIMIT:
            if not shutdown_warning_shown:
                show_warning_window()
        
        if not shutdown_warning_shown and current_time - face_not_detected_time >= NO_ACTIVITY_LIMIT:
            if idle_time >= NO_ACTIVITY_LIMIT:
                shutdown_computer()
                
        time.sleep(ACTIVITY_CHECK_INTERVAL)  # Cek setiap 10 detik

def shutdown_computer():
    global stop_script
    # Memanggil perintah untuk mematikan komputer
    os.system('shutdown /s /t 1')  # Menggunakan perintah shutdown Windows
    stop_script = True
    root.quit()  # Keluar dari aplikasi

def detect_sleeping_face():
    # Load Haar Cascade for face detection
    face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
    
    if face_cascade.empty():
        update_status("Error: Haar Cascade classifier could not be loaded.")
        return
    
    # Start video capture from the webcam
    cap = cv2.VideoCapture(0)

    global last_activity_time
    global shutdown_warning_shown
    global face_not_detected_time
    global stop_script
    
    while not stop_script:
        ret, frame = cap.read()
        if not ret:
            update_status("Error: Could not read frame from webcam.")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) == 0:
            # No face detected; update the face not detected time
            face_not_detected_time = time.time()
            update_status("Tidak ada wajah terdeteksi. Menyimpulkan pengguna sudah tidur.")
        else:
            with activity_lock:
                last_activity_time = time.time()  # Reset idle time if face is detected
            update_status(f"Wajah terdeteksi: {len(faces)}")

        time.sleep(5)  # Cek setiap 5 detik

    cap.release()
    cv2.destroyAllWindows()

def start_listeners():
    keyboard_listener = keyboard.Listener(on_press=on_key_press)
    mouse_listener = mouse.Listener(on_move=on_mouse_move)
    
    keyboard_listener.start()
    mouse_listener.start()
    
    keyboard_listener.join()
    mouse_listener.join()

def update_status(message):
    status_label.config(text=message)
    root.update_idletasks()

def stop_script_callback():
    global stop_script
    stop_script = True
    root.quit()

def start_monitoring():
    global stop_script
    stop_script = False

    # Mulai thread untuk mendeteksi wajah
    face_detection_thread = Thread(target=detect_sleeping_face)
    face_detection_thread.start()

    # Mulai thread untuk mendengarkan aktivitas pengguna
    listener_thread = Thread(target=start_listeners)
    listener_thread.start()

    # Jalankan pengecekan waktu idle di thread utama
    idle_check_thread = Thread(target=check_idle_time)
    idle_check_thread.start()

def show_about():
    about_window = tk.Toplevel()
    about_window.title("Tentang")
    about_window.geometry("500x300")
    
    label = tk.Label(about_window, text="Developed by:\nKurumi Wallnut\n© 2024 All Rights Reserved", padx=10, pady=10)
    label.pack()

    link = tk.Label(about_window, text="Python", fg="blue", cursor="hand2", padx=10, pady=10)
    link.pack()
    link.bind("<Button-1>", lambda e: webbrowser.open_new("https://www.python.org/downloads/"))

    link = tk.Label(about_window, text="PyInstaller", fg="blue", cursor="hand2", padx=10, pady=10)
    link.pack()
    link.bind("<Button-1>", lambda e: webbrowser.open_new("https://pypi.org/project/pyinstaller/"))

    link = tk.Label(about_window, text="OpenCV", fg="blue", cursor="hand2", padx=10, pady=10)
    link.pack()
    link.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/opencv/opencv/tree/master/data/haarcascades"))

    link = tk.Label(about_window, text="Tkinter", fg="blue", cursor="hand2", padx=10, pady=10)
    link.pack()
    link.bind("<Button-1>", lambda e: webbrowser.open_new("https://www.geeksforgeeks.org/how-to-install-tkinter-in-windows/"))

    link = tk.Label(about_window, text="Pynput", fg="blue", cursor="hand2", padx=10, pady=10)
    link.pack()
    link.bind("<Button-1>", lambda e: webbrowser.open_new("https://pypi.org/project/pynput/"))

def show_disclaimer():
    disclaimer_window = tk.Toplevel()
    disclaimer_window.title("Disclaimer")
    disclaimer_window.geometry("400x100")

    label = tk.Label(disclaimer_window, text="Aplikasi ini memantau aktivitas keyboard, mouse, dan deteksi wajah.\n"
                                             "Komputer Anda akan mati secara otomatis jika tidak ada aktivitas\n"
                                             "dalam waktu yang telah ditentukan. Pastikan untuk menyimpan\n"
                                             "pekerjaan Anda secara berkala.", padx=10, pady=10)
    label.pack()

    button = tk.Button(disclaimer_window, text="OK", command=disclaimer_window.destroy)
    button.pack(pady=10)

    disclaimer_window.transient(root)  # Make the disclaimer window stay on top of the main window
    disclaimer_window.grab_set()       # Block interactions with other windows until the disclaimer is closed
    root.wait_window(disclaimer_window) # Wait for the disclaimer window to be closed

if __name__ == "__main__":
    # Buat antarmuka GUI utama
    root = tk.Tk()
    root.title("Autoshutdown v1.0.0 - Rilis Awal 05/08/24")
    root.geometry("400x200")

    show_disclaimer()

    status_label = tk.Label(root, text="Klik 'Mulai' untuk memulai monitoring...", padx=10, pady=10)
    status_label.pack()

    start_button = tk.Button(root, text="Mulai", command=start_monitoring)
    start_button.pack(pady=10)

    stop_button = tk.Button(root, text="Berhenti", command=stop_script_callback)
    stop_button.pack(pady=10)

    about_button = tk.Button(root, text="Tentang", command=show_about)
    about_button.pack(pady=10)

    copyright_label = tk.Label(root, text="© 2024 Kurumi Wallnut. All Rights Reserved.", padx=10, pady=10)
    copyright_label.pack(side=tk.BOTTOM)

    root.mainloop()
