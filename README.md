# CLAMP
CTF Logger Analyzer Mimicker Patcher

CLAMP consist of the following elements:

1. Database of vulnerabilities and exploits
	- [pctf.db](pctf.db)
2. Executor: the orchestrator of attacks
	- [executor.py](executor.py)
3. Logger of traffic
	- [docs/logger.md](docs/logger.md)
4. Analyzer of traffic
	- [analyzer.py](analyzer.py)
5. Mimicker of attacks
	- TBD
6. Patcher of vulnerabilities
	- [docs/patcher_checklist.md](docs/patcher_checklist.md)


## Developer Setup

0. Create a virtual Python environment

		$ python3 -m venv ENV

1. Activate the virtual environment

		$ source ENV/bin/activate

2. Install the dependencies

		(ENV)$ pip install -r requirements.txt

