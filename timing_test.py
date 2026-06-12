from datetime import datetime
import time 


def coarseTimer():
    startTime = datetime.now()
    time.sleep(1) #this is in seconds
    timeTaken  = datetime.now() - startTime
    print ("coarse timer : ", timeTaken , "\n")


def fineTimer():
    startTime = time.perf_counter()
    time.sleep(1) #this is in seconds
    timeTaken = time.perf_counter() - startTime
    print ("fine timer : ", timeTaken , "\n")


if __name__ == "__main__":
    coarseTimer()
    fineTimer()