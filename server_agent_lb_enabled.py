import socket
import sys
import os
import time
import json
import threading
import math
# from statistics import mean

VMPath = '/etc/libvirt/qemu/ubuntu_18_04_guest4.xml'

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(('192.168.245.53', 8096))
s.listen(100)
print('Waiting for connection...')

numberOfSockets = 2
idlePowerConsumptionPerSocket = 25 # In terms of Watt
VMOnRunningSocket = "8083"
disconnectSignal = {"Exit": 1}

allocation1 = os.system("echo " + str(sys.argv[1]) + " | sudo tee "
                            "/sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw")
allocation2 = os.system("echo " + str(sys.argv[1]) + " | sudo tee "
                            "/sys/class/powercap/intel-rapl/intel-rapl:1/constraint_0_power_limit_uw")

# setVcpus1 = os.system("virsh setvcpus WikiImage_German2 6 --live")
# setVcpus2 = os.system("virsh setvcpus WikiImage_German3 1 --live")
# setVcpus3 = os.system("virsh setvcpus WikiImage_German4 1 --live")
                            

def allocateCore(machineName, allocatedNumberOfCores):
    os.system("virsh setvcpus " + str(machineName) + " " + str(allocatedNumberOfCores) + " --live")


def allocatePower(allocatedPower):
    allocation1 = os.system("echo " + str(allocatedPower) + " | sudo tee "
                            "/sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw")
    allocation2 = os.system("echo " + str(allocatedPower) + " | sudo tee "
                            "/sys/class/powercap/intel-rapl/intel-rapl:1/constraint_0_power_limit_uw")


def handle(sock, addr):
    requestedPower = 0

    print('New connection from Server Agent at the address %s:%s'%addr)
   
    data = sock.recv(1024)

    try:
        receivedData = json.loads(data)
        print(receivedData)
        
    except ValueError:
        print("Received content could not be a valid JSON!")
                    
    for i in receivedData:
        requestedPower = receivedData[i]
            
    print("Requested power is " + str(requestedPower))
    allocatePower(requestedPower)

    # isVMRun = self.runNewVM()

    # if isVMRun == True:
    #     self.forwardRequests()
    
    # else:
    #     print("New VM could not be run!")
    # sock.send(json.dumps(sentMessage).encode())

    sock.close()
    print('Disconnected from %s:%s' %addr)


while True:
    sock, addr = s.accept()
    t = threading.Thread(target = handle, args = (sock,addr))
    t.start()