#!/usr/bin/env python3
import pyshark
import argparse
import json
from redis_connection import get_redis_connection
import os
import logging


class SniffBlock(object):

    def __init__(self, services_json_path, interface, packet_len_filter):
        with open(services_json_path, "r") as f:
            self._services = json.load(fp=f)
        self._interface = interface
        self._packet_len_filter = packet_len_filter
        self._redis_con = get_redis_connection()
        self._debug = os.environ.get('DEBUG', False)

    def _packet_processor_callback(self, packet):
        protocol = packet.transport_layer
        src_addr = packet.ip.src
        src_port = packet[protocol].srcport
        # dst_addr = packet.ip.dst
        dst_port = packet[protocol].dstport
        try:
            src_eth = packet.eth.src
        except:
            src_eth = "undefined"
        # dst_eth = packet.eth.dst
        sniff_time = packet.sniff_time
        # packet_length = packet.length

        try:
            decoded_data = bytearray.fromhex(packet.data.data).decode()
        except AttributeError:
            decoded_data = None
        except UnicodeDecodeError:
            decoded_data = "cat"

        if decoded_data:
            payload = {
                "i": self._interface,
                "sip": src_addr,
                "sp": src_port,
                "d": decoded_data,
                "st": sniff_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
                "dp": dst_port,
                "se": src_eth,

            }
            payload = json.dumps(payload)
            if self._debug:
                print(json.dumps(payload))
            self._redis_con.lpush("ip_kill", payload)

    def sniffer(self):
        bpf_filer_string = " or ".join(
            [f"{value[0]} dst port {value[1]}" for key, value in self._services.items()])
        bpf_filer_string += f" and greater {self._packet_len_filter}"
        capture = pyshark.LiveCapture(interface=self._interface, bpf_filter=bpf_filer_string)
        print("listening on %s" % self._interface)
        capture.apply_on_packets(self._packet_processor_callback)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--services_json_path", help="running services json path",
                        required=False, default="../resources/services.json")
    parser.add_argument("-i", "--interface", help="interface to listen on",
                        required=True, default=None)
    parser.add_argument("-l", "--packet_len_filter", help="minimum length of packet to monitor",
                        required=False, default=60)
    args = parser.parse_args()

    SniffBlock(args.services_json_path, args.interface, args.packet_len_filter).sniffer()
