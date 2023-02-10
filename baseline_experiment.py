import time
import argparse
import statistics

logFile = "/var/log/haproxy.log"

dropPercentage = []
logData = []

ap = argparse.ArgumentParser()

ap.add_argument("-p", "--applicationsubpath", required=True, help="Application subpath")
ap.add_argument("-d", "--experimentduration", required=True, help="Application subpath")
ap.add_argument("-nl", "--numberoflinestoberead", required=True, help="Number of lines to be read")
ap.add_argument("-st", "--samplingtime", required=True, help="Sampling time")
ap.add_argument("-ap", "--allocatedpower", required=True, help="File to keep allocated power")
ap.add_argument("-rt", "--measuredresponsetime", required=True, help="File to keep measured response time")
ap.add_argument("-lf", "--logfile", required=True, help="File to keep interested log file columns")
ap.add_argument("-dp", "--droppercentage", required=False, help="File to keep drop percentage")
ap.add_argument("-er", "--estimatednumberofrequest", required=False, help="File to keep estimated number of request")

args = vars(ap.parse_args())

applicationSubPath = str(args["applicationsubpath"])
experimentDuration = int(args["experimentduration"])
numberOfLinesToBeRead = int(args["numberoflinestoberead"])                          # Read log file (number of line)
samplingTime = int(args["samplingtime"])           
fileToKeepAllocatedPowerData = str(args["allocatedpower"])                          # File for allocated power data
fileToKeepMeasuredResponseTimeData = str(args["measuredresponsetime"])              # File for measured response time
fileToKeepInterestedLogFileColumns = str(args["logfile"])                           # File for interested apache log file columns
fileToKeepDropPercentage = str(args["droppercentage"])                              # File for keeping drop percentage
fileToKeepEstimatedNumberOfRequest = str(args["estimatednumberofrequest"])          # File for keeping estimating number of requests


def convertWattToMicrowatt(value):
    return value * 1000000


def convertMicrowattToWatt(value):
    return round(value / 1000000, 2)


def convertMillisecondToSecond(value):
    return round(value / 1000, 2)


def readResponseTimeFromLog(numberOfLinesToBeRead):
    responseTime = 0.0
    readResponses = []
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
        
        logData.append(str(dateTimeInfo + " " + requestedPageInfo + " " + responseCodeInfo + " " + responseTimeInfo))

        # print(dateTimeInfo + " " + requestedPageInfo + " " + responseCodeInfo + " " + responseTimeInfo)

        if requestedPageInfo.strip().startswith(applicationSubPath):
            
            if responseTimeInfo.strip() != "-1":
                numberOfRequestsAllResponseCodes += 1

                dateTimeSplitted = dateTimeInfo.split(":")
                secondInfo = dateTimeSplitted[3][0:2]

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
        # return convertMillisecondToSecond(sum(dict200Responses[maxKey])/len(dict200Responses[maxKey])), len(dict200Responses[maxKey])
        return convertMillisecondToSecond(statistics.mean(dict200Responses[maxKey])), len(dict200Responses[maxKey])
    else:
        return 0.0, 0


def main():
    responseTimeData = []
    estimatedNumberOfRequests = []
    allocatedPower = []

    # time.sleep(1) # Wait 1 sec to make log file warmup

    start = time.time()

    while ( time.time() - start ) <= experimentDuration:
        readResponseTime, estimationOfNumberOfRequest = readResponseTimeFromLog(numberOfLinesToBeRead)

        if readResponseTime == 0.0:
            print("No response time has been read")
            # responseTimeData.append(0.0)
            time.sleep(samplingTime)
            continue

        # readResponseTime = convertMillisecondToSecond(readResponseTime)

        allocatedPower.append(58*4)

        print("Current response time: %f second" %(readResponseTime))
        print("Estimated number of request: %d" %(estimationOfNumberOfRequest))

        ''' 2. Measured response times are recorded '''
        responseTimeData.append(readResponseTime)
        estimatedNumberOfRequests.append(estimationOfNumberOfRequest)

        time.sleep(samplingTime)

    with open(fileToKeepMeasuredResponseTimeData, 'w') as filehandle:
        filehandle.writelines("%s," % place for place in responseTimeData)

    with open(fileToKeepDropPercentage, 'w') as filehandle:
        filehandle.writelines("%s," % place for place in dropPercentage)

    with open(fileToKeepEstimatedNumberOfRequest, 'w') as filehandle:
        filehandle.writelines("%s," % place for place in estimatedNumberOfRequests)

    with open(fileToKeepAllocatedPowerData, 'w') as filehandle:
        filehandle.writelines("%s," % place for place in allocatedPower)

    with open(fileToKeepInterestedLogFileColumns, 'w') as filehandle:
        filehandle.writelines("%s\n" % place for place in logData)


if __name__ == "__main__":
    main()