import socket
import threading
import json
import os


def handle(sock, addr):
    print(f"New request from the Client App at the address of {addr}")

    data = sock.recv(10240)

    try:
        receivedCommand = json.loads(data)
        print(receivedCommand)
        os.system(str(receivedCommand))

    except ValueError:
        print("Received content is not a valid JSON!")

    ## Send ACK to the workload generator...
    sentMessage = "SUCCESS"
    sock.send(json.dumps(sentMessage).encode())

    sock.close()
    print(f"Disconnected from {addr}")


if __name__ == "__main__":
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(('192.168.245.91', 8099))
    s.listen(100)
    print('Waiting for connection...')

    while True:
        sock, addr = s.accept()
        t = threading.Thread(target = handle, args = (sock, addr))
        t.start()