import time
import os 

# NOTES: database and swpag not implemented, must also establish a standard for exploit modules

def tick():
    #get exploits
    exploit_list = os.listdir("exploit_scripts")
    #TODO: add new modules to database

    #TODO: get targets (swpag)
    target_list = ['team1', 'team2', 'team3']

    # Q: Why exploit then team?; A: Allows us to stop running exploits when flag captured if you want to hide exploits
    # Alternatively, queue exploits for each team, don't fix what isn't broken and only change exploits for a given team (and only that team) if it stops working

    for exploit in exploit_list:
        for target in target_list:
            try:
                print(str(exploit) + ' against ' + str(target))
            #TODO: run exploit
            #TODO: submit flags (swpag)
            except Exception as e:
                print(e)

    #TODO: sort database based on flag captures

def main():
    tick_duration = 180 #seconds
    tick_num = 0 #used for counting ticks
    start_time = time.time()

    while True:

        tick_num += 1

        try:
            print("Tick " + str(tick_num) + ' (+' + str(time.time()-start_time) + 's)')
            tick()
        except Exception as e:
            print(e)

        sleep_duration = (start_time - time.time())%tick_duration
        time.sleep(sleep_duration)

if __name__ == "__main__":
  main()