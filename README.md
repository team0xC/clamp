# CLAMP

### Project Description

CLAMP was developed as the final project for ASU's CSE545 Software Security, as a set of tools to more effectively play in the class CTF competition. CLAMP stands for *CTF Logger Analyzer Mimicker Patcher*, the parts that were originally conceived to be in the project. However, since the short time frame of the course precluded dependencies between the parts, and since the analyzer and mimicker depended on having an interface to the logger and sample *pcap* files similar to actual CTF attacks, we opted to replace these parts with a firewall and encryption scripts that could be used to patch services.

### The Elements

CLAMP consist of the following elements, organized by the member of the team that authored them. Despite varying contributions to code, we'd stress that each member provided equally valuable input throughout the project cycle, much of which is in between the lines of code.

#### Database (lead: Joshua Gomez)

This database stores vulnerabilities and exploit scripts. It includes models (see the [code](models.py)) using the  *sqlalchemy* ORM to provide an interface, and unit tests to make sure that it all works (see the [code](testse.py)). For more information, see the directory [data](data/).

#### Executor (lead: Jonathan Chang)

The executor and interceptor runs scripts to exploit services and reset incoming connections respectively. For more information, see the directory [executor](executor/).

#### Logger (lead: Michael Kotovsky)

The logger, configurable with *Berkeley Packet Filter (BPF)* syntax generates Wireshark .pcap files on demand. For more information, see the directory [capture](capture/).

#### Firewall (lead: Kumar Raj)

The firewall monitors incoming TCP requests and sends a reset flag whenever any keywords on its black list are encountered. For more information, see the directory [firewall](firewall/).

#### Analyzer (lead: Mehran Tajbakhsh)

The analyzer pattern matches for flags in the bodies of incoming TCP requests, and could be expanded for more functionality (see the [code](analyzer.py)). A list of useful tools during the competition was also compiled. For more information, see the directory [doc](docs/).

#### Encryption & Patching Checklists (lead: Jonathan Ong)

These are encryption snippets written in C, PHP and Python, so that we could setup the encryption patch as quickly as possible. For more information, see the directory [encryption snippets](encryption%20snippets). The patching [checklist](https://docs.google.com/document/d/13cRbKB0WiuiLUDPpQ-4POr7_HJplsGUN54HbSIjyc6Y/edit?usp=sharing) was developed to help us complete our setup thoroughly and to identify common vulnerabilities during the competition.

## Flow Diagram

```mermaid
flowchart TD
    Adversaries(Adversaries)
    Inbound_Attack[\Inbound Attack/]
    Firewall[[Firewall]]
    Blacklist[/Blacklist\]
    Logger[[Logger]]
    Service([Service])
    Response1[/Response\]
    Log_Files[/Log Files\]
    Analyzer[[Analyzer]]
    Database[(Database)]
    Mimicker[[Mimicker]]
    Exploit[/Exploit Script/]
    Executor[[Executor]]
    Outbound_Attack[\Outbound Attack/]
    Victims(Victims)
    Response2[/Response\]
    Patcher[[Patcher]]
    ScoreKeeper(ScoreKeeper)

    Adversaries -- 1-send --> Inbound_Attack
    Inbound_Attack -- 2a-captured by --> Firewall
    Firewall <-- 2b-looks up --> Blacklist
    Firewall -- 2c-resets connection --> Inbound_Attack
    Inbound_Attack -- 3a-capture by --> Logger
    Logger -- 3b-stores --> Log_Files
    Inbound_Attack -- 4a-reaches --> Service
    Service -- 4b-returns --> Response1
    Response1 -- 4c-captured by --> Logger
    Response1 -- 4d-received by --> Adversaries
    Log_Files -- 5-read by --> Analyzer
    Analyzer -- 6-updates --> Database
    Database -- 7-read by --> Mimicker
    Mimicker -- 8a-produces --> Exploit
    Mimicker -- 8b-updates --> Database
    Executor <-- 9a-reads from --> Database
    Executor -- 9b-runs --> Exploit
    Exploit -- 10a-sends --> Outbound_Attack
    Outbound_Attack -- 10b-targets --> Victims
    Victims -- 10c-returns --> Response2
    Response2 -- 10d-captured by --> Exploit
    Exploit -- 10e-reports to --> Executor
    Executor -- 11a-submits flag --> ScoreKeeper
    Executor -- 11b-updates --> Database
    Database -- 13-read by --> Patcher
    Patcher -- 14a-patches --> Service
    Patcher -- 14b-updates --> Database
```


### Developer Setup

1. Create a virtual Python environment

```bash
$ python3 -m venv ENV
```

2. Activate the virtual environment

```bash
$ source ENV/bin/activate
```

3. Install the dependencies

```bash
(ENV)$ pip install -r requirements.txt
```

### Testing

Tests are run with Python's standard testing package `unittest`.

```bash
(ENV)$ python -m unittest
```

### Dependencies

* Dumpcap - [https://www.wireshark.org/docs/man-pages/dumpcap.html](https://www.wireshark.org/docs/man-pages/dumpcap.html)
* PyShark 0.4.5 - [http://kiminewt.github.io/pyshark/](http://kiminewt.github.io/pyshark/)
* Redis 6.2 - [https://redis.io/documentation](https://redis.io/documentation)
* Scapy 2.4.5 - [https://scapy.readthedocs.io/en/latest/](https://scapy.readthedocs.io/en/latest/)
* SQL Alchemy 1.4 - [https://docs.sqlalchemy.org/en/14/intro.html#installation](https://docs.sqlalchemy.org/en/14/intro.html#installation)
* SQLite 3 - [https://www.sqlite.org/docs.html](https://www.sqlite.org/docs.html)
* SWPAG Client 0.3.7 - [https://pypi.org/project/swpag-client/](https://pypi.org/project/swpag-client/)

### Authors

* **Joshua Gomez** - [joshuago78](https://github.com/joshuago78)
* **Jonathan Chang** - [jachang820](https://github.com/jachang820)
* **Michael Kotovsky** - [mkotovsk-asu-edu](https://github.com/mkotovsk-asu-edu)
* **Kumar Raj** - [k-raj](https://github.com/k-raj)
* **Mehran Tajbakhsh** - [MehranTJB](https://github.com/MehranTJB)
* **Jonathan Ong** - [jonathanongucla](https://github.com/jonathanongucla)
