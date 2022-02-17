import time
import os 
from common import game_client, team
import importlib
import math
import models

# NOTES: database and swpag not implemented, must also establish a standard for exploit modules

scripts_dir = "exploit_scripts"
exploit_modules = {}
exploit_success = {}
current_tick = -1
cwd = os.getcwd()
scripts_fullpath = cwd + '/' + scripts_dir + '/'

def run_all_exploits():
    #get exploits
    exploit_list = get_exploits_list()
    rebuild_path = lambda name: scripts_fullpath + name + '.py'
    for exploit_name in exploit_list:
        # Track module objects of exploits that have already been loaded
        exploit_modules[exploit_name] = load_exploit(exploit_name)

        # initialize successes of new exploits
        if exploit_name not in exploit_success:
            exploit_success[exploit_name] = 0

        # Warning: slow
        add_exploit_to_db(exploit_name)

      
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
    # Q: Premature optimization? 
    #    There will be at most 10-20 exploits. Sorting is o(nlogn).
    #    Querying the database is ???

# Get list of exploits from scripts directory, 
# then remove file extensions to make importing easier
def get_exploits_list():
    directory = './' + scripts_dir + '/'
    exploits_list = next(os.walk(directory))[2] # Gets only files as opposed to os.listdir
    for i in range(len(exploits_list)):
        exploit = exploits_list[i]
        if exploit[-3:] == '.py':
            exploits_list[i] = exploits[:-3]
    return exploits_list


# Create dictionary of {<service_id>: [<team_id>, ...]...}
# of all the services that are still up
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

# Sort exploits by number of successes achieved
def sort_exploits(exploit_success):
    exploit_list = list(exploit_success.items())
    exploit_list.sort(key=lambda x: x[1], reverse=True)
    return exploit_list

# Dynamically load exploit and save object
def load_exploit(exploit_name):
    module_path = scripts_dir + '.' + exploit_name

    # Check if exploit has previously been imported, dynamically reload if so
    if exploit_name not in exploit_modules:
        module = importlib.import_module(module_path)
    else:
        module = importlib.reload(exploit_modules[exploit_name])
    return module

def get_exploit(exploit_name):
    module = exploit_modules[exploit_name]
    class_name = module.class_name
    exploit_class = getattr(module, class_name)
    return exploit_class(game_client)

# add new modules to database
def add_exploit_to_db(exploit_name):
    engine = models.get_db_engine()
    Session = models.get_db_session(engine)
    Exploit = models.Exploit
    exploit_fullpath = rebuild_path(exploit_name)
    with Session() as session:
        with session.begin():
        if not session.query(Exploit.query.filter(
            Exploit.path == exploit_fullpath).exists()
            ).scalar():

            exploit_obj = get_exploit(exploit_name)
            new_exploit = Exploit(
                path = exploit_fullpath,
                service_id = exploit_obj.service.id)
            session.add(new_exploit)

# Count number of correct values returned after submitting flags
def count_correct(lst):
    count = 0
    for value in lst:
        if value == 'correct':
            count += 1
    return count

# TODO: Move loop out to main event loop
def main():
    tick_num = 0 #used for counting ticks
    start_time = None

    while True:

        tick_info = team.get_tick_info()
        tick_num = int(tick_info['tick_id'])
        seconds_left = int(tick_info['approximate_seconds_left'])

        if tick_num > current_tick:
            current_tick = tick_num
            start_time = time.time()
            try:
                print("\nRunning exploits for tick " + str(tick_num) + '\n')
                run_all_exploits()
                runtime = time.time() - start_time
                print("\nExploits for tick " + str(tick_num) + 
                    "finished after " + str(runtime) + 's\n')
            except Exception as e:
                runtime = time.time() - start_time
                print('\nException after ' + str(runtime) + 's')
                print(e)
                print('\n')

        else:
            if seconds_left > 1:
                time.sleep(seconds_left - 1)
            else:
                time.sleep(1)


if __name__ == "__main__":
  main()