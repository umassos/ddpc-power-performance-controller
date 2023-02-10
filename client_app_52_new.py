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
    STEP II
    '''
    # print('Connect the socket to the server port')
    server_address = ("192.168.245.97", 8099)
    # server_address = ('localhost', 8096)

    '''
    STEP III
    '''
    sock.connect(server_address)

    # sentMessage = {"Exit": [3842, 10]}

    sock.send(json.dumps(messsage).encode())


def sendWorkloadGeneratorProgramMessage(message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    '''
    STEP II
    ''' 
    # print('Connect the socket to the server port')
    server_address = ("192.168.245.73", 8099)
    # server_address = ('localhost', 8099)

    '''
    STEP III
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
    server_address = ("192.168.245.97", 8099)
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
    server_address = ("ip_addr_machine_controller_generator", 8099)
    # server_address = ('localhost', 8099)

    '''
    STEP III
    '''
    sock.connect(server_address)

    # sentMessage = {"Exit": [3842, 10]}

    sock.send(json.dumps(message).encode())


def sendClusterAgentProgramMessage(message):
    ''' 
    STEP I
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    '''
    STEP II
    '''
    # print('Connect the socket to the server port')
    server_address = ("192.168.245.97", 8099)
    # server_address = ('localhost', 8099)

    '''
    STEP III
    '''
    sock.connect(server_address)

    # sentMessage = {"Exit": [3842, 10]}

    sock.send(json.dumps(message).encode())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()

    # ap.add_argument("-rd", "--requestduration", required=True, help="Exposure time of each request")
    ap.add_argument("-d", "--duration", type=int, required=True, help="Experiment duration")
    ap.add_argument("-s", "--sourcefolder", required=True, help="Source folder of model parameters")
    ap.add_argument("-f", "--sourcefile", required=True, help="Source file of model parameters")
    ap.add_argument("-mm", "--messagetomeasurement", required=True, help="Message to measurement program")
    ap.add_argument("-mw", "--messagetoworkload", required=True, help="Message to workload generator program")
    # ap.add_argument("-nc", "--numberofcoressetting", type=int, required=True, help="Number of cores setting")
    ap.add_argument("-mg", "--messagetomodelgenerator", required=True, help="Message to model generator program")
    ap.add_argument("-mp", "--messagetopicontrollergenerator", required=True, help="Message to pi controller generator program")
    ap.add_argument("-mc", "--messagetoclusteragentprogram", required=True, help="Message to cluster agent program")

    args = ap.parse_args()

    # numberOfCoresSetting = args.numberofcoressetting
    
    # my_thread = threading.Thread(target = sendMeasurementProgramMessage, args = (args.messagetomeasurement))
    # my_thread.start()
    
    # my_thread1 = threading.Thread(target = sendWorkloadGeneratorProgramMessage, args = (args.messagetoworkload))
    # my_thread1.start()
    
    # my_thread.join()
    # my_thread1.join()

    # my_thread2 = threading.Thread(target = sendModelParameterGeneratorProgramMessage, args = (args.messagetomodelgenerator))
    # my_thread2.start()
    # my_thread2.join()
    
    # my_thread3 = threading.Thread(target = sendPIControllerGeneratorProgramMessage, args = (args.messagetopicontrollergenerator))
    # my_thread3.start()
    # my_thread3.join()
    
    # sendClusterAgentProgramMessage(args.messagetoclusteragentprogram)

    # print(args.sourcefolder)
    # print(args.sourcefile)

    # sendMeasurementProgramMessage(args.messagetomeasurement)
    # print("Measurement program has been ran")
    # sendWorkloadGeneratorProgramMessage(args.messagetoworkload)
    # print("Workload generator program has been ran")
    # print("Waiting to finish profiling...")
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
    # sendClusterAgentProgramMessage(args.messagetoclusteragentprogram)
