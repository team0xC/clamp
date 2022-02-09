# Memory Investigation/Threat Hunting
The  Volatility  Framework  is a completely open collection of tools for the extraction of digital artifacts from volatile memory (RAM) samples. It is useful in forensics  analysis. The  extraction  techniques  are  performed  completely  independent  of  the system being investigated but offer unprecedented visibility into the runtime state of the system. 
Getting Help
>vol.py -h  *(shows options and supported plugins)*
vol.py pluin -h *(show plugin usage)*
col.py plugin --info   *(show available OS profiles)*
## Identify Rogue Process
>vol.py pslist *(High level view of running processes)*
vol.py  psscan   *(Scan memory for EPROCESS blocks)*
vol.py pstree *(Display parent-process relationships*
## Analyze Process DLLs and Handles
>vol.py dlllist -p 1022,868   *(Show information only for specific) processes (PIDs)*
vol.py getsids -p 868  *(Print process security identifiers for specific PIDs)*
vol.py handles -p 868 -t  *(List of open handles for specific processes (PIDs)*
- __handles: Process, Thread, Key, Event, File, Mount, Token, Port__

## Review Network Artifacts
>vol.py netscan   *(Scan for TCP connections and sockets)*
## Look for Evidence of Code Injection
>vol.py malfind -p 868 --dumpdir ./output_dir    *(Find injected code and dump sections for specific PIDs)*
vol.py ldrmodules -p 868 -v   *(Detect unlink DLLs for specific PIDs)*
vol.py hollowfind -p 868 -D ./output_dir   *(Detect process hollowing techniques for specific PIDs)*
## Check for Sign of a Rootkit
>vol.py psxview    *(Find hidden process using cross-view)*
vol.py modscan   *(Scan memory for loaded, unloaded, and unlinked drivers)*
vol.py apihooks -p 868  *(Find API/DLL  function hooks for specific PIDs)*
vol.py ssdt    | egrepv -v   *(Hooks in System Service Descriptor Table)*

__(use vol.py --info | grep Debian       :to find proper profile)__
>vol.py driverirp -r tcpip   (Identify I/O request packet (IRP) hooks)
# Memory Monitoring
#### Execsnoop
Leverage ftrace to record exec() calls
>execsnoop-pref -a 16 -r > log.txt      *(-a max arguments to show / -r include re-execs)*
#### Forkstat
records the following events:
__fork, exec, exit, core, comm, clone, ptrce, uid, sid, all__
>forkstat -e all -x -S >forklog.txt