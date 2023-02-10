import socket
import json
import os
import http.client, time, timeit, urllib, random
import multiprocessing as mp
import string
import argparse
import threading

request_types = ["GET", "POST"]


def sendGETRequest(connection_info, n, where):
    for _ in range(n):    
        if where == 0:
            r = "/wrk2-api/home-timeline/read?"
        else:
            r = "/wrk2-api/user-timeline/read?"
        
        idx = random.randint(1,962)
        start = random.random() * 100
        stop = start + 100
        r += 'user_id=' + str(idx) + '&start=' + str(start) + '&stop=' + str(stop)

        conn = http.client.HTTPConnection(connection_info)
        conn.request("GET", r)
        r1 = conn.getresponse()
        
        r1.read()
        # time.sleep(random.random()*1.5+0.5)
        conn.close()
        

def decRandom(length):
    a = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    
    if(length > 0):
        return decRandom(length - 1) + a[random.randint(0,9)]
    else:
        return ''


def sendPOSTRequest(connection_info, n):
    for _ in range(n):
        idx = str(random.randint(1,962))
        username = f"user_name_{idx}"
        user_id = idx
        letters = string.ascii_lowercase
        text = ''.join(random.choice(letters) for i in range(256))
        num_media = random.randint(0,4)
        num_urls = random.randint(0,5)
        num_user_mentions = random.randint(0,5)
        media_ids='['
        media_types='['

        for _ in range(num_user_mentions):
            user_mention_id = 0

            while(True):
                user_mention_id = random.randint(1,962)
                if user_id != user_mention_id:
                    break

            text = f"{text}@username_{user_mention_id}"

        for _ in range(num_urls):
            text = text + " http://" + ''.join(random.choice(letters) for i in range(64))

        for _ in range(num_media):
            media_id = decRandom(18)
            media_ids = media_ids + "\"" + media_id + "\","
            media_types = media_types + "\"png\","

        if num_media > 0:
            media_ids = media_ids[:-1]
            media_types = media_types[:-1]

        media_ids = media_ids + ']'
        media_types = media_types + ']'
        #print('media_ids=',media_ids)
        #print('media_types=',media_types)
        params = ""

        if num_media == 0:
            params=urllib.parse.urlencode({'username':username,'user_id':user_id,'text':text,'media_ids':media_ids,'post_type':'0'})
        else:
            params=urllib.parse.urlencode({'username':username,'user_id':user_id,'text':text,'media_ids':media_ids,'media_types':media_types,'post_type':'0'})

        headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}

        conn = http.client.HTTPConnection(connection_info)
        conn.request("POST", "/wrk2-api/post/compose", params, headers)

        r1 = conn.getresponse()
        # print(r1.status)

        r1.read()
        # time.sleep(random.random()*1.5+0.5)
        conn.close()


def run(connection_info, number_of_request, number_of_user):
    # processes = [mp.Process(target = self.sendRequest, args=(numberofrequest)) for x in range(number_of_user)]

    #     for p in processes:
    #         p.start()

    #     print("Start threads joining")

    #     for p in processes:
    #         p.join()
    #     # time.sleep(random.random())

    #     time.sleep(interval)

    # for _ in range(iteration):
    threads = []

    for _ in range(int(number_of_request/3)):
        type_of_request = request_types[random.randint(0, 1)]
        
        # if type_of_request == "POST":
        #     p = threading.Thread(target = sendPOSTRequest, args=(connection_info, number_of_request))
        #     p.start()
        #     threads.append(p)
        
        # else:
        #     p = threading.Thread(target = sendGETRequest, args=(connection_info, number_of_request, random.randint(0, 1)))
        #     p.start()
        #     threads.append(p)
        p = threading.Thread(target = sendGETRequest, args=(connection_info, number_of_request, random.randint(0, 1)))
        p.start()
        threads.append(p)

    for t in threads:
        t.join()


# def commandServerAgent(receivedMessage, exposureTimeOfEachRequest):
def commandServerAgent(connection_info, receivedMessage, port):
    ''' TO DO: 
        1. Enable to forward requests to selected VMs.
        2. Tell them how much power they are eligible for. 
    '''
    for i in receivedMessage:
        machine_ip = i
        requestRate = receivedMessage[i][0]
        requestDuration = receivedMessage[i][1]
        
    '''
    STEP I
    '''
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    '''
    STEP II
    ''' 
    server_address = (machine_ip, port)
    
    '''
    STEP III
    '''
    # Connect the socket to the server port
    sock.connect(server_address)
    print('Connected to Server Agent')
    
    sock.send(json.dumps(receivedMessage).encode())

    data = sock.recv(1024)

    try:
        receivedData = json.loads(data)
        print(f"Received ACK: {receivedData}")
        
    except ValueError:
        print("Received content was not a valid JSON!")

    if receivedData == "TERMINATE":
        sock.close()
        # sys.exit("Experiment is done on workload generator side!")
        os.system(f"kill -9 {os.getpid()}")

    elif receivedData == "SUCCESS":
        # Starting to send a load with the request rate
        # print("Workload generator is being started!")
        print(f"Current request rate: {requestRate}")
        # exec_post = POSTRequestGenerator(connection_info)
        # exec_get = GETRequestGenerator(connection_info)
        initial = timeit.default_timer()

        while (timeit.default_timer() - initial <= requestDuration):
            run(connection_info, requestRate, 1)
            
    else:
         print("Received ACK is not correct to launch the workload generator!")

    sock.close()


if __name__ == "__main__":
    random.seed(0)
    ap = argparse.ArgumentParser()

    ap.add_argument("-H", "--loadbalancerip", required=True, help="Host IP address")
    ap.add_argument("-p", "--port", default=8060, type=int, help="Port number")
    ap.add_argument("-po", "--serveragentport", default=8096, type=int, help="Server Agent port number")
    ap.add_argument("-n", "--initialnumberofrequest", type=int, required=True, help="Initial number of request")
    ap.add_argument("-i", "--increment", type=int, required=True, help="Increment in the number of request")
    ap.add_argument("-l", "--finalrequestnumber", type=int, required=True, help="Final number of request")
    ap.add_argument("-rd", "--requestduration", type=int, required=True, help="Exposure time of each request")
    # ap.add_argument("-f", "--file", required=True, help="File used in storing")

    args = ap.parse_args()
    '''
    The values of the following variables will be provided by the datacenter operator.    
    '''
    increment = args.increment
    exposureTimeToEachRequest = args.requestduration
    # fileName = args.file
    load_balancer_ip = args.loadbalancerip
    server_agent_port = int(args.serveragentport)

    profilingDuration = (((args.finalrequestnumber - args.initialnumberofrequest) / increment) + 1) * exposureTimeToEachRequest

    tempVariable = args.initialnumberofrequest

    connection_info = f"{load_balancer_ip}:{args.port}"
    
    start = timeit.default_timer()
    
    while ( timeit.default_timer() - start ) <= profilingDuration:
        sentMessage = {load_balancer_ip: [tempVariable, exposureTimeToEachRequest]}
        tmpTime = timeit.default_timer()
        commandServerAgent(connection_info, sentMessage, server_agent_port)
        print(f"Request rate is sent through {timeit.default_timer() - tmpTime} seconds")
        tempVariable += increment
        # time.sleep(2)

    print(f"Profiling in fact took {timeit.default_timer() - start} seconds")

    sentMessage = {load_balancer_ip: [3842, 10]}
    commandServerAgent(connection_info, sentMessage, server_agent_port)