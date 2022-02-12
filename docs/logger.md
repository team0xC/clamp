#CLAMP Logger module

Configuration changes, including users, locations and other details can be found by editing
		./capture/capture.cfg

## To Install utilities (via apt), services and crontab (as root)
		./capture/capture.install.asroot

Once installed, the service (default name: clamp-capture) can be stopped/started via
		service clamp-capture start
		service clamp-capture stop
		service clamp-capture status

( Scripts can also be invoked using /etc/init.d/clamp-capture )

## To Uninstall
		./capture/capture.uninstall.asroot

( Cleanup users/groups as necessary. By default the clamp user is created and added to the wireshark group )

## Notes:
	- Default capture location can be found in capture/pcap
	- Default daemon user and pcap owner is: clamp
	- Old pcap files will be compressed/archived as need, see capture/capture.cfg file for options
