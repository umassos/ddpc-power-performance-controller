import socket
from xml.dom import minidom
# import libvirt
import json
import math
import os
import threading
import queue
import time
import sys
import random
import argparse
import queue

ap = argparse.ArgumentParser()

## The following parameters will be provided by the datacenter operator.
''' Parameters for App1 '''
ap.add_argument("-p1", "--applicationsubpath_1", required=True, help="Application subpath")
ap.add_argument("-sf1", "--sourcefile_1", required=True, help="File for App1 that is to be read")
ap.add_argument("-ep1", "--estimatedpower_1", required=True, help="File to keep estimated power")
ap.add_argument("-rt1", "--measuredresponsetime_1", required=True, help="File to keep measured response time")
ap.add_argument("-ev1", "--errorvalue_1", required=True, help="File to keep error value")
ap.add_argument("-dp1", "--droppercentage_1", required=False, help="File to keep drop percentage")
ap.add_argument("-er1", "--estimatednumberofrequest_1", required=False, help="File to keep estimated number of request")
ap.add_argument("-pt1", "--pterms_1", required=True, help="File to keep p terms")
ap.add_argument("-it1", "--iterms_1", required=True, help="File to keep i terms")
ap.add_argument("-op1", "--operatingpoints_1", required=True, help="File to keep operating points")
ap.add_argument("-in1", "--integrator_1", required=True, help="File to keep integrator value")
ap.add_argument("-is1", "--integralswitchonoff_1", required=False, help="File to keep integrator switch on/off value")
ap.add_argument("-um1", "--numberofusedmachines_1", required=True, help="File to keep number of used machines")
ap.add_argument("-ap1", "--allocatedpower_1", required=True, help="File to keep allocated power")

''' Common parameters '''
ap.add_argument("-lf", "--logfile", required=True, help="File to keep interested log file columns")

ap.add_argument("-t", "--tunepercentage", required=True, help="Tune percentage on Kp and Ki values")
ap.add_argument("-nl", "--numberoflinestoberead", required=True, help="Number of lines to be read")
ap.add_argument("-st", "--samplingtime", required=True, help="Sampling time")
ap.add_argument("-ri", "--referenceInput", required=True, help="Reference input")
ap.add_argument("-pb", "--powerBudget", required=True, help="Power budget")

args = vars(ap.parse_args())

''' Command Line Variables for App1 '''
applicationSubPath_1 = str(args["applicationsubpath_1"])
sourceFile_1 = str(args["sourcefile_1"])
fileToKeepEstimatedPowerData_1 = str(args["estimatedpower_1"])                          # File for estimated power data
fileToKeepMeasuredData_1 = str(args["measuredresponsetime_1"])                          # File for measured response time
fileToKeepErrorValue_1 = str(args["errorvalue_1"])                                      # File for controller input/error input
fileToKeepDropPercentage_1 = str(args["droppercentage_1"])                              # File for keeping drop percentage
fileToKeepEstimatedNumberOfRequest_1 = str(args["estimatednumberofrequest_1"])          # File for keeping estimating number of requests
fileToKeepPTerms_1 = str(args["pterms_1"])                                              # File for keeping P terms
fileToKeepITerms_1 = str(args["iterms_1"])                                              # File for keeping I terms
fileToKeepOperatingPoints_1 = str(args["operatingpoints_1"])                            # File for keeping operating point values
fileToKeepIntegrator_1 = str(args["integrator_1"])                                      # File for keeping integrator
fileToKeepIntegralSwitchOnOff_1 = str(args["integralswitchonoff_1"])                    # File for keeping integral switch on/off
fileToKeepNumberOfUsedMachines = str(args["numberofusedmachines_1"])                    # File for keeping number of to used machines
fileToKeepAllocatedPowerData = str(args["allocatedpower_1"])                            # File for allocated power data

''' Common Variables '''
fileToKeepInterestedLogFileColumns = str(args["logfile"])                               # File for interested apache log file columns

tunePercentage = float(args["tunepercentage"])
numberOfLinesToBeRead = int(args["numberoflinestoberead"])                              # Read log file (number of line)
samplingTime = int(args["samplingtime"])                                                # Sampling time
refInput = float(args["referenceInput"])
powerBudget = float(args["powerBudget"])

ipToMachineNames = { '192.168.245.52': 'WikiImage_German2', '192.168.245.53': 'WikiImage_German3', '192.168.245.54': 'WikiImage_German4', '192.168.245.55': 'WikiImage_German5' }
machineToSetPower = { 'WikiImage_German2': 58, 'WikiImage_German3': 58, 'WikiImage_German4': 58, 'WikiImage_German5': 58 }
VMPath = '/etc/libvirt/qemu/ubuntu_18_04_guest4.xml'

logFile = "/var/log/haproxy.log"

numberOfSockets = 2
idlePowerConsumptionPerSocket = 25 # In terms of Watt

PI_LIM_MIN = 30
PI_LIM_MAX = 58

''' Variables for App1 '''
kpValues_1 = {}
kiValues_1 = {}
powerValues_1 = {}
responseTimeValues_1 = {}
aValues_1 = {}
bValues_1 = {}

integrator_1 = 0
integralSwitchOnOff_1 = 0
intOk_1 = True
prevResponseTime_1 = 0.0
initialDetection_1 = 0
badTuningCount_1 = 0
totalTuning_1 = 0

numberOfRequests_1 = []
dropPercentage_1 = []
nameOfEnabledMachines_1 = set(ipToMachineNames.keys())

# It is used to keep all log lines
logData = []


def convertWattToMicrowatt(value):
    return value * 1000000


def convertMicrowattToWatt(value):
    return round(value / 1000000, 2)


def convertMillisecondToSecond(value):
    return round(value / 1000, 2)


def initializeKpAndKiValues():
    global kpValues_1, kiValues_1, powerValues_1, responseTimeValues_1, aValues_1, bValues_1, numberOfRequests_1
    
    with open(sourceFile_1, "r") as fileStream:

        for line in fileStream:
            currentline = line.split(",")
            kpValues_1[str(currentline[0])] = float(currentline[1])
            kiValues_1[str(currentline[0])] = float(currentline[2])
            powerValues_1[str(currentline[0])] = float(currentline[3])
            responseTimeValues_1[str(currentline[0])] = float(currentline[4])
            aValues_1[str(currentline[0])] = float(currentline[5])
            bValues_1[str(currentline[0])] = float(currentline[6])
            numberOfRequests_1.append(int(currentline[0]))


def readResponseTimeFromLog(numberOfLinesToBeRead):
    readResponses = []
    global logData

    ''' App1 (Mediawiki 1) Variables '''
    global dropPercentage_1
    numberOfRequests200ResponseCodes_1 = 0
    numberOfRequestsAllResponseCodes_1 = 0
    dictNumberOfRequests_1 = {}
    dict200Responses_1 = {}

    # opening file using with() method so that file get closed 
    # after completing work 
    with open(logFile) as file: 
        # loop to read iterate last numberOfLinesToBeRead lines 
        # and store it in list
        for line in (file.readlines() [-numberOfLinesToBeRead:]): 
            readResponses.append(line)

    for responses in readResponses:
        splitted = str(responses).split()
        
        if (len(splitted) < 21):
            continue
        
        dateTimeInfo = splitted[6][1:-1]
        responseCodeInfo = splitted[10]
        requestedPageInfo = splitted[18]
        responseTimeInfo = splitted[20]
        
        logData.append(str(dateTimeInfo + " " + requestedPageInfo + " " + responseCodeInfo + " " + responseTimeInfo))

        # print(dateTimeInfo + " " + requestedPageInfo + " " + responseCodeInfo + " " + responseTimeInfo)

        if requestedPageInfo.strip().startswith(applicationSubPath_1):
            
            if responseTimeInfo.strip() != "-1":
                numberOfRequestsAllResponseCodes_1 += 1

                dateTimeSplitted = dateTimeInfo.split(":")
                secondInfo = dateTimeSplitted[3][0:2]

                valueOfDict = dictNumberOfRequests_1.get(secondInfo, 0)
                dictNumberOfRequests_1[secondInfo] = valueOfDict + 1

                if responseCodeInfo.strip() == "200":  
                    tempList = dict200Responses_1.get(secondInfo, list())
                    tempList.append(float(responseTimeInfo))
                    dict200Responses_1[secondInfo] = tempList
                    numberOfRequests200ResponseCodes_1 += 1

    averageResponseTime_1 = 0.0
    estimatedNumberOfRequest_1 = 0

    if len(dictNumberOfRequests_1.keys()) == 0:
        return averageResponseTime_1, estimatedNumberOfRequest_1
    
    ''' It returns key with max value '''
    maxKey_1 = max(dictNumberOfRequests_1, key = dictNumberOfRequests_1.get)
    
    # print("Number of read requests: %d" %(numberOfReadRequests))
    # numberOfRequests.append(numberOfReadRequests)
    dropPercentage_1.append(100 * (numberOfRequestsAllResponseCodes_1 - numberOfRequests200ResponseCodes_1) / numberOfRequestsAllResponseCodes_1)

    if dict200Responses_1.get(maxKey_1, 0) != 0:
        averageResponseTime_1 = convertMillisecondToSecond(sum(dict200Responses_1[maxKey_1])/len(dict200Responses_1[maxKey_1]))
        estimatedNumberOfRequest_1 = len(dict200Responses_1[maxKey_1])

    return averageResponseTime_1, estimatedNumberOfRequest_1


def forwardRequests(machineName):
    os.system("echo 'enable server http_back/" + machineName + "' | socat stdio tcp4-connect:127.0.0.1:9999")


def stopForwardingRequests(machineName):
    os.system("echo 'disable server http_back/" + ipToMachineNames[machineName] + "' | socat stdio tcp4-connect:127.0.0.1:9999")


def commandServerAgent(receivedMessage):
    ''' TO DO: 
        1. Enable to forward requests to selected VMs.
        2. Tell them how much power they are eligible for. 
    '''
    machineName = ""
    machineIP = ""
    
    for i in receivedMessage:
        machineIP = i
        machineName = ipToMachineNames[i]
        
    forwardRequests(machineName.strip())
    
    '''
    STEP I
    '''
    # print('Create a TCP/IP socket')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    '''
    STEP II
    ''' 
    # print('Connect the socket to the server port')
    server_address = (machineIP, 8096)
    # server_address = ('localhost', 8096)
    
    '''
    STEP III
    '''
    sock.connect(server_address)
    print('Connected to Server Agent')
    
    sock.send(json.dumps(receivedMessage).encode())
    sock.close()


def estimatePowerBudgetForApp1(responseTime, numberOfRequest):
    global integrator_1
    global integralSwitchOnOff_1
    global intOk_1
    global prevResponseTime_1
    global initialDetection_1
    global badTuningCount_1
    global totalTuning_1

    for loopCounter in range(len(numberOfRequests_1)):    
    
        if numberOfRequest <= numberOfRequests_1[loopCounter]:
            kp = kpValues_1[str(numberOfRequests_1[loopCounter])] * tunePercentage
            ki = kiValues_1[str(numberOfRequests_1[loopCounter])] * tunePercentage
            operatingPointControlValue = powerValues_1[str(numberOfRequests_1[loopCounter])]
            operatingPointOutputValue = responseTimeValues_1[str(numberOfRequests_1[loopCounter])]
            break    

        else:
            kp = kpValues_1[str(numberOfRequests_1[-1])] * tunePercentage
            ki = kiValues_1[str(numberOfRequests_1[-1])] * tunePercentage
            operatingPointControlValue = powerValues_1[str(numberOfRequests_1[-1])]
            operatingPointOutputValue = responseTimeValues_1[str(numberOfRequests_1[-1])]

    if initialDetection_1 == 0:
        actualResponseTime = responseTime

    else:
        actualResponseTime = (responseTime + prevResponseTime_1) / 2 # - operatingPointOutputValue
        # print("Actual response time: %.2f" %(actualResponseTime))

    prevResponseTime_1 = responseTime
    initialDetection_1 += 1
   
    currError = round(refInput - actualResponseTime, 3)

    '''
    Proportional part
    '''
    pTerm = kp * currError    

    '''
    Integral part
    '''

    newIntegrator = integrator_1 + currError
    
    #if integralSwitch == False:
        # Input of Integral Part (Accumulated Error)
    #    integrator += currError # * (currTime - initialTime) 
    
    iTerm = ki * newIntegrator  

    ''' 
    # Controller Output (PI)
    '''
    estimatedControllerOutput = round(pTerm + iTerm + operatingPointControlValue, 2)

    print("Current controller output: %f" %estimatedControllerOutput)

    intOk_1 = True

    if estimatedControllerOutput < PI_LIM_MIN:
        # print("The output of controller is less than 30 W. It is computed as %s" %estimatedControllerOutput)
        badTuningCount_1 += 1

        if currError > 0:
            intOk_1 = False
    
    elif estimatedControllerOutput > PI_LIM_MAX:
        # print("The output of controller is greater than 58 W. It is computed as %s" %estimatedControllerOutput)
        badTuningCount_1 += 1

        if currError < 0:
            intOk_1 = False

    if intOk_1 == True:
        integrator_1 = newIntegrator
        integralSwitchOnOff_1 = 0
    
    else:
        integrator_1 = 0
        integralSwitchOnOff_1 = 1

    totalTuning_1 += 1

    tempEstimatedPower = int(estimatedControllerOutput)

    with open(fileToKeepEstimatedPowerData_1, 'a') as filehandle:
        filehandle.write("%s," %tempEstimatedPower)

    with open(fileToKeepMeasuredData_1, 'a') as filehandle:
        filehandle.write("%s," %actualResponseTime)

    with open(fileToKeepErrorValue_1, 'a') as filehandle:
        filehandle.write("%s," %currError)
    
    with open(fileToKeepPTerms_1, 'a') as filehandle:
        filehandle.write("%s," %pTerm)

    with open(fileToKeepITerms_1, 'a') as filehandle:
        filehandle.write("%s," %iTerm)

    with open(fileToKeepOperatingPoints_1, 'a') as filehandle:
        filehandle.write("%s," %operatingPointControlValue)

    with open(fileToKeepIntegrator_1, 'a') as filehandle:
        filehandle.write("%s," %newIntegrator)

    with open(fileToKeepIntegralSwitchOnOff_1, 'a') as filehandle:
        filehandle.write("%s," %integralSwitchOnOff_1)

    with open(fileToKeepDropPercentage_1, 'a') as filehandle:
        filehandle.write("%s," %dropPercentage_1)

    with open(fileToKeepEstimatedNumberOfRequest_1, 'a') as filehandle:
        filehandle.write("%s," %numberOfRequest)

    return tempEstimatedPower


def applyUniformlyDistributePolicy(estimatedControllerOutput):
    totalCappedPower = 0
    numberOfUsedMachines = len(list(ipToMachineNames.keys()))

    if estimatedControllerOutput < PI_LIM_MIN:
        # print("The output of controller is less than 30W. It is computed as %d" %estimatedControllerOutput)
        totalCappedPower = PI_LIM_MIN        

    if estimatedControllerOutput >= 30 and estimatedControllerOutput <= 58:
        # print("The output of controller is between 30 W and 58 W. It is computed as %d" %estimatedControllerOutput)
        if estimatedControllerOutput > (powerBudget / (len(list(ipToMachineNames.keys())))):
            totalCappedPower = (powerBudget / (len(list(ipToMachineNames.keys()))))

        else:
            totalCappedPower = estimatedControllerOutput

    if estimatedControllerOutput > PI_LIM_MAX:
        if estimatedControllerOutput > (powerBudget / (len(list(ipToMachineNames.keys())))):
            totalCappedPower = (powerBudget / (len(list(ipToMachineNames.keys()))))

        else:
            totalCappedPower = PI_LIM_MAX 

    t1 = threading.Thread(target=commandServerAgent, args=({"192.168.245.52": totalCappedPower * 1000000},))
    t2 = threading.Thread(target=commandServerAgent, args=({"192.168.245.53": totalCappedPower * 1000000},))
    t3 = threading.Thread(target=commandServerAgent, args=({"192.168.245.54": totalCappedPower * 1000000},))
    t4 = threading.Thread(target=commandServerAgent, args=({"192.168.245.55": totalCappedPower * 1000000},))

    t1.start()
    t2.start()
    t3.start()
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()

    return numberOfUsedMachines, totalCappedPower * numberOfUsedMachines


def applyPackToMinServerPolicy(estimatedControllerOutput):
    global nameOfEnabledMachines_1
    totalCappedPower = 0
    numberOfUsedMachines = 1

    if estimatedControllerOutput < PI_LIM_MIN:
        # print("The output of controller is less than 30W. It is computed as %d" %estimatedControllerOutput)
        totalCappedPower = PI_LIM_MIN

        availableMachines = list(ipToMachineNames.keys())

        selectedVMIndex = random.randint(0, len(availableMachines)-1)

        ipOfSelectedMachine = str(availableMachines[selectedVMIndex])
        tempSet = set()
        tempSet.add(ipOfSelectedMachine)
        sentMessage = { ipOfSelectedMachine: convertWattToMicrowatt(totalCappedPower) }

        commandServerAgent(sentMessage)
        print("%s is commanded to have %d W!" %(ipOfSelectedMachine, totalCappedPower))
        
        diffSet = nameOfEnabledMachines_1.difference(tempSet)
        # lenNameOfEnabledMachines = len(nameOfEnabledMachines)

        for s1 in diffSet:
            stopForwardingRequests(s1)
            # nameOfEnabledMachines.discard(s1)

        # if (len(diffSet) == lenNameOfEnabledMachines):
        #     nameOfEnabledMachines.add(ipOfSelectedMachine)
        nameOfEnabledMachines_1 = tempSet
        numberOfUsedMachines = len(nameOfEnabledMachines_1)

    if estimatedControllerOutput >= 30 and estimatedControllerOutput <= 58:
        # print("The output of controller is between 30 W and 58 W. It is computed as %d" %estimatedControllerOutput)
        totalCappedPower = estimatedControllerOutput
        
        availableMachines = list(ipToMachineNames.keys())

        selectedVMIndex = random.randint(0, len(availableMachines)-1)

        ipOfSelectedMachine = str(availableMachines[selectedVMIndex])
        tempSet = set()
        tempSet.add(ipOfSelectedMachine)
        sentMessage = { ipOfSelectedMachine: convertWattToMicrowatt( totalCappedPower ) }

        commandServerAgent(sentMessage)
        print("%s is commanded to have %d W!" %(ipOfSelectedMachine, totalCappedPower))

        diffSet = nameOfEnabledMachines_1.difference(tempSet)
        # lenNameOfEnabledMachines = len(nameOfEnabledMachines)

        for s1 in diffSet:
            stopForwardingRequests(s1)
            # nameOfEnabledMachines.discard(s1)

        # if (len(diffSet) == lenNameOfEnabledMachines):
        #     nameOfEnabledMachines.add(ipOfSelectedMachine)
        nameOfEnabledMachines_1 = tempSet
        numberOfUsedMachines = len(nameOfEnabledMachines_1)

    if estimatedControllerOutput > PI_LIM_MAX:
        # print("The output of controller is greater than 58 W. It is computed as %d" %estimatedControllerOutput)
    
        availableMachines = list(ipToMachineNames.keys())
        tempSet = set()

        # commands = list()

        # Use active power here.
        if estimatedControllerOutput > len(availableMachines) * (PI_LIM_MAX - idlePowerConsumptionPerSocket):
            totalAllocatedPowerEstimation = len(availableMachines) * (PI_LIM_MAX - idlePowerConsumptionPerSocket)

        else:
            totalAllocatedPowerEstimation = estimatedControllerOutput

        requiredNumberOfMachines = math.floor( totalAllocatedPowerEstimation / (PI_LIM_MAX - idlePowerConsumptionPerSocket) )
        print("%d servers are needed!" %requiredNumberOfMachines)

        for i in range(requiredNumberOfMachines):
            selectedVMIndex = random.randint(0, len(availableMachines)-1)

            ipOfSelectedMachine = str(availableMachines[selectedVMIndex])
            
            sentMessage = {ipOfSelectedMachine: convertWattToMicrowatt(PI_LIM_MAX)}
            # commands.append(sentMessage)
            commandServerAgent(sentMessage)
            print("%s is commanded to have %d W!" %(ipOfSelectedMachine, PI_LIM_MAX))
            tempSet.add(ipOfSelectedMachine)
            availableMachines.remove(ipOfSelectedMachine)
            totalCappedPower += PI_LIM_MAX

        residualPower = totalAllocatedPowerEstimation - (requiredNumberOfMachines * (PI_LIM_MAX - idlePowerConsumptionPerSocket))

        if residualPower < 5:
            residualPower = 5

        if len(availableMachines) != 0:
            selectedVMIndex = random.randint(0, len(availableMachines)-1)

            ipOfSelectedMachine = str(availableMachines[selectedVMIndex])
            allocatedPower = residualPower + idlePowerConsumptionPerSocket
            sentMessage = {ipOfSelectedMachine: convertWattToMicrowatt(allocatedPower)}
            # commands.append(sentMessage)
            commandServerAgent(sentMessage)
            print("%s is commanded to have %d W!" %(ipOfSelectedMachine, allocatedPower))
            tempSet.add(ipOfSelectedMachine)
            availableMachines.remove(ipOfSelectedMachine)
            totalCappedPower += allocatedPower

        diffSet = nameOfEnabledMachines_1.difference(tempSet)

        for s1 in diffSet:
            stopForwardingRequests(s1)
            # nameOfEnabledMachines.discard(s1)
        
        nameOfEnabledMachines_1 = tempSet
        numberOfUsedMachines = len(nameOfEnabledMachines_1)

        # t1 = threading.Thread(target=commandServerAgent, args=({"192.168.245.53": PI_LIM_MIN * 1000000},))
        # t1.start()
        # t2 = threading.Thread(target=commandServerAgent, args=({"192.168.245.52": PI_LIM_MIN * 1000000},))
        # t2.start()

    return numberOfUsedMachines, totalCappedPower


def main():
    # time.sleep(1) # Wait 1 sec to make log file warmup
    global logData

    while True:
        with open(logFile) as file: 
            lastLine = (file.readlines() [-1:])

        while True: 
            with open(logFile) as file: 
                newLastLine = (file.readlines() [-1:])
            
            if lastLine != newLastLine:
                break

        readResponseTime_1, estimationOfNumberOfRequest_1 = readResponseTimeFromLog(numberOfLinesToBeRead)

        if readResponseTime_1 == 0.0:
            print("No response time has been read")
            logData = []
            time.sleep(samplingTime)
            continue

        print("Estimated number of requests: %d" %(estimationOfNumberOfRequest_1))

        print("Current response times: %.2f" %(readResponseTime_1))

        estimatedControllerOutput = estimatePowerBudgetForApp1(readResponseTime_1, estimationOfNumberOfRequest_1 / len(list(ipToMachineNames.keys())))

        ''' 8. Allocated power is recorded '''
        # numberOfUsedMachines, allocatedPowerData = applyPackToMinServerPolicy(estimatedControllerOutput)
        numberOfUsedMachines, allocatedPowerData = applyUniformlyDistributePolicy(estimatedControllerOutput)
        # print(allocatedPowerData)

        print("Bad tuning/Total tuning for App-1 = %.2f" %(badTuningCount_1/totalTuning_1))

        with open(fileToKeepAllocatedPowerData, 'a') as filehandle:
            filehandle.write("%s," %allocatedPowerData)

        with open(fileToKeepNumberOfUsedMachines, 'a') as filehandle:
            filehandle.write("%s," %numberOfUsedMachines)

        with open(fileToKeepInterestedLogFileColumns, 'a') as filehandle:
            filehandle.writelines("%s\n" % place for place in logData)

        logData = []
        time.sleep(samplingTime)


if __name__ == '__main__':
    initializeKpAndKiValues()
    main()
