import argparse
import numpy as np
import statistics as stat

if __name__ == "__main__":
    ap = argparse.ArgumentParser()

    ap.add_argument("-n", "--initialnumberofrequest", type=int, required=True, help="Initial number of request")
    ap.add_argument("-i", "--increment", type=int, required=True, help="Increment in the number of request")
    ap.add_argument("-l", "--finalrequestnumber", type=int, required=True, help="Final number of request")
    ap.add_argument("-sf", "--sourcefile", required=True, help="File that is to be read")
    ap.add_argument("-df", "--destinationfile", required=True, help="File that is to be written")

    args = ap.parse_args()

    ## The values of the following five variables will be provided by the datacenter operator.
    initialNumberOfRequest = int(args.initialnumberofrequest)
    increment = int(args.increment)
    finalNumberOfRequest = int(args.finalrequestnumber)
    sourceFile = args.sourcefile
    destinationFile = args.destinationfile

    responseTimes = {}
    allocatedPowers = {}
    modelParameters = {}

    for tmpVariable in range(initialNumberOfRequest, finalNumberOfRequest + 1, increment):
        allocatedPowers[str(tmpVariable)] = []
        responseTimes[str(tmpVariable)] = []
        modelParameters[str(tmpVariable)] = []

    # sourceFile = "/Users/msavasci/Desktop/Research/Synthesis_Project/Designing_a_Controller/Data_Acquisition/Social_Networking_Application/req100/rt100All.txt"

    with open(sourceFile, "r") as fileStream:
        
        for line in fileStream:
            currentline = line.split(",")

            allocatedPowers[str(currentline[0])].append(int(currentline[1]))
            responseTimes[str(currentline[0])].append(int(currentline[2]))
            # if str(currentline[0]) == "8":
            #     allocatedPowers[str(currentline[1])].append(int(currentline[2]))
            #     responseTimes[str(currentline[1])].append(int(currentline[3]))

    u1 = []
    y = []
    u1_offset = []
    y_offset = []

    # while tmpVariable <= finalNumberOfRequest:
    for tmpVariable in range(initialNumberOfRequest, finalNumberOfRequest + 1, increment):
        print(f"For {tmpVariable}")
        
        for i in allocatedPowers[str(tmpVariable)]:
            u1.append(i/1000000) # Convert from microwatt to watt

        for j in responseTimes[str(tmpVariable)]:
            y.append(j/1000) # Convert from millisecond to second

        # u1Mean = sum(u1[:-1])/len(u1[:-1])
        u1Mean = stat.mean(u1[:-1])
        
        # yMean = sum(y[1:])/len(y[1:])
        yMean = stat.mean(y[1:])

        u1_offset = [number - u1Mean for number in u1]

        y_offset = [number - yMean for number in y]

        m_list = [y_offset[:-1], u1_offset[:-1]]
        A = np.array(m_list)
        # print(A.shape)
        A_prime = np.transpose(A)
        # print(A_prime.shape)
        
        B = np.array(y_offset[1:])
        # print(len(B))
        theta = np.linalg.lstsq(A_prime, B, rcond=None)

        a = theta[0][0]
        b1 = theta[0][1]

        # yhat = a * y_offset(1:end-1) + b1 * u1_offset(1:end-1);% + b2 * u2_offset(1:end-1)
        # RMSE = sqrt(mean((y_offset(2:end) - yhat).^2));  # Root-Mean-Squared Error
        
        print("a = " + str(a) + ", b1 = " + str(b1))

        yhatC1 = [number * a for number in y_offset[:-1]]

        yhatC2 = [number * b1 for number in u1_offset[:-1]]

        yhat = []

        for i in range(len(y_offset[:-1])):
            yhat.append(yhatC1[i] + yhatC2[i])

        sub = []

        for i in range(0, len(yhat)):
            sub.append(y_offset[i+1] - yhat[i])

        RSQUARE = 1 - ( stat.variance(sub) / stat.variance(y_offset[1:]) )
        print("R^2 = " + str(RSQUARE))

        with open(destinationFile, 'a') as f:
            f.write("%d,%f,%f,%f,%f,%f\n" %(tmpVariable, a, b1, u1Mean, yMean, RSQUARE))

        # tmpVariable += increment