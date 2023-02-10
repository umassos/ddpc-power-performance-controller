import socket
import sys
import os
import time
import json
import threading
import math
import argparse
import timeit
# from statistics import mean

# logFile = "/Users/msavasci/Desktop/Research/Synthesis_Project/Designing_a_Controller/Data_Acquisition/Social_Networking_Application/haproxy_social_network.log"

logData = list()
    

def readResponseTimeFromLog(numberOfLinesToBeRead, allocatedPower, log_file, application_subpath):
    readResponses = list()

    # opening file using with() method so that file get closed after completing work 
    with open(log_file) as file: 
        # loop to read iterate last numberOfLinesToBeRead lines and store it in list
        for line in (file.readlines() [-numberOfLinesToBeRead:]):
            readResponses.append(line)

    for responses in readResponses:
        splitted = str(responses).split()
        
        if (len(splitted) < 21):
            print("The log file tried to be read does not have a valid format! Please check it!")
            break
        
        responseCodeInfo = splitted[10]
        requestedPageInfo = splitted[18]
        responseTimeInfo = splitted[20]

        if requestedPageInfo.strip().startswith(application_subpath): 
        # Mediawiki application: "/gw/"
        # Social Network application: "/wrk2-api/"

            if responseTimeInfo.strip() != "-1":

                if responseCodeInfo.strip() == "200":  
                    logData.append(str(numberOfLinesToBeRead) + "," + str(allocatedPower) + "," + str(responseTimeInfo))

    '''if len(logData) == 0:
        return 0

    return logData'''
                            

def handle(sock, addr, initial_power_budget_level, power_budget_level_duration, increment, app_server_ip, app_server_port, sampling_time, application_subpath, fileToKeepInterestedLogFileColumns, log_file):
    print(f"New request from the Workload Generator at the address of {addr}")
   
    data = sock.recv(1024)

    try:
        receivedData = json.loads(data)
        print(receivedData)
        
    except ValueError:
        print("Received content was not a valid JSON!")
                    
    for i in receivedData:
        requestRate = receivedData[i][0]
        requestDuration = receivedData[i][1]
            
    print(f"Request rate is {requestRate}")
    print(f"Request duration is {requestDuration} seconds")

    # 3842 is the termination signal received from Workload Generator.
    if requestRate == 3842:
        sentMessage = "TERMINATE"
        sock.send(json.dumps(sentMessage).encode())
        sock.close()
        print(f"Disconnected from {addr}")
        # sys.exit("Experiment is done on measurement program side!")
        # sys.exit(1)
        # os.system("python3 /workspace/pipeline-structure/ModelGenerator.py -n {} -i {} -l {} -sf {} -df {}".format(initialPowerBudgetLevel, incrementInPower, fileToKeepInterestedLogFileColumns, powerBudgetLevelDuration))
        os.system('kill -9 %d' % os.getpid())

    ## Send SUCCESS ACK to the workload generator...
    else: 
        sentMessage = "SUCCESS"

    sock.send(json.dumps(sentMessage).encode())

    sock.close()
    print(f"Disconnected from {addr}")

    ''' 
    WAIT A SECOND TO MAKE SURE WORKLOAD GENERATOR HAS BEEN LAUNCHED!
    '''
    # time.sleep(1)

    # requestDuration = (((finalPowerBudgetLevel - initialPowerBudgetLevel) / increment) + 1) * powerLevelDuration

    tempVariable = initial_power_budget_level 

    start = timeit.default_timer()
    
    while ( timeit.default_timer() - start ) <= requestDuration - 1:
        # Change the power budget levels on packages
        ''' 
        STEP I
        '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        '''
        STEP II
        ''' 
        # print('Connect the socket to the server port')
        server_address = (app_server_ip, app_server_port)
        print(server_address)
    
        '''
        STEP III
        '''
        sock.connect(server_address)
        print('Connected to application server')
    
        new_msg = {application_subpath: tempVariable}

        # sock.send(json.dumps(tempVariable).encode())
        sock.send(json.dumps(new_msg).encode())

        data = sock.recv(1024)

        try:
            receivedData = json.loads(data)
            print(f"Received ACK: {receivedData}")
        
        except ValueError:
            print("Received content was not a valid JSON!")

        sock.close()

        # allocatePower(tempVariable)
        print(f"Power budget level has been set to {tempVariable}")
        
        '''
        WE HAVE A SLEEP METHOD HERE TO PERFECTLY MAKE SURE ALLOCATED POWER BUDGET HAS BEEN IN EFFECT! 
        '''
        time.sleep(1)                   
        tmpTime = timeit.default_timer()

        while ( timeit.default_timer() - tmpTime ) <= power_budget_level_duration - 1:
            # readResponseTimeFromLog(requestRate, numberOfCoresGiven, tempVariable, logFile)
            readResponseTimeFromLog(requestRate, tempVariable, log_file, application_subpath)
            time.sleep(sampling_time)

        tempVariable += increment
        
        print(f"Exposure to set power budget level in fact took {timeit.default_timer() - tmpTime} seconds")
        
    print(f"Exposure to incoming request rate in fact took {time.time() - start} seconds")

    with open(fileToKeepInterestedLogFileColumns, 'a') as filehandle:
        filehandle.writelines("%s\n" % place for place in logData)
        filehandle.close()
        # print([place for place in logData])

    logData.clear()


def convert_from_watt_microwatt(value):
    return value * 1000000


if __name__ == "__main__":
    ## The values of the following variables will be provided by the datacenter operator.
    ap = argparse.ArgumentParser()

    ap.add_argument("-H", "--ip", default="192.168.245.97", required=False, help="Host IP address")
    ap.add_argument("-po", "--port", default=8096, required=False, help="Host port number")
    ap.add_argument("-H1", "--appserverip", default="192.168.245.54", required=False, help="App Server IP address")
    ap.add_argument("-po1", "--appserverport", default=8099, required=False, help="App Server port number")
    ap.add_argument("-ip", "--initialpowerbudgetlevel", type=int, required=True, help="Initial power budget level")
    ap.add_argument("-i", "--incrementofpower", type=int, required=True, help="Increment in power budget level")
    ap.add_argument("-fp", "--finalpowerbudgetlevel", type=int, required=True, help="Final power budget level")
    ap.add_argument("-pd", "--powerbudgetlevelduration", type=int, required=True, help="Final power budget level")
    # ap.add_argument("-c", "--numberofcores", required=True, type=int, help="Number of allocated cores")
    ap.add_argument("-s", "--samplingtime", type=int, required=True, help="Sampling time")
    ap.add_argument("-p", "--applicationsubpath", required=True, help="Application subpath")
    ap.add_argument("-lf", "--logfile", required=True, help="Log file")
    ap.add_argument("-f", "--filename", required=True, help="File for storing collected data")

    args = ap.parse_args()

    initialPowerBudgetLevel = convert_from_watt_microwatt(int(args.initialpowerbudgetlevel))
    increment = convert_from_watt_microwatt(int(args.incrementofpower))
    finalPowerBudgetLevel = convert_from_watt_microwatt(int(args.finalpowerbudgetlevel))
    # numberOfCoresGiven = args.numberofcores

    my_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn = (args.ip, 8094)
    my_sock.bind(conn) 
    my_sock.listen(100)
    print('Waiting for connection...')

    while True:
        sock, addr = my_sock.accept()
        t = threading.Thread(target = handle, args = (sock, addr, initialPowerBudgetLevel, int(args.powerbudgetlevelduration), increment, args.appserverip, int(args.appserverport), int(args.samplingtime), args.applicationsubpath, args.filename, args.logfile))
        t.start()