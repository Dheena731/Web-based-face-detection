import cv2
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk

class FaceCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Capture GUI")
        self.root.geometry("700x300")  

        # Variables
        self.person_name = tk.StringVar()
        self.mode = tk.StringVar(value="auto")
        self.save_path = ""
        self.count = 0
        self.frame_count = 0
        self.capture_running = False
        self.frame = None

        # GUI Layout
        self.setup_gui()

        # OpenCV
        self.cap = None

    def setup_gui(self):
        # Input for name
        tk.Label(self.root, text="Person Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.person_name).grid(row=0, column=1, padx=5, pady=5)

        # Mode dropdown
        tk.Label(self.root, text="Mode:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Combobox(self.root, textvariable=self.mode, values=["auto", "manual"], state="readonly").grid(row=1, column=1, padx=5, pady=5)

        # Buttons
        tk.Button(self.root, text="Start Capture", command=self.start_capture).grid(row=2, column=0, padx=5, pady=5)
        tk.Button(self.root, text="Stop", command=self.stop_capture).grid(row=2, column=1, padx=5, pady=5)

        # Capture Button (manual mode only)
        self.capture_btn = tk.Button(self.root, text="Capture Image", command=self.capture_image)
        self.capture_btn.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        self.capture_btn.config(state="disabled")

        # Status label
        self.status_label = tk.Label(self.root, text="Status: Idle", fg="blue")
        self.status_label.grid(row=4, column=0, columnspan=2)

        # Image count
        self.count_label = tk.Label(self.root, text="Images Captured: 0")
        self.count_label.grid(row=5, column=0, columnspan=2)

        # Video panel
        self.video_panel = tk.Label(self.root)
        self.video_panel.grid(row=0, column=2, rowspan=6, padx=10)

    def start_capture(self):
        name = self.person_name.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Please enter a name.")
            return

        self.save_path = os.path.join("face_dataset", name)
        os.makedirs(self.save_path, exist_ok=True)

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open webcam.")
            return

        # Smaller resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        self.capture_running = True
        self.count = 0
        self.frame_count = 0
        self.status_label.config(text="Status: Capturing...", fg="green")

        if self.mode.get() == "manual":
            self.capture_btn.config(state="normal")

        self.root.after(10, self.video_loop)

    def stop_capture(self):
        self.capture_running = False
        if self.cap:
            self.cap.release()
        self.status_label.config(text="Status: Stopped", fg="red")
        self.video_panel.config(image='')  # Clear video feed
        self.capture_btn.config(state="disabled")

    def capture_image(self):
        if self.frame is not None:
            face_img = cv2.resize(self.frame, (224, 224))
            img_name = os.path.join(self.save_path, f"{self.count}.jpg")
            cv2.imwrite(img_name, face_img)
            self.count += 1
            self.count_label.config(text=f"Images Captured: {self.count}")
            self.status_label.config(text=f"Saved: {img_name}", fg="blue")

    def video_loop(self):
        if not self.capture_running:
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        self.frame = frame.copy()

        # Auto capture
        if self.mode.get() == "auto" and self.frame_count % 5 == 0:
            self.capture_image()

        self.frame_count += 1

        # Convert image to RGB and resize to match preview size
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame).resize((320, 240))
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_panel.imgtk = imgtk
        self.video_panel.configure(image=imgtk)

        self.root.after(10, self.video_loop)

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = FaceCaptureApp(root)
    root.mainloop()
