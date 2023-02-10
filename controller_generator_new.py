import matlab
import matlab.engine
import argparse

ap = argparse.ArgumentParser()

ap.add_argument("-sf", "--sourcefile", required=True, help="File that is to be read")
ap.add_argument("-df", "--destinationfile", required=True, help="File that is to be written")

args = vars(ap.parse_args())

## The values of the following variables will be provided by the datacenter operator.
sourceFile = str(args["sourcefile"])
destinationFile = str(args["destinationfile"])

def computeKiAndKp(a, b):
    eng = matlab.engine.start_matlab()
    Kp, Ki = eng.PIControllerGenerator(a, b, nargout=2)
    eng.quit()
    return Kp, Ki

if __name__ == "__main__":
    with open(sourceFile, "r") as fileStream:
        for line in fileStream:
            currentline = line.split(",")
            numberOfRequest = int(currentline[0])
            aValue = float(currentline[1])
            bValue = float(currentline[2])
            uOffsetValue = float(currentline[3])
            yOffsetValue = float(currentline[4])
            kp, ki = computeKiAndKp(aValue, bValue)

            print("Number of Request: %d, Kp: %f, Ki: %f" %(numberOfRequest, kp, ki))

            with open(destinationFile, 'a') as f:
                f.write("%d,%f,%f,%f,%f,%f,%f\n" %(numberOfRequest, kp, ki, uOffsetValue, yOffsetValue, aValue, bValue))