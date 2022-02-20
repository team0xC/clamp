#!/bin/bash

while [ $# -gt 0 ]; do
  case "$1" in
    --interface=*)
      interface="${1#*=}"
      ;;
    --num_workers=*)
      num_workers="${1#*=}"
      ;;
    --prj_path=*)
      prj_path="${1#*=}"
      ;;
    *)
      printf "***************************\n"
      printf "* Error: Invalid argument.*\n"
      printf "***************************\n"
      exit 1
  esac
  shift
done

if [[ -z "$interface" ]]
then
  printf '%s\n' "--interface is mandatory" >&2
  exit 1
elif [[ -z "$prj_path" ]]
then
  printf '%s\n' "--prj_path is mandatory" >&2
  exit 1
elif [[ -z "$num_workers" ]]
then
    num_workers=4
fi

if [ ! -d "$HOME/firewall_pyvenv" ]
then
  sudo apt update
  sudo apt install redis-server
  "Y"|sudo apt install redis-server
  sudo cp $prj_path/resources/redis.conf  /etc/redis/redis.conf
  sudo systemctl restart redis.service
  sudo systemctl status redis
  "Y"|sudo apt install dsniff
  sudo apt-get install python3.6-venv
  /usr/bin/python3 -m venv ~/firewall_pyvenv
  ~/firewall_pyvenv/bin/python -m pip install -r $prj_path/requirements.txt

  sed "s|@home@|${HOME}|" <$prj_path/resources/sniffer_template.service >$prj_path/resources/sniffer.service;
  sed -i "s|@prj_dir@|$prj_path|" $prj_path/resources/sniffer.service;
  sed -i "s|@interface@|$interface|" $prj_path/resources/sniffer.service;

  sudo cp $prj_path/resources/sniffer.service /etc/systemd/system/sniffer.service
  sudo systemctl enable sniffer.service
  sudo systemctl start sniffer.service
  sudo systemctl status sniffer.service
fi


capturer_proc="capturer -i \"$interface\""
makerun="$HOME/firewall_pyvenv/bin/python -m "${capturer_proc}
src_dir="$prj_path/src"

summarizer_proc="summarizer"
makerun="$HOME/firewall_pyvenv/bin/python -m "${summarizer_proc}
if ps ax | grep -v grep | grep -v bash | grep --quiet "/firewall_pyvenv/bin/python -m summarizer"
      then
          #printf "Process '%s' is running.\n" "$process"
          :
      else
          printf "Starting process '%s' with command '%s'.\n" "$summarizer_proc" "$makerun"
          `(cd $src_dir && $makerun)`  2>&1  >/dev/null & disown;
fi

for i in $(seq 1 "$(expr $num_workers + 0)")
do
    eval "process$i=\"ip_kill_workers -n killer_$i\"";
    eval "makerun$i=\"$HOME/firewall_pyvenv/bin/python ""-m \${process$i}\""
    if ps ax | grep -v grep | grep -v bash | grep --quiet killer_$i
    then
        #printf "Process '%s' is running.\n" "$process1"
        :
    else
        printf "Starting ip_killer-"$i"\n"
        eval "(cd \$src_dir && \$makerun$i)" &>/dev/null & disown;
    fi
done