import os
import time
def intermission():

    print("DISCUSSION STARTED")
    print()

    for i in range(5, 0, -1): 
        print(i, "seconds left", end="\r", flush=True) 
        time.sleep(1)
    #time is set to 5 seconds just to show the game, in reality the time should be set to 180 seconds

    print("DISCUSSION ENDED")
    time.sleep(5)
    os.system('cls' if os.name == 'nt' else 'clear') 

