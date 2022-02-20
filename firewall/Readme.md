# PCTF Firewall

This is a firewall designed for PCTF game, it kills all the IP connections coming to defined specific service ports 

with data packets containing defined set of blacklisted keywords. It also acts as a monitor to capture protocol and port

specific traffic to generate summary for manual analysis.

### Define Blacklist Keywords
blacklist keywords are defined in a JSON file at location [proj_path]/firewall/resources/bl_keywords.json(sample below)
```
{"*": ["/", ";", "&", "|", "`", "cat", "bin", "bash", "more", "less", "opt", "ictf", "services"],
  "exclusion": {
    "10001": ["/",";", "&","|", "`"],
    "10002": ["/"],
    "10003": [";"],
    "10004": ["&"],
    "10005": ["|"]
  }
}
```
"*" keywords will be applied to all the services ports and per service based exclusion can be defined 

with "service" port as key and exclusion as list of keywords which will be excluded from "*". 

Here in the above example for service running at port 10001 only ["cat", "bin", "bash", "more", "less", "opt", "ictf", "services"]

### Define Services
Listening service ports are defined in a JSON file at location [proj_path]/firewall/resources/services.json(sample below)
```
{
  "simplecalc": ["tcp","10001"],
  "simplecalc2": ["tcp","10002"]
}
```
where keys are service name and values are list with protocol and service port

### Pull summaries from the Game VM to Local machine for analysis

scp -i ~/.ssh/[rsa_key_file] -r [game_user]@[vm_host_ip/name]:[proj_path]/firewall/summary_logs  /path/to/local/machine/pctf/summary_logs

### Setup the Application
sudo chmod +x <proj_path>/firewall/startme.sh --interface="[interface]" --prj_path="[proj_path]/firewall"

### sudo crontab -e
*/1 * * * * <proj_path>/firewall/startme.sh --interface="[interface]" --prj_path="[proj_path]/firewall"

### Add Network Delay
sudo tc qdisc del dev [interface] root --> to remove delay

sudo tc qdisc add dev [interface] root netem delay 1000ms --> to induce delay

