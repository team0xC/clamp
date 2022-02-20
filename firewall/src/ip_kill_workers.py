import argparse
from time import time
import subprocess
import json
import logging
from redis_connection import get_redis_connection


logging.basicConfig(filename="../summary_logs/ip_killer.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


def read_bl_keywords(path="./bl_keywords.json"):
    with open(path, "r") as f:
        bl_keywords = json.load(fp=f)
        exclusions = bl_keywords['exclusion']
        del bl_keywords['exclusion']
        for key in exclusions:
            bl_keywords[key] = list(set(bl_keywords["*"]) - set(exclusions[key]))
        return bl_keywords


def worker(queue_name, bl_path, bl_read_freq=60, kill_sec=5):
    r_conn = get_redis_connection()
    bl_keywords = read_bl_keywords(bl_path)
    start_time = time()
    while True:
        encoded_message = r_conn.rpop(queue_name)
        if not encoded_message:
            continue
        message = json.loads(encoded_message.decode())
        if time() - start_time > bl_read_freq:
            bl_keywords = read_bl_keywords(bl_path)
            start_time = time()
        if message is not None and isinstance(message, dict):
            interface = message.get('i')
            src_ip = message.get('sip')
            src_port = message.get('sp')
            dst_port = message.get('dst_port')
            data = message.get('d').replace("\n", " ")
            for i in bl_keywords.get(dst_port, bl_keywords["*"]):
                if i in data:
                    if not r_conn.get(f"{src_ip}__{src_port}"):
                        command = f"sudo timeout {kill_sec}s tcpkill -i any -9 host {src_ip} and port {src_port} >/dev/null 2>&1"
                        subprocess.Popen(command, shell=True)
                        logging.info(f"BLOCKED::::::IP:{src_ip}--Port:{src_port}--Data:{data}:::")
                        r_conn.setex(f"{src_ip}__{src_port}", kill_sec, 1)
                    break
            r_conn.lpush("summarizer", encoded_message)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--queue_name", help="Enter worker queue name", required=False, default="ip_kill")
    parser.add_argument("-d", "--bl_file", help="Blacklisted keywords file path", required=False,
                        default="../resources/bl_keywords.json")
    parser.add_argument("-k", "--kill_sec", help="duration to open tcpkill monitor for an ip and port", required=False,
                        default=6, type=int)
    parser.add_argument("-n", "--name", help="worker name", required=True)
    args = parser.parse_args()

    worker(queue_name=args.queue_name, bl_path=args.bl_file, kill_sec=args.kill_sec)
