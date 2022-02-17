import time
import os 
from common import game_client, team
import importlib
import math

# NOTES: database and swpag not implemented, must also establish a standard for exploit modules

scripts_dir = "./exploit_scripts/"
exploit_success = {}

def tick():
    #get exploits
    exploit_list = next(os.walk(scripts_dir))[2] # Gets only files as opposed to os.listdir
    for exploit_name in exploit_list:
        if exploit_name not in exploit_success:
            exploit_success[exploit_name] = 0
    
    #TODO: add new modules to database

    # e.g. {<service_id>: [<team_id>, ...], ...}
    target_services = services_up()

    # Q: Why exploit then team?; A: Allows us to stop running exploits when flag captured if you want to hide exploits
    # Alternatively, queue exploits for each team, don't fix what isn't broken and only change exploits for a given team (and only that team) if it stops working

    # process exploit with most successes first
    exploit_list = sort_exploits(exploit_success) 
    for exploit_name in exploit_list:
        exploit = get_exploit(exploit_name)
        flags = []
        target_team_ids = target_services[exploit.service.id]
        for team_id in target_team_ids:
            hostname = 'team' + str(team_id)
            try:
                print(str(exploit) + ' against ' + hostname)
                new_flags = exploit.run(hostname)
                if type(new_flags) == str:
                    new_flags = [new_flags]
                flags.extend(new_flags)

            except Exception as e:
                print(e)

        batches = math.ceil(len(flags) / 100)
        for i in range(batches):
            submission = flags[i * 100:(i + 1) * 100]
            results = team.submit_flag(flags)
            exploit_success[exploit_name] += count_correct(results)

    #TODO: sort database based on flag captures

def services_up():
    service_list = {}
    team_services = team.get_game_status()['service_states']
    for team_id, services in team_services.items():
        for service_id, service in services.items():
            if service['service_state'] == 'up':
                team_id = int(team_id)
                service_id = int(service_id)
                if service_id in service_list:
                    service_list[service_id].append(team_id)
                else:
                    service_list[service_id] = [team_id]
    return service_list

def sort_exploits(exploit_success):
    exploit_list = list(exploit_success.items())
    exploit_list.sort(key=lambda x: x[1], reverse=True)
    return exploit_list

def get_exploit(exploit_name):
    module = importlib.import_module(scripts_dir + exploit_name)
    class_name = module.class_name
    exploit_class = getattr(module, class_name)
    return exploit_class(game_client)

def count_correct(lst):
    count = 0
    for value in lst:
        if value == 'correct':
            count += 1
    return count

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