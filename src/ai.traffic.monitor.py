import cv2
import os
import numpy as np
from ultralytics import YOLO
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import threading
import datetime
import queue
import threading


traffic_classes = [
    "car", "truck", "bus", "motorcycle", "bicycle", "person",
    "traffic light", "stop sign", "train"
]

loop_video=True


def load_yolo_model(model_name):
    search_paths = [
        f"/usr/bin/{model_name}",
        f"/usr/local/bin/{model_name}",
        os.path.join(os.getcwd(), model_name)
    ]

    for path in search_paths:
        if os.path.exists(path):
            print(f"Found model at: {path}")
            return YOLO(path)

    print("Model not found locally. Downloading...")
    model = YOLO(model_name)
    print(f"Model downloaded and loaded: {model_name}")
    return model

class TrafficDetectionApp:
    def __init__(self, root):
        self.root = root
        self.set_title_text("AI - Traffic Monitor")

        # Start maximized by default
        try:
            self.root.attributes('-zoomed', True)
        except tk.TclError:
            self.root.attributes('-fullscreen', True)

        # Keep standard window buttons (close, minimize, maximize)
        self.root.overrideredirect(False)
        self.root.configure(bg="black")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Handle minimize → restore to 700x400 and center
        def on_restore(event=None):
            if self.root.state() == "normal":
                w, h = 900, 600
                sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
                x = (sw - w) // 2
                y = (sh - h) // 2
                self.root.geometry(f"{w}x{h}+{x}+{y}")

        self.root.bind("<Map>", on_restore)

        # Keyboard shortcuts
        self.root.bind("<Escape>", lambda e: self.on_close())
        self.root.bind("q", lambda e: self.on_close())
        self.root.bind("Q", lambda e: self.on_close())
        self.paused = False
        self.root.bind("<space>", self.toggle_pause)

        self.mode = None
        self.cap = None
        self.running = False
        self.counter_labels = {}
        self.setup_mode_selector()


    def set_title_text(self, text):
        # Crude way to move title text to the left ( by adding spaces )
        screen_width = root.winfo_screenwidth()
        num_spaces = screen_width
        title_text = text + " " * num_spaces
        title_text += " "
        self.root.title(title_text)


    def toggle_pause(self, event=None):
        self.paused = not self.paused

    def setup_mode_selector(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        frame = tk.Frame(self.root, bg="black")
        frame.pack(expand=True)
        tk.Label(frame, text="Select Mode", font=("Arial", 28, "bold"), fg="white", bg="black").pack(pady=40)
        for mode in ["Image Mode", "Video Mode", "Live Mode"]:
            ttk.Button(frame, text=mode, command=lambda m=mode: self.start_mode(m)).pack(pady=10, ipadx=20, ipady=10)
        ttk.Button(frame, text="Exit", command=self.on_close).pack(pady=40)

    def start_mode(self, mode):
        if mode == "Image Mode":
            file = filedialog.askopenfilename(title="Select Image", filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
            if not file:
                return
            self.mode = "image"
            self.source_path = file
        elif mode == "Video Mode":
            file = filedialog.askopenfilename(title="Select Video", filetypes=[("Video files", "*.mp4 *.avi *.mov")])
            if not file:
                return
            self.mode = "video"
            self.source_path = file
        elif mode == "Live Mode":
            self.mode = "live"
            self.source_path = 0
        self.setup_ui()


    def setup_ui(self):
        self.img1 = None
        self.img2 = None

        for widget in self.root.winfo_children():
            widget.destroy()

        self.frame_original = tk.Label(self.root, bg="black", highlightthickness=2, highlightbackground="white")
        self.frame_original.place(relx=0.01, rely=0.05, relwidth=0.48, relheight=0.7)
        self.frame_detected = tk.Label(self.root, bg="black", highlightthickness=2, highlightbackground="white")
        self.frame_detected.place(relx=0.51, rely=0.05, relwidth=0.48, relheight=0.7)

        self.input_label_overlay = tk.Label(self.root, text="Input", font=("Arial", 16, "bold"), bg="black", fg="white")
        self.input_label_overlay.place(x=25, y=self.frame_original.winfo_y()+10)

        self.processed_label_overlay = tk.Label(self.root, text="AI Processed", font=("Arial", 16, "bold"), bg="black", fg="white")
        self.processed_label_overlay.place(x=int(self.root.winfo_screenwidth()/2)+10, y=self.frame_detected.winfo_y()+10)

        self.date_overlay = tk.Label(self.root, font=("Arial", 14, "bold"), bg="black", fg="cyan")
        self.date_overlay.place(x=self.root.winfo_screenwidth()-200, y=65)

        self.time_overlay = tk.Label(self.root, font=("Arial", 16, "bold"), bg="black", fg="yellow")
        self.time_overlay.place(x=self.root.winfo_screenwidth()-185, y=85)

        self.frame_time_overlay = tk.Label(self.root, font=("Arial", 14, "bold"), bg="black", fg="orange")
        self.frame_time_overlay.place(x=self.root.winfo_screenwidth()-225, y=110)

        console_frame = tk.Frame(self.root, bg="#e8e8e8", highlightbackground="black", highlightthickness=1)
        console_frame.place(relx=0, rely=0.78, relwidth=1, relheight=0.22)
        table_frame = tk.Frame(console_frame, bg="black", padx=2, pady=2)
        table_frame.pack(expand=True)

        rows = 3
        cols = (len(traffic_classes) + rows - 1) // rows
        self.counter_labels.clear()
        idx = 0
        for c in range(cols):
            for r in range(rows):
                if idx >= len(traffic_classes):
                    break
                obj = traffic_classes[idx]
                cell_frame = tk.Frame(table_frame, bg="white", highlightbackground="black", highlightthickness=1, padx=10, pady=5)
                cell_frame.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
                tk.Label(cell_frame, text=obj.title(), font=("Arial", 13, "bold"), bg="white", anchor="w", width=15).pack(side="left", padx=5)
                count_label = tk.Label(cell_frame, text="0", font=("Arial", 13, "bold"), bg="white", fg="blue", width=6, anchor="e")
                count_label.pack(side="left", padx=5)
                self.counter_labels[obj] = count_label
                idx += 1

        if self.mode == "image":
            self.show_image()
        else:
            self.cap = cv2.VideoCapture(self.source_path)
            self.frame_queue = queue.Queue(maxsize=2)
            self.running = True
            self.paused = False
            threading.Thread(target=self.process_frames, daemon=True).start()
            self.update_video_frame()

    def resize_proportionally(self, img, target_w, target_h):
        h, w = img.shape[:2]
        scale = min(target_w / w, target_h / h)
        new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(img, (new_w, new_h))
        background = np.zeros((target_h, target_w, 3), dtype=np.uint8)
        y_off, x_off = (target_h - new_h) // 2, (target_w - new_w) // 2
        background[y_off:y_off + new_h, x_off:x_off + new_w] = resized
        return background

    def show_image(self):
        img = cv2.imread(self.source_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        detected = img.copy()
        counts = {obj: 0 for obj in traffic_classes}
        results = model(img, verbose=False)
        for box, cls_id in zip(results[0].boxes.xyxy, results[0].boxes.cls):
            cls_name = model.names[int(cls_id)].lower()
            if cls_name in counts:
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(detected, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(detected, cls_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                counts[cls_name] += 1
        for obj, label in self.counter_labels.items():
            label.config(text=str(counts.get(obj, 0)))
        display_w = int(self.root.winfo_screenwidth() * 0.48)
        display_h = int(self.root.winfo_screenheight() * 0.7)
        img_disp = self.resize_proportionally(img, display_w, display_h)
        det_disp = self.resize_proportionally(detected, display_w, display_h)
        #cv2.putText(img_disp, "Input", (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        #cv2.putText(det_disp, "AI Processed", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        img1 = ImageTk.PhotoImage(Image.fromarray(img_disp))
        img2 = ImageTk.PhotoImage(Image.fromarray(det_disp))
        self.frame_original.configure(image=img1)
        self.frame_original.image = img1
        self.frame_detected.configure(image=img2)
        self.frame_detected.image = img2


    def process_frames(self):
        while self.running and self.cap.isOpened():
            if self.paused:
                continue

            ret, frame = self.cap.read()
            if not ret:
                if loop_video:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    break

            frame = cv2.flip(frame, 1)
            detected = frame.copy()

            counts = {obj: 0 for obj in traffic_classes}
            results = model(frame, verbose=False)
            for box, cls_id in zip(results[0].boxes.xyxy, results[0].boxes.cls):
                cls_name = model.names[int(cls_id)].lower()
                if cls_name in counts:
                    x1, y1, x2, y2 = map(int, box)
                    cv2.rectangle(detected, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    counts[cls_name] += 1

            if self.frame_queue.full():
                try: self.frame_queue.get_nowait()
                except: pass
            self.frame_queue.put((frame, detected, counts))

    def update_video_frame(self):
        if not self.running:
            return

        try:
            frame, detected, counts = self.frame_queue.get_nowait()
        except queue.Empty:
            self.root.after(30, self.update_video_frame)
            return

        for obj, label in self.counter_labels.items():
            label.config(text=str(counts.get(obj, 0)))

        #in seconds
        current_frame_time: float = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        current_frame_time_str: str = self.format_video_time(current_frame_time)

        now = datetime.datetime.now().strftime("%H:%M:%S")
        today = datetime.datetime.now().strftime("%d-%m-%Y")
        self.time_overlay.config(text=now)
        self.date_overlay.config(text=today)
        self.frame_time_overlay.config(text=f"{current_frame_time_str}")

        target_w = int(self.root.winfo_screenwidth() * 0.48)
        target_h = int(self.root.winfo_screenheight() * 0.7)
        frame_disp = self.resize_proportionally(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), target_w, target_h)
        det_disp = self.resize_proportionally(cv2.cvtColor(detected, cv2.COLOR_BGR2RGB), target_w, target_h)

        if self.img1 is None:
            self.img1 = ImageTk.PhotoImage(Image.fromarray(frame_disp))
        else:
            self.img1.paste(Image.fromarray(frame_disp))

        if self.img2 is None:
            self.img2 = ImageTk.PhotoImage(Image.fromarray(det_disp))
        else:
            self.img2.paste(Image.fromarray(det_disp))

        self.frame_original.configure(image=self.img1)
        self.frame_detected.configure(image=self.img2)

        self.root.after(30, self.update_video_frame)

    def format_video_time(self, current_time_sec: float):
        total_ms = int(current_time_sec * 1000)
        hours = total_ms // (3600*1000)
        minutes = (total_ms % (3600*1000)) // (60*1000)
        seconds = (total_ms % (60*1000)) // 1000
        milliseconds = total_ms % 1000
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{milliseconds:03d}"

    def on_close(self):
        self.running = False
        self.paused = False
        if self.cap:
            try:
                self.cap.release()
            except:
                pass
            self.cap = None
        self.root.after(200, self.root.destroy)

if __name__ == "__main__":
    model = load_yolo_model('yolov8n.pt')
    root = tk.Tk()
    app = TrafficDetectionApp(root)
    root.mainloop()

