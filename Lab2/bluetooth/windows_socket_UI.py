import socket
import threading
from collections import deque
import signal
import time
import json

server_addr = 'E4:5F:01:FC:E8:32'
server_port = 1

buf_size = 1024

client_sock = None
server_sock = None
sock = None

exit_event = threading.Event()

message_queue = deque([])
output = ""

dq_lock = threading.Lock()
output_lock = threading.Lock()

def handler(signum, frame):
    exit_event.set()

signal.signal(signal.SIGINT, handler)

def start_client():
    global sock
    global dq_lock
    global output_lock
    global exit_event
    global message_queue
    global output
    global server_addr
    global server_port
    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    sock.settimeout(10)
    sock.connect((server_addr,server_port))
    sock.settimeout(None)
    print("after connect")
    sock.setblocking(False)
    while not exit_event.is_set():
        if dq_lock.acquire(blocking=False):
            if(len(message_queue) > 0):
                try:
                    sent = sock.send(bytes(message_queue[0], 'utf-8'))
                except Exception as e:
                    exit_event.set()
                    continue
                if sent < len(message_queue[0]):
                    message_queue[0] = message_queue[0][sent:]
                else:
                    message_queue.popleft()
            dq_lock.release()
        
        if output_lock.acquire(blocking=False):
            data = ""
            telemetry = []
            try:
                try:
                    data = sock.recv(1024).decode("utf-8")
                    print(data)
                    if data.startswith("{") and data.endswith("}"):
                        telemetry = data.split(", ")
                        ent_direction.delete(0, tk.END)
                        ent_direction.insert(0, telemetry[0].split(": ")[1])
                        ent_speed.delete(0, tk.END)
                        ent_speed.insert(0, telemetry[1].split(": ")[1])
                        ent_distance.delete(0, tk.END)
                        ent_distance.insert(0, telemetry[2].split(": ")[1])
                        ent_temperature.delete(0, tk.END)
                        ent_temperature.insert(0, telemetry[3].split(": ")[1])
                        ent_battery.delete(0, tk.END)
                        ent_battery.insert(0, telemetry[4].split(": ")[1].rstrip("}")+"v/7.4v")
                        #message_queue.append(data)
                except socket.error as e:
                    assert(1==1)
                    #no data
            except Exception as e:
                #exit_event.set()
                print(e)
                continue
            output += data
            output_split = output.split("\r\n")
            for i in range(len(output_split) - 1):
                print(output_split[i]+" from pi")
            output = output_split[-1]
            output_lock.release()
    sock.close()
    print("client thread end")


cth = threading.Thread(target=start_client)

cth.start()


print("finish join")




import tkinter as tk

window = tk.Tk()
window.title("PiCar Controller")
window.resizable(width=True, height=True)

def handle_keypress(event):
    global message_queue
    message_queue.append(event.char + "\r\n")

window.bind("<Key>", handle_keypress)

# Display command button
frm_command = tk.Frame(master=window, width=100, height=10)
lbl_command = tk.Label(
    master=frm_command,
    text="Key press: w=>forward, s=>backward, a=>turn left, d=>turn right",
    width=50,
    bg="yellow",
    fg="blue"
)
lbl_command.grid(row=0, column=0)

# Display direction
frm_direction = tk.Frame(master=window, width=100, height=10)
ent_direction = tk.Entry(master=frm_direction, width=20)
lbl_direction = tk.Label(master=frm_direction, text = "Direction:", width=10)

# Layout the direction button and entry in frm_direction
# using the .grid() geometry manager
lbl_direction.grid(row=0, column=0)
ent_direction.grid(row=0, column=1)

# Display speed
frm_speed = tk.Frame(master=window, width=100, height=10)
ent_speed = tk.Entry(master=frm_speed, width=20)
lbl_speed = tk.Label(master=frm_speed, text = "Speed:", width=10)

# Layout the speed button and entry in frm_speed
# using the .grid() geometry manager
lbl_speed.grid(row=0, column=0)
ent_speed.grid(row=0, column=1)

# Display distance
frm_distance = tk.Frame(master=window, width=100, height=10)
ent_distance = tk.Entry(master=frm_distance, width=20)
lbl_distance = tk.Label(master=frm_distance, text = "Distance:", width=10)

# Layout the speed button and entry in frm_speed
# using the .grid() geometry manager
lbl_distance.grid(row=0, column=0)
ent_distance.grid(row=0, column=1)

# Display temperature
frm_temperature = tk.Frame(master=window, width=100, height=10)
ent_temperature = tk.Entry(master=frm_temperature, width=20)
lbl_temperature = tk.Label(master=frm_temperature, text = "Temperature:", width=10)

# Layout the speed button and entry in frm_speed
# using the .grid() geometry manager
lbl_temperature.grid(row=0, column=0)
ent_temperature.grid(row=0, column=1)

# Display bettery
frm_battery = tk.Frame(master=window, width=100, height=10)
ent_battery = tk.Entry(master=frm_battery, width=20)
lbl_battery = tk.Label(master=frm_battery, text = "Battery:", width=10)

# Layout the speed button and entry in frm_speed
# using the .grid() geometry manager
lbl_battery.grid(row=0, column=0)
ent_battery.grid(row=0, column=1)


# Arrange the label and data area into window
frm_command.grid(row=0, column=0, padx=10)
frm_direction.grid(row=1, column=0, padx=10)
frm_speed.grid(row=2, column=0, padx=10)
frm_distance.grid(row=3, column=0, padx=10)
frm_temperature.grid(row=4, column=0, padx=10)
frm_battery.grid(row=5, column=0, padx=10)

window.mainloop()



#j = 0
while not exit_event.is_set():
    dq_lock.acquire()
    #msg = input("Enter your message: ") + "\r\n"
    #message_queue.append("Message from PC")
    #message_queue.append(msg)
    #message_queue.append("PC " + str(j) + " \r\n")
    dq_lock.release()
    #j += 1
    time.sleep(5)

print("Disconnected.")



print("All done from client.")
