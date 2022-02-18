from redis_connection import get_redis_connection
import argparse
from time import time
import csv
import json
from time import sleep
from datetime import datetime
from pathlib import Path


def summarizer(queue_name, log_path, freq):
    r_conn = get_redis_connection()
    start_time = time()
    messages = {}
    while True:
        encoded_message = r_conn.rpop(queue_name)
        if not encoded_message:
            sleep(2)
            continue
        message = json.loads(encoded_message.decode())

        history = {}
        summary = {}

        if message is not None and isinstance(message, dict):
            interface = message.get('i')
            src_ip = message.get('sip')
            dst_port = message.get('dp')
            src_eth = message.get('se').replace(":", "-")
            data = message.get('d')[:-1]
            sniff_time = datetime.strptime(message.get('st'), "%Y-%m-%d %H:%M:%S.%f")
            key = f"{interface}/{src_ip}/{src_eth}/{dst_port}"
            if key in messages:
                messages[key]['sniff_time'].append(sniff_time)
                messages[key]['data'].append(data)
            else:
                messages[key] = {'sniff_time': [sniff_time], 'data': [data]}

        if time() - start_time > freq:
            if Path(log_path).exists():
                with open(log_path) as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    line_count = 0
                    for row in csv_reader:
                        if line_count == 0:
                            line_count += 1
                        else:
                            history[row[0]] = {"last_req_time": datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S.%f"),
                                               "time_btw_req": row[2],
                                               "all_data": row[3]}
                            line_count += 1

            for each_key in messages:
                if each_key in history:
                    summary[each_key] = {"last_req_time": max([min(messages[each_key]['sniff_time']),
                                                               history[each_key]['last_req_time']]),
                                         "time_btw_req": (float(history[each_key]['time_btw_req']) +
                                                          (min(messages[each_key]['sniff_time'])-history[each_key]['last_req_time']).seconds) / 2,
                                         "all_data": history[each_key]['all_data'] + "--" + "--".join(
                                             messages[each_key]['data'])
                                         }
                else:
                    summary[each_key] = {"last_req_time": min(messages[each_key]['sniff_time']),
                                         "time_btw_req": "0",
                                         "all_data": "--".join(messages[each_key]['data'])
                                         }

            with open(log_path, mode='w') as csv_file:
                csv_file_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_file_writer.writerow(
                    [f"interface/src_ip/src_eth/dst_port", "last_req_time", "time_btw_req", "all_data"])
                for each_key in summary:
                    csv_file_writer.writerow(
                        [each_key, summary[each_key]["last_req_time"].strftime("%Y-%m-%d %H:%M:%S.%f"),
                         summary[each_key]["time_btw_req"],
                         summary[each_key]["all_data"],
                         ])

            del messages
            messages = {}
            start_time = time()
            continue


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--queue_name", help="Enter worker queue name", required=False,
                        default="summarizer")
    parser.add_argument("-l", "--log_path", help="log path", required=False,
                        default="../summary_logs/firewall_summary.csv")
    parser.add_argument("-t", "--freq", help="frequency of summary generation in seconds", required=False,
                        default=120, type=int)
    args = parser.parse_args()

    summarizer(queue_name=args.queue_name, log_path=args.log_path, freq=args.freq)
