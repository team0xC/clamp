# Tools for Investigate Network Traffic Anomalies
## Arkime 
Arkime is a full-packet ingestion and indexing platform. It reads a live network data stream or existing pcap files, then extracts data from known protocol fields to store in an Elasticsearch backend.
### tcpdump: Log or parse network traffic
>$ tcpdump -n -r infile.pcap -w tcp80.pcap 'tcp port 80'
>$ sudo tcpdump -n -i enp0s3 -w outfile.pcap 
>$ sudo tcpdump -n -i enp0s3 -C 1024 -G 100 -w 10GB_rolling_buffer.pcap 
$ sudo tcpdump -n -i enp0s8 -G 86400 -w dns-%F.%T.pcap 
### Wireshark
Deep, protocol-aware packet exploration and analysis
### mergecap
Merge two or more pcap files
### editcap
Modify contents of a capture file
>$ editcap -A '2017-01-16 00:00:00' -B '2017-02-16 00:00:00' infile.pcap 2017-jan-16.pcap
>$ editcap -d infile.pcap dedupe.pcap
>$ editcap -i 3600 infile.pcap hourly.pcap
### tshark
Command-line access to nearly all Wireshark features
>$ tshark -n -r infile.pcap  -Y 'http.host contains "google"'  -T fields -e ip.src -e http.host  -e http.user_agent
>$ tshark -n -r infile.pcap  -Y 'ssl.handshake.certificates'  -w just_certificates.pcap
### lsof
List of Open files
>$sudo lsof -iTCP -P -n   (List of open TCP connections)
>$sudo lsof -R -p 2106   (Get FD, sockets and pipes used by specific PIDs)
### tcpxtract
Carve reassembled TCP streams for known header and footer bytes to attempt file reassembly

Signature format:
>file_ext(max_size, start_bytes, end_bytes);

Signature examples:
>gif(3000000, \x47\x49\x46\x38\x37\x61, \x00\x3b);
>rpm(400000000, \xed\xab\xee\xdb);

Example:
>tcpxtract -f infile.pcap -c rpm-tcpxtract.conf -o ./
### grep
Display lines from input text that match a specified regular expression pattern
>$ grep pastebin access.log
>$ grep -rail google /var/spool/squid/
>$ grep -Fv 192.168.75. syslog-messages
>$ grep -C 5 utmscr error.log
### capinfos
Calculate and display high-level summary statistics for an input pcap file
>$ capinfos -A infile.pcap
>$ capinfos -A -T infile2.pcap
>$ capinfos -A *.pcap
### ngrep
Display metadata and context from packets that match a specified regular expression pattern
>$ ngrep -I infile.pcap 'RETR' 'tcp and port 21'
>$ ngrep -I infile.pcap -i 'l33tAUTH'
### tcpflow
Reassemble input packet data to TCP data segments 
>$ tcpflow -r infile.pcap -o /tmp/output/
>$ tcpflow -l *.pcap -o /tmp/output/
