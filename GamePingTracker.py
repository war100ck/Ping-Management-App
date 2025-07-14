import sys
import subprocess
import tkinter.messagebox as messagebox

# Функция для проверки и установки отсутствующих модулей
def install_missing_packages():
    required_packages = {
        'ttkbootstrap': 'ttkbootstrap',
        'psutil': 'psutil',
        'pythonping': 'pythonping',
        'requests': 'requests'
    }
    
    missing_packages = []
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        message = f"To operate the program, you need to install the following modules: {', '.join(missing_packages)}.\nInstall now?"
        if messagebox.askyesno("Installing modules", message):
            for package in missing_packages:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                except subprocess.CalledProcessError:
                    messagebox.showerror("Ошибка", f"Failed to install module {package}")
                    sys.exit(1)
            messagebox.showinfo("Success", "The modules have been installed successfully. Please restart the program..")
            sys.exit(0)

# Проверяем модули до всех остальных импортов
if not hasattr(sys, 'frozen'):
    install_missing_packages()

# Теперь импортируем все остальные модули
import tkinter as tk
from tkinter import filedialog, colorchooser
import ttkbootstrap as ttkb
from tkinter import ttk
import psutil
import time
import pythonping
from threading import Thread, Event
import ctypes
import requests
import json

def find_server_ips(process_name):
    server_ips = []
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            try:
                connections = psutil.net_connections(kind='inet')
                for conn in connections:
                    if conn.pid == proc.info['pid'] and conn.raddr:
                        server_ips.append(conn.raddr.ip)
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue
    return list(set(server_ips))

def ping_server(server_ip):
    try:
        response = pythonping.ping(server_ip, count=1, timeout=1, verbose=False)
        if response.success():
            return response.rtt_avg_ms
        else:
            return None
    except Exception:
        return None

def get_ip_info(ip):
    try:
        response = requests.get(f"http://ipinfo.io/{ip}/json")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception:
        return None

def update_stats(label, process_name, stop_event, ip_info_label, ping_color_var, font_style_var):
    while not stop_event.is_set():
        if not label.winfo_exists():
            break
        server_ips = find_server_ips(process_name)
        
        if server_ips:
            best_ping = float('inf')
            best_ip = None
            
            for ip in server_ips:
                ping = ping_server(ip)
                if ping is not None:
                    if ping < best_ping:
                        best_ping = ping
                        best_ip = ip

            if best_ip:
                if label.winfo_exists():
                    label.config(text=f"{best_ping:.2f} ms", fg=ping_color_var.get())
                ip_info = get_ip_info(best_ip)
                if ip_info:
                    ip_info_text = (
                        f"IP: {best_ip}\n"
                        f"City: {ip_info.get('city', 'Unknown')}\n"
                        f"Region: {ip_info.get('region', 'Unknown')}\n"
                        f"Country: {ip_info.get('country', 'Unknown')}\n"
                        f"Organization: {ip_info.get('org', 'Unknown')}\n"
                    )
                else:
                    ip_info_text = f"IP: {best_ip}\nInformation not available"
                if ip_info_label.winfo_exists():
                    ip_info_label.config(text=ip_info_text)
            else:
                if label.winfo_exists():
                    label.config(text="Unreachable", fg=ping_color_var.get())
                if ip_info_label.winfo_exists():
                    ip_info_label.config(text="IP: Unreachable")

        else:
            if label.winfo_exists():
                label.config(text="Game process not found or server not detected", fg=ping_color_var.get())
            if ip_info_label.winfo_exists():
                ip_info_label.config(text="IP: Unreachable")

        time.sleep(1)

def start_stats_thread(label, process_name, stop_event, ip_info_label, ping_color_var, font_style_var):
    stop_event.clear()
    thread = Thread(target=update_stats, args=(label, process_name, stop_event, ip_info_label, ping_color_var, font_style_var))
    thread.daemon = True
    thread.start()
    return thread

def select_exe_file(entry):
    file_path = filedialog.askopenfilename(
        title="Select .exe File",
        filetypes=[("Executable Files", "*.exe")]
    )
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

def choose_color(ping_color_var):
    color_code = colorchooser.askcolor(title="Select Ping Text Color")[1]
    if color_code:
        ping_color_var.set(color_code)

def update_size(label, frame, size_value, font_style_var):
    if label.winfo_exists():
        size = int(size_value)
        current_style = font_style_var.get()
        label.config(font=("Helvetica", size, current_style))
        frame.config(bd=size // 10)

def update_transparency(ping_window, transparency_value):
    if ping_window and ping_window.winfo_exists():
        alpha = transparency_value / 100
        ping_window.attributes("-alpha", alpha)

def update_font_style(label, font_style_var):
    if label.winfo_exists():
        style = font_style_var.get()
        current_size = label.cget("font").split()[1]
        label.config(font=("Helvetica", current_size, style))

def make_window_draggable(window):
    def on_start_drag(event):
        window._drag_data = {'x': event.x, 'y': event.y}

    def on_drag(event):
        delta_x = event.x - window._drag_data['x']
        delta_y = event.y - window._drag_data['y']
        new_x = window.winfo_x() + delta_x
        new_y = window.winfo_y() + delta_y
        window.geometry(f'+{new_x}+{new_y}')

    window.bind('<Button-1>', on_start_drag)
    window.bind('<B1-Motion>', on_drag)

    hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
    ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0004)

def open_ping_window(root, process_name, stop_event, ping_color_var, text_size_var, transparency_var, font_style_var, ip_info_label, window_position):
    process_name = process_name.split("/")[-1]
    ping_window = tk.Toplevel(root)
    ping_window.title("Ping to Game Server")
    ping_window.overrideredirect(True)
    ping_window.attributes("-topmost", True)

    make_window_draggable(ping_window)

    if window_position:
        ping_window.geometry(f'+{window_position[0]}+{window_position[1]}')

    frame = tk.Frame(ping_window, bg="black", bd=int(text_size_var.get()) // 10, relief="solid")
    frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    label = tk.Label(frame, text="0.00 ms", font=("Helvetica", int(text_size_var.get()), font_style_var.get()), bg="black", fg=ping_color_var.get())
    label.pack(padx=10, pady=10, expand=True)

    def update_text_size(*args):
        if label.winfo_exists() and frame.winfo_exists():
            update_size(label, frame, text_size_var.get(), font_style_var)

    def update_text_color(*args):
        if label.winfo_exists():
            label.config(fg=ping_color_var.get())

    def update_window_transparency(*args):
        if ping_window and ping_window.winfo_exists():
            update_transparency(ping_window, transparency_var.get())

    def update_text_style(*args):
        if label.winfo_exists():
            update_font_style(label, font_style_var)

    if hasattr(text_size_var, '_trace_id'):
        try:
            text_size_var.trace_remove("w", text_size_var._trace_id)
        except tk.TclError:
            pass
    if hasattr(ping_color_var, '_trace_id'):
        try:
            ping_color_var.trace_remove("w", ping_color_var._trace_id)
        except tk.TclError:
            pass
    if hasattr(transparency_var, '_trace_id'):
        try:
            transparency_var.trace_remove("w", transparency_var._trace_id)
        except tk.TclError:
            pass
    if hasattr(font_style_var, '_trace_id'):
        try:
            font_style_var.trace_remove("w", font_style_var._trace_id)
        except tk.TclError:
            pass

    text_size_var._trace_id = text_size_var.trace("w", update_text_size)
    ping_color_var._trace_id = ping_color_var.trace("w", update_text_color)
    transparency_var._trace_id = transparency_var.trace("w", update_window_transparency)
    font_style_var._trace_id = font_style_var.trace("w", update_text_style)

    start_stats_thread(label, process_name, stop_event, ip_info_label, ping_color_var, font_style_var)

    return ping_window

def save_settings_to_file(settings):
    with open('settings.json', 'w') as file:
        json.dump(settings, file, indent=4)

def load_settings_from_file():
    try:
        with open('settings.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

class PingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Ping Tracker")
        self.root.geometry("760x355")
        self.root.minsize(760, 355)

        self.ping_window = None
        self.stop_event = Event()
        self.ping_color_var = tk.StringVar(value="white")
        self.text_size_var = tk.IntVar(value=20)
        self.transparency_var = tk.IntVar(value=100)
        self.font_style_var = tk.StringVar(value="normal")
        self.window_position = (0, 0)

        style = ttk.Style()
        style.configure('TButton', padding=6, relief="flat", background="#007bff")
        style.map('TButton', background=[('active', "#0056b3")])
        style.configure('TMenubutton', padding=6, relief="flat", background="#007bff")
        style.map('TMenubutton', background=[('active', "#0056b3")])

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        frame_top = ttk.Frame(main_frame)
        frame_top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(5, 10))

        self.file_entry = ttk.Entry(frame_top)
        self.file_entry.insert(0, "Select Game (.exe) File:")
        self.file_entry.bind("<FocusIn>", lambda e: self.file_entry.delete(0, tk.END) if self.file_entry.get() == "Select Game (.exe) File:" else None)
        self.file_entry.bind("<FocusOut>", lambda e: self.file_entry.insert(0, "Select Game (.exe) File:") if not self.file_entry.get() else None)
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        file_button = ttk.Button(frame_top, text="Browse", command=lambda: select_exe_file(self.file_entry))
        file_button.pack(side=tk.LEFT, padx=5)

        save_button = ttk.Button(frame_top, text="Save Settings", command=self.save_settings)
        save_button.pack(side=tk.LEFT, padx=5)

        frame_middle = ttk.Frame(main_frame)
        frame_middle.pack(expand=True, fill=tk.BOTH, padx=10, pady=(5, 5))

        frame_middle.columnconfigure(0, weight=35)
        frame_middle.columnconfigure(1, weight=65)

        frame_info = ttk.LabelFrame(frame_middle, text="IP Information", padding=5)
        frame_info.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        frame_settings = ttk.LabelFrame(frame_middle, text="Settings", padding=5)
        frame_settings.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        frame_middle.rowconfigure(0, weight=1)
        frame_middle.columnconfigure(0, weight=1)
        frame_middle.columnconfigure(1, weight=1)

        self.ip_info_label = ttk.Label(frame_info, text="IP: Unavailable", anchor="w", justify=tk.LEFT)
        self.ip_info_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        settings_frame = ttk.Frame(frame_settings)
        settings_frame.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X)

        self.color_button = ttk.Button(settings_frame, text="Choose Ping Text Color", command=lambda: choose_color(self.ping_color_var))
        self.color_button.pack(side=tk.LEFT, padx=5)

        font_style_options = ["normal", "bold", "italic", "underline"]
        self.font_style_var = tk.StringVar(value="normal")
        font_style_menu = ttk.OptionMenu(settings_frame, self.font_style_var, *font_style_options)
        font_style_menu.pack(side=tk.LEFT, padx=5)
        font_style_menu.config(style='TMenubutton')

        self.text_size_var = tk.IntVar(value=20)
        text_size_label = ttk.Label(frame_settings, text=f"Text Size: {self.text_size_var.get()}")
        text_size_label.pack(anchor=tk.W, padx=5, pady=5)

        text_size_slider = ttk.Scale(frame_settings, from_=8, to=64, orient=tk.HORIZONTAL, variable=self.text_size_var)
        text_size_slider.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X)

        self.text_size_var.trace("w", lambda *args: text_size_label.config(text=f"Text Size: {self.text_size_var.get()}"))

        self.transparency_var = tk.IntVar(value=100)
        transparency_label = ttk.Label(frame_settings, text=f"Transparency: {self.transparency_var.get()}%")
        transparency_label.pack(anchor=tk.W, padx=5, pady=5)

        transparency_slider = ttk.Scale(frame_settings, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.transparency_var)
        transparency_slider.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X)

        self.transparency_var.trace("w", lambda *args: transparency_label.config(text=f"Transparency: {self.transparency_var.get()}%"))

        self.font_style_var.trace("w", lambda *args: font_style_menu.config(text=f"Font Style: {self.font_style_var.get()}"))

        frame_bottom = ttk.Frame(main_frame)
        frame_bottom.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(5, 10))

        start_button = ttk.Button(frame_bottom, text="Start Ping", command=self.start_ping)
        start_button.pack(side=tk.LEFT, padx=5)

        stop_button = ttk.Button(frame_bottom, text="Stop", command=self.stop_ping)
        stop_button.pack(side=tk.LEFT, padx=5)

        self.load_settings()

    def save_settings(self):
        settings = {
            "file_path": self.file_entry.get(),
            "ping_color": self.ping_color_var.get(),
            "text_size": self.text_size_var.get(),
            "transparency": self.transparency_var.get(),
            "font_style": self.font_style_var.get(),
            "window_position": (self.ping_window.winfo_x(), self.ping_window.winfo_y()) if self.ping_window and self.ping_window.winfo_exists() else (0, 0)
        }
        save_settings_to_file(settings)

    def load_settings(self):
        settings = load_settings_from_file()
        if settings:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, settings.get("file_path", "Select Game (.exe) File:"))
            self.ping_color_var.set(settings.get("ping_color", "white"))
            self.text_size_var.set(settings.get("text_size", 20))
            self.transparency_var.set(settings.get("transparency", 100))
            self.font_style_var.set(settings.get("font_style", "normal"))
            self.window_position = settings.get("window_position", (0, 0))

    def start_ping(self):
        if self.ping_window is None or not self.ping_window.winfo_exists():
            process_name = self.file_entry.get()
            if not process_name or process_name == "Select Game (.exe) File:":
                messagebox.showerror("Error", "Please select a game file.")
                return

            if self.ping_window:
                self.stop_event.set()
                self.ping_window.destroy()
                self.ping_window = None

            self.ping_window = open_ping_window(self.root, process_name, self.stop_event, self.ping_color_var, self.text_size_var, self.transparency_var, self.font_style_var, self.ip_info_label, self.window_position)
        else:
            messagebox.showinfo("Information", "Ping window is already open.")

    def stop_ping(self):
        if self.ping_window and self.ping_window.winfo_exists():
            self.window_position = (self.ping_window.winfo_x(), self.ping_window.winfo_y())
            self.save_settings()
            self.ping_window.destroy()
        self.ping_window = None
        self.stop_event.set()

if __name__ == "__main__":
    root = ttkb.Window(themename="darkly")
    app = PingApp(root)
    root.mainloop()