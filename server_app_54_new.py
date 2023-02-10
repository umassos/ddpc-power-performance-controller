import socket
import threading
import json
import os
import argparse

def allocatePower(allocatedPower):
    os.system(f"echo {allocatedPower} | sudo tee /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw")
    os.system(f"echo {allocatedPower} | sudo tee /sys/class/powercap/intel-rapl/intel-rapl:1/constraint_0_power_limit_uw")


def allocateCore(machineName, allocatedNumberOfCores):
    os.system(f"virsh setvcpus {machineName} {allocatedNumberOfCores} --live")


def handle(sock, addr):
    print(f"New request from the Measurement Program at the address {addr}")

    data = sock.recv(1024)

    try:
        receivedValue = json.loads(data)

        for i in receivedValue:
            appPath = i
            coreOrPowerInfo = receivedValue[i]

        if int(coreOrPowerInfo) <= 32:

            if str(appPath) == "/gw/":
                allocateCore("WikiImage_German3", coreOrPowerInfo)

            elif str(appPath) == "/wrk2-api/":
                allocateCore("ubuntu_18_04_guest4", coreOrPowerInfo)

        else:
            allocatePower(coreOrPowerInfo)

    except ValueError:
        print("Received content was not a valid JSON!")

    ## Send ACK to the workload generator...
    sentMessage = "CLOSE"
    sock.send(json.dumps(sentMessage).encode())

    sock.close()
    print(f"Disconnected from {addr}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()

    ap.add_argument("-pb", "--powerbudget", type=int, required=True, help="Allocated power budget")
    ap.add_argument("-vm", "--virtualmachine", required=True, help="Name of virtual machine")
    ap.add_argument("-c", "--core", type=int, required=True, help="Allocated number of cores")
    
    args = ap.parse_args()

    allocatePower(args.powerbudget)
    allocateCore(args.virtualmachine, args.core)

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(('192.168.245.54', 8099))
    s.listen(100)
    print('Waiting for connection...')

    while True:
        sock, addr = s.accept()
        t = threading.Thread(target = handle, args = (sock, addr))
        t.start()