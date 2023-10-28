import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from matplotlib.dates import DateFormatter
from ps3webman import WebMan
import datetime


class TempMonitorApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("PS3 Temperature Monitor")
        self.geometry("300x150")

        self.create_widgets()

    def create_widgets(self):
        self.ip_label = ttk.Label(self, text="PS3 IP Address:")
        self.ip_label.pack(padx=5, pady=5)

        self.ip_entry = ttk.Entry(self)
        self.ip_entry.pack(fill=tk.X, padx=5, pady=5)
        self.ip_entry.insert(0, "10.100.102.12")

        self.port_label = ttk.Label(self, text="Port:")
        self.port_label.pack(padx=5, pady=5)

        self.port_entry = ttk.Entry(self)
        self.port_entry.pack(fill=tk.X, padx=5, pady=5)
        self.port_entry.insert(0, "80")

        self.connect_button = ttk.Button(self, text="Connect", command=self.connect_to_ps3)
        self.connect_button.pack(pady=10)

    def connect_to_ps3(self):
        ip = self.ip_entry.get()
        port = self.port_entry.get()
        self.destroy()
        start_temp_monitor(ip, port)

def start_temp_monitor(ip, port):
    root = tk.Tk()
    root.title("PS3 Temperature Monitor")
    app = TempMonitor(root, ip, port)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()

class TempMonitor(tk.Frame):
    def __init__(self, master, ip, port):
        tk.Frame.__init__(self, master)
        self.ps3 = WebMan(ip, port=port)
        self.x_data, self.cpu_data, self.rsx_data = [], [], []
        self.create_widgets()

    def create_widgets(self):
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
        self.ani = FuncAnimation(self.fig, self.update, interval=1000)
        
    def update(self, frame):
        cpu_temp, rsx_temp = self.ps3.get_temps()
        self.x_data.append(datetime.datetime.now())
        self.cpu_data.append(cpu_temp)
        self.rsx_data.append(rsx_temp)
        
        if len(self.x_data) > 20:
            self.x_data.pop(0)
            self.cpu_data.pop(0)
            self.rsx_data.pop(0)

        self.ax.clear()
        self.ax.plot(self.x_data, self.cpu_data, label='CPU Temp')
        self.ax.plot(self.x_data, self.rsx_data, label='RSX Temp')
        self.ax.set_title('PS3 CPU and RSX Temperatures')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Temperature (Celsius)')
        self.ax.legend()
        self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
        self.fig.autofmt_xdate()
        self.canvas.draw()

if __name__ == "__main__":
    app = TempMonitorApp()
    app.mainloop()

