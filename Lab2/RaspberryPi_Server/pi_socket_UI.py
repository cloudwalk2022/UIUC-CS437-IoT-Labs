import socket
import threading
from collections import deque
import signal
import time
import picar_4wd as fc
from picar_4wd.utils import cpu_temperature, power_read
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

def move_car(keycode):

    return_data = {}
    direction = ""
    speed = []
    distance = 0.0

    if keycode == 'w\r\n':
        direction = "North"
        for i in range(10):
            fc.forward(1)
            time.sleep(0.1)
            speed.append(fc.speed_val())
            distance += fc.speed_val() * 0.1
        fc.stop()
    elif keycode == 's\r\n':
        direction = "South"
        for i in range(10):
            fc.backward(1)
            time.sleep(0.1)
            speed.append(fc.speed_val())
            distance += fc.speed_val() * 0.1
        fc.stop()
    elif keycode == 'a\r\n':
        direction = "West"
        fc.turn_left(1)
        time.sleep(1.0)
        for i in range(10):
            fc.forward(1)
            time.sleep(0.1)
            speed.append(fc.speed_val())
            distance += fc.speed_val() * 0.1
        fc.stop()
    elif keycode == 'd\r\n':
        direction = "East"
        fc.turn_right(1)
        time.sleep(1.0)
        for i in range(10):
            fc.forward(1)
            time.sleep(0.1)
            speed.append(fc.speed_val())
            distance += fc.speed_val() * 0.1
        fc.stop()
    else:
        fc.stop()

    avg_speed = sum(speed[1:])/(len(speed) - 1)
    return_data["direction"] = direction
    return_data["speed"] = round(avg_speed, 2)
    return_data["distance"] = round(distance, 2)
    return_data["temperature"] = round(cpu_temperature(), 2)
    return_data["battery"] = power_read()
    return return_data

fc.start_speed_thread()


def handler(signum, frame):
    exit_event.set()

signal.signal(signal.SIGINT, handler)

def start_client():
    global server_addr
    global server_port
    global server_sock
    global sock
    global exit_event
    global message_queue
    global output
    global dq_lock
    global output_lock
    server_sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    server_sock.bind((server_addr, server_port))
    server_sock.listen(1)
#    server_sock.settimeout(10)
    print("Server is running")
    sock, address = server_sock.accept()
    print("Connected")
    server_sock.settimeout(None)
    sock.setblocking(0)
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
            try:
                try:
                    data = sock.recv(1024).decode('utf-8')
#                   if data != b"":     
                    if data in ['w\r\n','s\r\n','a\r\n','d\r\n']:
                        print('Car moves')
                        data = json.dumps(move_car(data))
                        print(data)
                        message_queue.append(data)
                    else:
                        print("You pressed the \""+data.rstrip()+"\" key, the car will not move.")
                        message_queue.append("Please only press w,s,a,d keys.")
                except socket.error as e:
                    assert(1==1)
                    #no data

            except Exception as e:
                exit_event.set()
                continue
#            output += data
#            output_split = output.split("\r\n")
#            for i in range(len(output_split) - 1):
#                print(output_split[i])
#            output = output_split[-1]
            output_lock.release()
    server_sock.close()
    sock.close()
    print("client thread end")


cth = threading.Thread(target=start_client)

cth.start()

j = 0
while not exit_event.is_set():
    dq_lock.acquire()
    #message_queue.append("RPi " + str(j) + " \r\n")
    dq_lock.release()
    j += 1
    time.sleep(5)


print("Disconnected.")


print("All done.")
