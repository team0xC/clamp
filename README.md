# CLAMP
CTF Logger Analyzer Mimicker Patcher

CLAMP consist of the following elements:

1. Database of vulnerabilities and exploits
	- [pctf.db](data/pctf.db)
	- [models.py](models.py)
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
	- https://docs.google.com/document/d/13cRbKB0WiuiLUDPpQ-4POr7_HJplsGUN54HbSIjyc6Y/edit?usp=sharing


## Developer Setup

0. Create a virtual Python environment

		$ python3 -m venv ENV

1. Activate the virtual environment

		$ source ENV/bin/activate

2. Install the dependencies

		(ENV)$ pip install -r requirements.txt

## Testing

Tests are run with Python's standard testing package `unittest`.

		(ENV)$ python -m unittest
		
