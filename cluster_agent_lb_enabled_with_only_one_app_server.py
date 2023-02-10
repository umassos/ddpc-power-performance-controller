import socket
from xml.dom import minidom
# import libvirt
import json
import math
import os
import threading
import time
import sys
import random
import argparse
import statistics

ipToMachineNames = { '192.168.245.53': 'WikiImage_German3' }
machineToSetPower = { 'WikiImage_German3': 58 }
VMPath = '/etc/libvirt/qemu/ubuntu_18_04_guest4.xml'

logFile = "/var/log/haproxy.log"

numberOfSockets = 2
idlePowerConsumptionPerSocket = 25 # In terms of Watt
disconnectSignal = {"Exit": 1}

PI_LIM_MIN = 30
PI_LIM_MAX = 58

# It is used to keep all log lines
logData = []
dropPercentage = []

ap = argparse.ArgumentParser()

ap.add_argument("-nl", "--numberoflinestoberead", required=True, help="Number of lines to be read")
ap.add_argument("-st", "--samplingtime", required=True, help="Sampling time")
ap.add_argument("-t", "--tunepercentage", required=True, help="Tune percentage on Kp and Ki values")
ap.add_argument("-p", "--applicationsubpath", required=True, help="Application subpath")
ap.add_argument("-sf", "--sourcefile", required=True, help="File that is to be read")
ap.add_argument("-ri", "--referenceInput", required=True, help="Reference input target")

ap.add_argument("-ap", "--allocatedpower", required=True, help="File to keep allocated power")
ap.add_argument("-ep", "--estimatedpower", required=True, help="File to keep estimated power")
ap.add_argument("-rt", "--measuredresponsetime", required=True, help="File to keep measured response time")
ap.add_argument("-lf", "--logfile", required=True, help="File to keep interested log file columns")
ap.add_argument("-ev", "--errorvalue", required=True, help="File to keep error value")
ap.add_argument("-dp", "--droppercentage", required=False, help="File to keep drop percentage")
ap.add_argument("-er", "--estimatednumberofrequest", required=False, help="File to keep estimated number of request")
ap.add_argument("-pt", "--pterms", required=True, help="File to keep p terms")
ap.add_argument("-it", "--iterms", required=True, help="File to keep i terms")
ap.add_argument("-op", "--operatingpoints", required=True, help="File to keep operating points")
ap.add_argument("-in", "--integrator", required=True, help="File to keep integrator value")
ap.add_argument("-is", "--integralswitchonoff", required=False, help="File to keep integrator switch on/off value")

args = vars(ap.parse_args())

## The values of the following six variables will be provided by the datacenter operator.
numberOfLinesToBeRead = int(args["numberoflinestoberead"])                          # Read log file (number of line)
samplingTime = int(args["samplingtime"])                                            # Sampling time
tunePercentage = float(args["tunepercentage"])
applicationSubPath = str(args["applicationsubpath"])
sourceFile = str(args["sourcefile"])
refInput = float(args["referenceInput"])

fileToKeepAllocatedPowerData = str(args["allocatedpower"])                          # File for allocated power data
fileToKeepEstimatedPowerData = str(args["estimatedpower"])                          # File for estimated power data
fileToKeepMeasuredData = str(args["measuredresponsetime"])                          # File for measured response time
fileToKeepInterestedLogFileColumns = str(args["logfile"])                           # File for interested apache log file columns
fileToKeepErrorValue = str(args["errorvalue"])                                      # File for controller input/error input
fileToKeepDropPercentage = str(args["droppercentage"])                              # File for keeping drop percentage
fileToKeepEstimatedNumberOfRequest = str(args["estimatednumberofrequest"])          # File for keeping estimating number of requests
fileToKeepPTerms = str(args["pterms"])                                              # File for keeping P terms
fileToKeepITerms = str(args["iterms"])                                              # File for keeping I terms
fileToKeepOperatingPoints = str(args["operatingpoints"])                            # File for keeping operating point values
fileToKeepIntegrator = str(args["integrator"])                                      # File for keeping integrator
fileToKeepIntegralSwitchOnOff = str(args["integralswitchonoff"])                    # File for keeping integral switch on/off

kpValues = {}
kiValues = {}
powerValues = {}
responseTimeValues = {}
aValues = {}
bValues = {}
numberOfRequests = []


def readControllerValues():
    global kpValues, kiValues, powerValues, responseTimeValues, aValues, bValues, numberOfRequests

    with open(sourceFile, "r") as fileStream:
        for line in fileStream:
            currentline = line.split(",")
            kpValues[str(currentline[0])] = float(currentline[1])
            kiValues[str(currentline[0])] = float(currentline[2])
            powerValues[str(currentline[0])] = float(currentline[3])
            responseTimeValues[str(currentline[0])] = float(currentline[4])
            aValues[str(currentline[0])] = float(currentline[5])
            bValues[str(currentline[0])] = float(currentline[6])
            numberOfRequests.append(int(currentline[0]))


def convertWattToMicrowatt(value):
    return value * 1000000


def convertMicrowattToWatt(value):
    return round(value / 1000000, 2)


def convertMillisecondToSecond(value):
    return round(value / 1000, 2)


def readResponseTimeFromLog(numberOfLinesToBeRead):
    readResponses = []
    global dropPercentage, logData
    numberOfRequests200ResponseCodes = 0
    numberOfRequestsAllResponseCodes = 0
    dictNumberOfRequests = {}
    dict200Responses = {}

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
        
        logData.append("%s %s %s %s" %(dateTimeInfo, requestedPageInfo, responseCodeInfo, responseTimeInfo))

        # print(dateTimeInfo + " " + requestedPageInfo + " " + responseCodeInfo + " " + responseTimeInfo)

        if requestedPageInfo.strip().startswith(applicationSubPath):
            numberOfRequestsAllResponseCodes += 1

            dateTimeSplitted = dateTimeInfo.split(":")
            secondInfo = dateTimeSplitted[3].split(".")[0]

            valueOfDict = dictNumberOfRequests.get(secondInfo, 0)
            dictNumberOfRequests[secondInfo] = valueOfDict + 1

            if responseCodeInfo.strip() == "200":  
                tempList = dict200Responses.get(secondInfo, list())
                tempList.append(float(responseTimeInfo))
                dict200Responses[secondInfo] = tempList
                numberOfRequests200ResponseCodes += 1

    if len(dictNumberOfRequests.keys()) == 0:
        return 0.0, 0
    
    ''' It returns key with max value '''
    maxKey = max(dictNumberOfRequests, key = dictNumberOfRequests.get)

    # print("Number of read requests: %d" %(numberOfReadRequests))
    # numberOfRequests.append(numberOfReadRequests)
    dropPercentage.append(100 * (numberOfRequestsAllResponseCodes - numberOfRequests200ResponseCodes) / numberOfRequestsAllResponseCodes)

    if dict200Responses.get(maxKey, 0) != 0:
        return convertMillisecondToSecond(statistics.mean(dict200Responses[maxKey])), len(dict200Responses[maxKey])
    else:
        return 0.0, 0


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
        
    # forwardRequests(machineName.strip())
    
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


def writeToFile( allocatedPowerData, estimatedPowerData, responseTimeData, errorData, dropPercentage, estimatedNumberOfRequest, pTerms, iTerms, operatingPoints, integrators, integralSwitchOnOff, logData ):

    with open(fileToKeepAllocatedPowerData, 'a') as filehandle:
            filehandle.writelines("%s," %allocatedPowerData)

    with open(fileToKeepEstimatedPowerData, 'a') as filehandle:
        filehandle.writelines("%s," %estimatedPowerData)

    with open(fileToKeepMeasuredData, 'a') as filehandle:
        filehandle.writelines("%s," %responseTimeData)

    with open(fileToKeepErrorValue, 'a') as filehandle:
        filehandle.writelines("%s," %errorData)

    with open(fileToKeepDropPercentage, 'a') as filehandle:
        filehandle.writelines("%s," % place for place in dropPercentage)

    with open(fileToKeepEstimatedNumberOfRequest, 'a') as filehandle:
        filehandle.writelines("%s," %estimatedNumberOfRequest)
    
    with open(fileToKeepPTerms, 'a') as filehandle:
        filehandle.writelines("%s," %pTerms)

    with open(fileToKeepITerms, 'a') as filehandle:
        filehandle.writelines("%s," %iTerms)

    with open(fileToKeepOperatingPoints, 'a') as filehandle:
        filehandle.writelines("%s," %operatingPoints)

    with open(fileToKeepIntegrator, 'a') as filehandle:
        filehandle.writelines("%s," %integrators)

    with open(fileToKeepIntegralSwitchOnOff, 'a') as filehandle:
        filehandle.writelines("%s," %integralSwitchOnOff)

    ''''''
    with open(fileToKeepInterestedLogFileColumns, 'a') as filehandle:
        filehandle.writelines("%s\n" % place for place in logData)


def main():
    readControllerValues()
    global dropPercentage, logData

    intOk = True
    newIntegrator = 0.0
    integrator = 0.0

    prevResponseTime = 0.0

    totalTuning = 0
    badTuningCount = 0

    initialDetection = 0

    # writingCounter = False

    # time.sleep(1) # Wait 1 sec to make log file warmup

    # initialTime = time.time()

    # start = time.time()

    # while ( time.time() - start ) < experimentDuration:
    while True:
        # errorData, responseTimeData, allocatedPowerData, estimatedPowerData, estimatedNumberOfRequest, integralSwitchOnOff, correctedPower, dropPercentage, pTerms, iTerms, integrators, operatingPoints, logData = [], [], [], [], [], [], [], [], [], [], [], [], []
        logData, dropPercentage = [], []

        # with open(logFile, "r") as file:
        #     for line in file:
        #         pass
        with open(logFile) as file: 
            line = (file.readlines() [-1:])

        while True: 
            with open(logFile) as file: 
                newLastLine = (file.readlines() [-1:])
            
            if str(line).strip() != str(newLastLine).strip():
                break
            
            ''' This part is only for the experimentation purposes. It will be removed or commented once this is moved to Production phase.  '''
            # if writingCounter != False:
            #     writeToFile(allocatedPowerData, estimatedPowerData, responseTimeData, errorData, dropPercentage, estimatedNumberOfRequest, pTerms, iTerms, operatingPoints, integrators, integralSwitchOnOff, correctedPower, logData)

            #     # Reset variables
            #     errorData, responseTimeData, allocatedPowerData, estimatedPowerData, estimatedNumberOfRequest, integralSwitchOnOff, correctedPower, dropPercentage, pTerms, iTerms, integrators, operatingPoints, logData = [], [], [], [], [], [], [], [], [], [], [], [], []

        # writingCounter = True

        readResponseTime, estimationOfNumberOfRequest = readResponseTimeFromLog(numberOfLinesToBeRead)
        
        estimatedNumberOfRequest = estimationOfNumberOfRequest
        print("Estimated number of request: %d" %estimationOfNumberOfRequest)

        if readResponseTime == 0.0:
            print("No response time has been read")
            time.sleep(samplingTime)
            continue

        print("Current response time: %.2f" %(readResponseTime))

        for loopCounter in range(len(numberOfRequests)):    
    
            if estimationOfNumberOfRequest <= numberOfRequests[loopCounter]:
                kp = kpValues[str(numberOfRequests[loopCounter])] * tunePercentage
                ki = kiValues[str(numberOfRequests[loopCounter])] * tunePercentage
                operatingPointControlValue = powerValues[str(numberOfRequests[loopCounter])]
                operatingPointOutputValue = responseTimeValues[str(numberOfRequests[loopCounter])]
                break    

        else:
                kp = kpValues[str(numberOfRequests[-1])] * tunePercentage
                ki = kiValues[str(numberOfRequests[-1])] * tunePercentage
                operatingPointControlValue = powerValues[str(numberOfRequests[-1])]
                operatingPointOutputValue = responseTimeValues[str(numberOfRequests[-1])]

        ''' 1. Operating points are recorded '''
        operatingPoints = operatingPointControlValue

        if initialDetection == 0:
            actualResponseTime = readResponseTime

        else:
            actualResponseTime = (readResponseTime + prevResponseTime) / 2 # - operatingPointOutputValue
            # print("Actual response time: %.2f" %(actualResponseTime))

        prevResponseTime = readResponseTime
        initialDetection += 1

        ''' 2. Measured response times are recorded '''
        responseTimeData = actualResponseTime

        currError = round(refInput - actualResponseTime, 3)

        ''' 3. Error is recorded '''
        errorData = currError

        # curr_control_input = prev_control_input + ((Kp + Ki) * curr_error) - (Kp * prev_error)

        '''
        # Proportional part
        '''
        pTerm = kp * currError
        
        ''' 4. Proportional terms are recorded '''
        pTerms = pTerm

        '''
        # Integral part
        '''

        # newIntegrator = integrator + currError

        newIntegrator = integrator + currError
        
        #if integralSwitch == False:
            # Input of Integral Part (Accumulated Error)
        #    integrator += currError # * (currTime - initialTime) 

        ''' 5. integral error is recorded '''
        integrators = newIntegrator

        iTerm = ki * newIntegrator  

        ''' 6. Integral terms are recorded '''
        iTerms = iTerm

        ''' 
        # Controller Output (PI)
        '''
        estimatedControllerOutput = round(pTerm + iTerm + operatingPointControlValue, 2)

        print("Current controller output: %f" %estimatedControllerOutput)

        ''' 7. Controller output is recorded '''
        estimatedPowerData = estimatedControllerOutput

        tempAllocatedPower = int(estimatedControllerOutput)

        intOk = True

        # allocatedPower = tempAllocatedPower

        # print("Power is being set to %d" %allocatedPower)

        ''' 8. Allocated power is recorded '''
        # allocatedPowerData.append(allocatedPower)

        totalTuning += 1

        if estimatedControllerOutput < PI_LIM_MIN:
            print("The output of controller is saturated. The value: %s" %estimatedControllerOutput)
            tempAllocatedPower = PI_LIM_MIN
            badTuningCount += 1

            if currError > 0:
                intOk = False
        
        elif estimatedControllerOutput > PI_LIM_MAX:
            print("The output of controller is saturated. The value is: %s" %estimatedControllerOutput)
            tempAllocatedPower = PI_LIM_MAX
            badTuningCount += 1

            if currError < 0:
                intOk = False

        if intOk == True:
            integrator = newIntegrator
            integralSwitchOnOff = 0
        
        else:
            integrator = 0
            integralSwitchOnOff= 1

        allocatedPower = tempAllocatedPower

        print("Power is being set to %d" %allocatedPower)

        ''' 8. Allocated power is recorded '''
        allocatedPowerData= allocatedPower

        for key in ipToMachineNames.keys():
            sentMessage = {key: tempAllocatedPower * 1000000}
            commandServerAgent(sentMessage)

        print("Ratio of bad tuning to number of total tuning: %f" %(badTuningCount/totalTuning))

        writeToFile(allocatedPowerData, estimatedPowerData, responseTimeData, errorData, dropPercentage, estimatedNumberOfRequest, pTerms, iTerms, operatingPoints, integrators, integralSwitchOnOff, logData)

        time.sleep(samplingTime)

        # with open(fileToKeepAllocatedPowerData, 'a') as filehandle:
        #     filehandle.writelines("%s," % place for place in allocatedPowerData)

        # with open(fileToKeepEstimatedPowerData, 'a') as filehandle:
        #     filehandle.writelines("%s," % place for place in estimatedPowerData)

        # with open(fileToKeepMeasuredData, 'a') as filehandle:
        #     filehandle.writelines("%s," % place for place in responseTimeData)

        # with open(fileToKeepErrorValue, 'a') as filehandle:
        #     filehandle.writelines("%s," % place for place in errorData)

        # with open(fileToKeepDropPercentage, 'a') as filehandle:
        #     filehandle.writelines("%s," % place for place in dropPercentage)

        # with open(fileToKeepEstimatedNumberOfRequest, 'a') as filehandle:
        #     filehandle.writelines("%s," % place for place in estimatedNumberOfRequest)
        
        # with open(fileToKeepPTerms, 'a') as filehandle:
        #     filehandle.writelines("%s," % place for place in pTerms)

        # with open(fileToKeepITerms, 'a') as filehandle:
        #     filehandle.writelines("%s," % place for place in iTerms)

        # with open(fileToKeepOperatingPoints, 'a') as filehandle:
        #     filehandle.writelines("%s," % place for place in operatingPoints)

        # with open(fileToKeepIntegrator, 'a') as filehandle:
        #     filehandle.writelines("%s," % place for place in integrators)

        # with open(fileToKeepIntegralSwitchOnOff, 'a') as filehandle:
        #     filehandle.writelines("%s," % place for place in integralSwitchOnOff)

        # ''''''
        
        # with open(fileToKeepEstimatedToBeAllocatedPower, 'a') as filehandle:
        #     filehandle.writelines("%s," % place for place in correctedPower)

        # with open(fileToKeepInterestedLogFileColumns, 'a') as filehandle:
        #     filehandle.writelines("%s\n" % place for place in logData)


if __name__ == '__main__':
    main()
