## Checklist for Network Traffic Anomalies
### HTTP GET vs POST Ratio
This ratio establish a typical profile for HTTP traffic. When it skews too far from the normal baseline, it may suggest brute force, SQL injection attempts, RAT usage, server feature probing or other suspicious activity.
### HTTP User-Agent
Rapid change for a given IP address, significant increase in the number of observed User_Agent string, which may highlight suspicious activity.
### Top DNS Domain Queried
The most frequently queried second-level domain based on internal clients' requests activity.
### HTTP Return Code Ratio
- 100s: Informational
- 200s: Success
- 300s: Redirection
- 400s: Client-side error
- 500s: Server-side error

A spike in 400-series codes could indicate reconnaissance or scanning activity, while an unusually high number of 500-series codes could indicate failed loginor SQL injection attempts. 
### Newly-Observed/Newly-Registered Domains
The first time a domain is queried in a given environment may indicate a new or highly-focused targeting operation. Brand new domains are often associated with malicious activity, given that attackers generally require a dynamic infrastructure for their operations.
### External Infrastructure Usage Attempts
By identifying internal clients that attempts to or succeed in using external services, it is possible to quickly collect a list of endpoints that exhibit anomalous behaviour. These may include connections to external DNS servers rather than internal resolvers, HTTP connection attempts that seek to bypass proxy servers, connections to VPN providers, raw socket connections to unusual ports.
### Typical Port and Protocol Usage
Similar to the purpose for tracking top-talking IP addresses, knowing the typical port and protocol usage enables quick identification of anomalies that should be further explored for potential suspicious activity.
### DNS TTL Values and RR Counts
Very short TTLs may suggest fast-flux DNS or potential tunneling behaviour. A high RR count could indicate largescale load balancing assiciated with fast-flux or similar elastic architectures.
### Autonomous System Communications
Certain ASNs ore often more prominently associated with malicious activity than others. Reputation databases can be useful in determining these. 
### Periodic Traffic  Volume Metrics
These will identify normative traffic patterns, making deviations easier to spot and investigate. A sudden spike of traffic or connections during a period would be a clear anomaly to concern.
