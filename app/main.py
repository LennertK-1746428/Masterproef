import tkinter as tk
import tkinter.font as tkFont
from tkinter import IntVar
import threading
from app.predictor_thread import *
from app.config import *
import socket
import time
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

# globals
RUNNING = False
capture_thread = None

# init window
window = tk.Tk()
window.title("OpenVPN Fingerprinting App")
window.geometry("1000x600")
window.resizable(0, 0)  # fixed size

# determine fonts
label_font = tkFont.Font(family="Helvetica", size=11)
title_font = tkFont.Font(family="Helvetica", size=15, weight="bold")


########################
# Left frame with info #
########################

info_frame = tk.Frame(master=window, width=400, height=500, highlightbackground="black", highlightthickness=1)
info_frame.pack(fill=tk.Y, side=tk.LEFT)

# IP label
ip_label = tk.Label(master=info_frame, text="Local IP address", font=label_font)
ip_entry = tk.Entry(master=info_frame, font=label_font)
ip_entry.insert(0, local_ip)
ip_label.pack(side=tk.TOP, anchor="nw", padx=20, pady=5)    # padx = (left, right), pady = (top, bottom)
ip_entry.pack(side=tk.TOP, anchor="nw",  padx=20, pady=5)

# Interface
iface_label = tk.Label(master=info_frame, text="Interface", font=label_font)
iface_entry = tk.Entry(master=info_frame, font=label_font)
iface_entry.insert(0, "WiFi")
iface_label.pack(side=tk.TOP, anchor="nw", padx=20, pady=(15, 5))
iface_entry.pack(side=tk.TOP, anchor="nw",  padx=20, pady=5)

# Server port
server_label = tk.Label(master=info_frame, text="Server port", font=label_font)
server_entry = tk.Entry(master=info_frame, font=label_font)
server_entry.insert(0, "1194")
server_label.pack(side=tk.TOP, anchor="nw", padx=20, pady=(15, 5))
server_entry.pack(side=tk.TOP, anchor="nw", padx=20, pady=5)

# Prediction interval
pred_interval_label = tk.Label(master=info_frame, text="Prediction interval (s)", font=label_font)
pred_interval_entry = tk.Entry(master=info_frame, font=label_font)
pred_interval_entry.insert(0, "60")
pred_interval_label.pack(side=tk.TOP, anchor="nw", padx=20, pady=(15, 5))
pred_interval_entry.pack(side=tk.TOP, anchor="nw", padx=20, pady=5)

# Use IP TTL for OS prediction
ttl_checkbox_value = IntVar()
ttl_checkbox_value.set(1)
ttl_checkbox = tk.Checkbutton(master=info_frame, font=label_font, text="Use IP TTL", variable=ttl_checkbox_value)
ttl_checkbox.pack(side=tk.TOP, anchor="nw", padx=15, pady=(15, 5))


##########################################
# Top right frame with start stop status #
##########################################

start_stop_frame = tk.Frame(master=window, width=800, height=100, highlightbackground="black", highlightthickness=1)
start_stop_frame.pack(fill=tk.X, side=tk.TOP)

# buttons

def start():
    global RUNNING, start_button, stop_button, status_value_label
    start_capture_thread()
    RUNNING = True
    start_button["state"] = "disabled"
    stop_button["state"] = "normal"
    status_value_label["text"] = "Running"
    status_value_label["fg"] = "green"

def stop():
    global RUNNING, start_button, stop_button, status_value_label
    stop_capture_thread()
    RUNNING = False
    start_button["state"] = "normal"
    stop_button["state"] = "disabled"
    status_value_label["text"] = "Not Running"
    status_value_label["fg"] = "red"

start_button = tk.Button(master=start_stop_frame, width=10, text="Start", command=start, font=label_font)
stop_button = tk.Button(master=start_stop_frame, width=10, text="Stop", command=stop, font=label_font)

start_button.pack(side=tk.LEFT)
stop_button.pack(side=tk.LEFT)

# status label

status_label = tk.Label(master=start_stop_frame, text="Status: ", font=label_font)
status_value_label = tk.Label(master=start_stop_frame, text="", font=label_font, fg="green")

status_label.pack(side=tk.LEFT, padx=(50, 0))
status_value_label.pack(side=tk.LEFT)


#######################################
# Bottom right frame with predictions #
#######################################

# Canvas with scrollbar
def on_configure(event):
    # update scrollregion after starting 'mainloop'
    # when all widgets are in canvas
    canvas.configure(scrollregion=canvas.bbox('all'))

# init canvas, frame, and scrollbar
canvas = tk.Canvas(window)
prediction_frame = tk.Frame(master=canvas, width=800, height=500)
scrollbar = tk.Scrollbar(window, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

# pack items
scrollbar.pack(side=tk.RIGHT, fill='y')
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# do some additional stuff
canvas.create_window((4,4), window=prediction_frame, anchor="nw")
prediction_frame.bind("<Configure>", lambda event, canvas=canvas: on_configure(canvas))


# frame

# prediction_frame.pack_propagate(0)  # do NOT shrink to fit child elements exactly
# prediction_frame.pack(fill=tk.BOTH, expand=True)

#####################
# Prediction thread #
#####################

def insert_prediction_label(text):
    global prediction_frame
    label = tk.Label(master=prediction_frame, text=text, font=label_font)
    label.pack(side=tk.TOP, anchor="nw", padx=10, pady=2)

def start_capture_thread():
    global capture_thread
    if capture_thread is not None and capture_thread.is_alive():
        print("Waiting for previous process to end..")
        capture_thread.join()
    capture_thread = None
    capture_thread = StoppableThread(target=predict_traffic, args=(insert_prediction_label, ip_entry.get(), iface_entry.get(), int(server_entry.get()),
        int(pred_interval_entry.get()), int(ttl_checkbox_value.get()),))
    capture_thread.start()

def stop_capture_thread():
    global capture_thread
    if capture_thread is not None:
        capture_thread.stop()

# status begins not running
stop()

# keep window running and listening for events
window.mainloop()