# PCTF Firewall

This is a firewall designed for PCTF game. It kills TCP requests to specific service ports with data packets containing keywords from a defined set in a blacklist. It also acts as a monitor to capture protocol and port specific traffic to generate a summary for manual analysis.

### Defining Blacklist Keywords
Blacklist keywords are defined in a JSON file at location [proj_path](resources/bl_keywords.json) (sample below)
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
"\*" keywords are applied to all the services ports. Particular keywords could be excluded per service, defined with the service port as key. The list of keywords to exclude are the values. In the example above, the firewall only blocks requests containing `["cat", "bin", "bash", "more", "less", "opt", "ictf", "services"]` to the service running on port 10001.

### Defining Services
Listening service ports are defined in a JSON file at location [proj_path](resources/services.json) (sample below)
```
{
  "simplecalc": ["tcp","10001"],
  "simplecalc2": ["tcp","10002"]
}
```
where keys are service name and values are listed with protocol and service port.

### Pulling Summaries 

Summaries can be pulled from the Game VM to Local machine for analysis using 

```scp -i ~/.ssh/[rsa_key_file] -r [game_user]@[vm_host_ip/name]:[proj_path]/firewall/summary_logs  /path/to/local/machine/pctf/summary_logs```

### Starting The Application

The following commands start the application. First, we must give execution permission to the application.

```sudo chmod +x <proj_path>/firewall/startme.sh --interface="[interface]" --prj_path="[proj_path]/firewall"```


Next, we start a cron job to schedule execution for every hour.

```sudo crontab -e```
```*/1 * * * * <proj_path>/firewall/startme.sh --interface="[interface]" --prj_path="[proj_path]/firewall"```

### Adding Network Delay

A temporary network delay could be useful during key events, such as when a flag is about to be retrieved by an exploit. The network delay would allow the reset to be sent before the flag. The following command induces such a delay for a second,

```sudo tc qdisc add dev [interface] root netem delay 1000ms```

And to remove the delay,

```sudo tc qdisc del dev [interface] root```

