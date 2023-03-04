import socket
import picar_4wd as fc
from picar_4wd.utils import cpu_temperature, power_read
import time
import json

HOST = "192.168.0.115" # IP address of your Raspberry PI
PORT = 65432          # Port to listen on (non-privileged ports are > 1023)

def move_car(keycode):

    return_data = {}
    direction = ""
    speed = []
    distance = 0.0
    if keycode.decode('utf-8') == '87\r\n':
        direction = "North"
        for i in range(10):
            fc.forward(1)
            time.sleep(0.1)
            speed.append(fc.speed_val())
            distance += fc.speed_val() * 0.1
        fc.stop()
    elif keycode.decode('utf-8') == '83\r\n':
        direction = "South"
        for i in range(10):
            fc.backward(1)
            time.sleep(0.1)
            speed.append(fc.speed_val())
            distance += fc.speed_val() * 0.1
        fc.stop()
    elif keycode.decode('utf-8') == '65\r\n':
        direction = "West"
        fc.turn_left(1)
        time.sleep(1.2)
        for i in range(10):
            fc.forward(1)
            time.sleep(0.1)
            speed.append(fc.speed_val())
            distance += fc.speed_val() * 0.1
        fc.stop()
    elif keycode.decode('utf-8') == '68\r\n':
        direction = "East"
        fc.turn_right(1)
        time.sleep(1.2)
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

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    try:
        while 1:
            client, clientInfo = s.accept()
            print("server recv from: ", clientInfo)
            data = client.recv(1024)      # receive 1024 Bytes of message in binary format
            if data != b"":     
                print("Data received:", data.decode('utf-8').rstrip())
                if data.decode('utf-8') in ['87\r\n', '83\r\n', '65\r\n', '68\r\n']:
                    print('Car moves')
                    data = json.dumps(move_car(data)).encode('utf-8')
                    print(data.decode('utf-8') + "\r\n")
                   # print(json.dumps(move_car(data)))
                   # data = json.dumps(move_car(data)).encode('utf-8')
                else:
                    fc.stop()
                    #data = json.dumps({"direction":"NA", "speed":"0.0", "distance":"0.0", "temperature":"0.0"}).encode('utf-8')
                client.sendall(data) # Echo back to client
    except: 
        print("Closing socket")
        client.close()
        s.close()    
