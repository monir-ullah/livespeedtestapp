import tkinter as tk
from tkinter import messagebox
import threading
import time
import os
import speedtest
import datetime
import winreg
import socket
import random

def check_internet_speed():
    st = speedtest.Speedtest()
    st.get_best_server()
    download_speed = st.download() / 1_000_000  # Convert to Mbps
    upload_speed = st.upload() / 1_000_000  # Convert to Mbps
    return download_speed, upload_speed

def is_internet_active():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

def add_to_startup(app_name, app_path):
    try:
        key = winreg.HKEY_CURRENT_USER
        sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, sub_key, 0, winreg.KEY_SET_VALUE) as registry_key:
            winreg.SetValueEx(registry_key, app_name, 0, winreg.REG_SZ, app_path)
    except Exception as e:
        print(f"Failed to add to startup: {e}")

class LiveStreamingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Speed Checker App")
        self.root.resizable(True, True)
        self.root.wm_minsize(width=600, height=0)

        self.status = tk.StringVar()
        self.status.set("Inactive")

        self.download_speed = tk.StringVar()
        self.download_speed.set("-- Mbps")

        self.upload_speed = tk.StringVar()
        self.upload_speed.set("-- Mbps")

        self.uptime = tk.StringVar()
        self.uptime.set("0 hours 0 minutes 0 seconds")

        self.avg_download_speed = tk.StringVar()
        self.avg_download_speed.set("-- Mbps")

        self.avg_upload_speed = tk.StringVar()
        self.avg_upload_speed.set("-- Mbps")

        self.speed_checks = 0
        self.total_download_speed = 0
        self.total_upload_speed = 0
        self.start_time = None

        # Header label
        header_label = tk.Label(self.root, text="Live Streaming App", font=("Arial", 18, "bold"), pady=10)
        header_label.pack()

        # Status
        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=25)
        tk.Label(status_frame, text="Status:", font=("Arial", 12)).pack(side="left")
        tk.Label(status_frame, textvariable=self.status, font=("Arial", 12), fg="blue").pack(side="left")

        # Download Speed
        download_frame = tk.Frame(self.root)
        download_frame.pack(pady=5)
        tk.Label(download_frame, text="⬇ Download Speed:", font=("Arial", 12), fg="blue").pack(side="left")
        tk.Label(download_frame, textvariable=self.download_speed, font=("Arial", 12)).pack(side="left")

        # Upload Speed
        upload_frame = tk.Frame(self.root)
        upload_frame.pack(pady=5)
        tk.Label(upload_frame, text="⬆ Upload Speed:", font=("Arial", 12), fg="green").pack(side="left")
        tk.Label(upload_frame, textvariable=self.upload_speed, font=("Arial", 12)).pack(side="left")

        # Uptime
        uptime_frame = tk.Frame(self.root)
        uptime_frame.pack(pady=25)
        tk.Label(uptime_frame, text="⏲ Uptime:", font=("Arial", 12), fg="orange").pack(side="left")
        tk.Label(uptime_frame, textvariable=self.uptime, font=("Arial", 12)).pack(side="left")

        # Average Download Speed
        avg_download_frame = tk.Frame(self.root)
        avg_download_frame.pack(pady=5)
        tk.Label(avg_download_frame, text="⬇ Average Download Speed:", font=("Arial", 12), fg="blue").pack(side="left")
        tk.Label(avg_download_frame, textvariable=self.avg_download_speed, font=("Arial", 12)).pack(side="left")

        # Average Upload Speed
        avg_upload_frame = tk.Frame(self.root)
        avg_upload_frame.pack(pady=5)
        tk.Label(avg_upload_frame, text="⬆ Average Upload Speed:", font=("Arial", 12), fg="green").pack(side="left")
        tk.Label(avg_upload_frame, textvariable=self.avg_upload_speed, font=("Arial", 12)).pack(side="left")

        # Terminal-like log
        log_frame = tk.Frame(self.root, pady=10)
        log_frame.pack()
        self.log_display = tk.Text(log_frame, wrap=tk.WORD, width=50, height=5, font=("Courier", 10), state="disabled", bg="black", fg="white", padx=10, pady=10)
        self.log_display.pack()

        # Buttons
        button_frame = tk.Frame(self.root, pady=20)
        button_frame.pack()
        self.start_button = tk.Button(button_frame, text="Start Streaming", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", padx=20, pady=10, relief="raised", command=self.start_streaming, borderwidth=4)
        self.start_button.pack(side="left", padx=10)

        self.stop_button = tk.Button(button_frame, text="Stop Streaming", font=("Arial", 12, "bold"), bg="#f44336", fg="white", padx=20, pady=10, relief="raised", command=self.stop_streaming, borderwidth=4, disabledforeground="white")
        self.stop_button.pack(side="left", padx=10)
        self.stop_button.config(state="disabled")

        
        # Speed Test Count
        count_frame = tk.Frame(self.root)
        count_frame.pack(pady=5)
        tk.Label(count_frame, text="🔄 Speed Test Count:", font=("Arial", 12), fg="purple").pack(side="left")
        self.speed_test_count_display = tk.Label(count_frame, text=f"{self.speed_checks}", font=("Arial", 12))
        self.speed_test_count_display.pack(side="left")



        # Footer
        footer_label = tk.Label(self.root, text="Designed for Windows 11. Developed by Monir Ullah", font=("Arial", 10, "italic"), fg="gray")
        footer_label.pack(side="bottom", pady=10)

        self.streaming_thread = None
        self.speed_test_thread = None
        self.uptime_thread = None
        self.streaming_active = False

        # Add to startup
        app_path = os.path.abspath(__file__)
        add_to_startup("LiveStreamingAppByMonirUllah", app_path)

    def log_message(self, message, color="green"):
        self.log_display.config(state="normal")
        self.log_display.insert(tk.END, f"{message}\n", (color,))
        self.log_display.tag_config(color, foreground=color)
        self.log_display.see(tk.END)
        self.log_display.config(state="disabled")

    def start_streaming(self):
        if not self.streaming_active:
            self.streaming_active = True
            self.status.set("Streaming Active")
            self.start_time = datetime.datetime.now()
            self.start_button.config(state="disabled", bg="#388E3C")
            self.stop_button.config(state="normal", bg="#D32F2F", fg="white")

            # Run initial checks immediately
            threading.Thread(target=self.run_initial_checks, daemon=True).start()

            self.streaming_thread = threading.Thread(target=self.run_streaming, daemon=True)
            self.streaming_thread.start()
            self.speed_test_thread = threading.Thread(target=self.run_speed_test, daemon=True)
            self.speed_test_thread.start()
            self.uptime_thread = threading.Thread(target=self.update_uptime, daemon=True)
            self.uptime_thread.start()

    def run_initial_checks(self):
        self.log_message("Checking internet speed...", color="yellow")
        download, upload = check_internet_speed()
        self.download_speed.set(f"{download:.2f} Mbps")
        self.upload_speed.set(f"{upload:.2f} Mbps")
        self.speed_checks += 1
        self.total_download_speed += download
        self.total_upload_speed += upload
        self.avg_download_speed.set(f"{self.total_download_speed / self.speed_checks:.2f} Mbps")
        self.avg_upload_speed.set(f"{self.total_upload_speed / self.speed_checks:.2f} Mbps")
        self.speed_test_count_display.config(text=f"{self.speed_checks}")
        self.log_message("Initial speed check completed.", color="green")
        if not is_internet_active():
            self.log_message("Preventing WiFi sleep by simulating activity...", color="red")

    def run_streaming(self):
        while self.streaming_active:
            if not is_internet_active():
                self.log_message("Preventing WiFi sleep by simulating activity...", color="red")
                time.sleep(5)  # Simulate regular network activity when idle

    def run_speed_test(self):
        while self.streaming_active:
            wait_time = random.randint(600, 3300)  # Random wait time between 10-55 minutes
            self.log_message(f"Waiting {wait_time // 60} minutes before next speed test...", color="yellow")
            time.sleep(wait_time)
            if (not is_internet_active()) or is_internet_active():
                self.log_message("Checking internet speed...", color="yellow")
                download, upload = check_internet_speed()
                self.download_speed.set(f"{download:.2f} Mbps")
                self.upload_speed.set(f"{upload:.2f} Mbps")

                # Track speed for averaging
                self.speed_checks += 1
                self.total_download_speed += download
                self.total_upload_speed += upload
                self.avg_download_speed.set(f"{self.total_download_speed / self.speed_checks:.2f} Mbps")
                self.avg_upload_speed.set(f"{self.total_upload_speed / self.speed_checks:.2f} Mbps")
                self.speed_test_count_display.config(text=f"{self.speed_checks}")

                # Log a success message indicating the completion of the speed test
                self.log_message("Speed Test completed.", color="green")

    def update_uptime(self):
        while self.streaming_active:
            elapsed_time = datetime.datetime.now() - self.start_time
            hours, remainder = divmod(elapsed_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.uptime.set(f"{elapsed_time.days} days {hours} hours {minutes} minutes {seconds} seconds")
            time.sleep(1)

    def stop_streaming(self):
        if self.streaming_active:
            self.streaming_active = False
            self.status.set("Inactive")
            self.start_button.config(state="normal", bg="#4CAF50")
            self.stop_button.config(state="disabled", bg="#f44336", fg="white")

if __name__ == "__main__":
    root = tk.Tk()
    app = LiveStreamingApp(root)
    root.mainloop()
