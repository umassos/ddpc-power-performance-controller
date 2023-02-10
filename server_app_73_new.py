import json
import os
import socket
import threading

def handle(sock, addr):
    print(f"New request from the Client App Generator at the address of {addr}")

    data = sock.recv(1024)

    try:
        receivedCommand = json.loads(data)
        print(receivedCommand)
        os.system(str(receivedCommand))

    except ValueError:
        print("Received content was not a valid JSON!")

    ## Send ACK to the workload generator...
    sentMessage = "SUCCESS"
    sock.send(json.dumps(sentMessage).encode())

    sock.close()
    print('Disconnected from %s:%s' %addr)


if __name__ == "__main__":
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(('192.168.245.73', 8099))
    
    s.listen(100)
    print('Waiting for connection...')

    while True:
        sock, addr = s.accept()
        t = threading.Thread(target = handle, args = (sock, addr))
        t.start()