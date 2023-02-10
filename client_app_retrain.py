import os
import socket
import json
import argparse
import time
import threading
import paramiko

ip_addr_machine_controller_generator = "128.119.40.235"

def sendMeasurementProgramMessage(messsage):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    '''
    STEP I
    '''
    # print('Connect the socket to the server port')
    server_address = ("192.168.245.91", 8099)
    # server_address = ('localhost', 8096)

    '''
    STEP II
    '''
    sock.connect(server_address)

    # sentMessage = {"Exit": [3842, 10]}

    sock.send(json.dumps(messsage).encode())


def sendWorkloadGeneratorProgramMessage(message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    '''
    STEP I
    ''' 
    # print('Connect the socket to the server port')
    server_address = ("192.168.245.73", 8099)
    # server_address = ('localhost', 8099)

    '''
    STEP II
    '''
    sock.connect(server_address)

    # sentMessage = {"Exit": [3842, 10]}

    sock.send(json.dumps(message).encode())


def sendModelParameterGeneratorProgramMessage(message):
    ''' 
    STEP I
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    '''
    STEP II
    '''
    # print('Connect the socket to the server port')
    server_address = ("192.168.245.91", 8099)
    # server_address = ('localhost', 8099)

    '''
    STEP III
    '''
    sock.connect(server_address)

    # sentMessage = {"Exit": [3842, 10]}

    sock.send(json.dumps(message).encode())


def sendPIControllerGeneratorProgramMessage(message):
    ''' 
    STEP I
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    '''
    STEP II
    '''
    # print('Connect the socket to the server port')
    server_address = (ip_addr_machine_controller_generator, 8099)
    # server_address = ('localhost', 8099)

    '''
    STEP III
    '''
    sock.connect(server_address)

    # sentMessage = {"Exit": [3842, 10]}

    sock.send(json.dumps(message).encode())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()

    ap.add_argument("-d", "--duration", type=int, required=True, help="Experiment duration")
    ap.add_argument("-s", "--sourcefolder", required=True, help="Source folder of model parameters")
    ap.add_argument("-f", "--sourcefile", required=True, help="Source file of model parameters")
    ap.add_argument("-mm", "--messagetomeasurement", required=True, help="Message to measurement program")
    ap.add_argument("-mw", "--messagetoworkload", required=True, help="Message to workload generator program")
    ap.add_argument("-mg", "--messagetomodelgenerator", required=True, help="Message to model generator program")
    ap.add_argument("-mp", "--messagetopicontrollergenerator", required=True, help="Message to pi controller generator program")

    args = ap.parse_args()

    sendMeasurementProgramMessage(args.messagetomeasurement)
    print("Measurement program has been ran")
    sendWorkloadGeneratorProgramMessage(args.messagetoworkload)
    print("Workload generator program has been ran")
    print("Waiting to finish profiling...")
    time.sleep(args.duration + 60)
    sendModelParameterGeneratorProgramMessage(args.messagetomodelgenerator)
    time.sleep(20)
    print("Model parameters has been generated")
    ssh = paramiko.SSHClient()
    ssh.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
    ssh.connect(ip_addr_machine_controller_generator, username='', password='')
    sftp = ssh.open_sftp()
    sftp.put(args.sourcefolder, os.path.join('/Users/msavasci/Desktop/Research/Obelix-Pipeline-Structure/', args.sourcefile))
    sftp.close()
    ssh.close()
    print("Waiting for copying model file...")
    time.sleep(3)
    sendPIControllerGeneratorProgramMessage(args.messagetopicontrollergenerator)
    print("Waiting to finish controller generation...")
    time.sleep(30)
