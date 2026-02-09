import json
import time
import random

class Packet:
    def __init__(self, src_ip, dest_ip, size_kb, payload_type):
        self.packet_id = random.randint(1000, 9999)
        self.src_ip = src_ip
        self.dest_ip = dest_ip
        self.size_kb = size_kb
        self.payload_type = payload_type
        self.timestamp = time.time()

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(data):
        obj = json.loads(data)
        pkt = Packet(
            obj["src_ip"],
            obj["dest_ip"],
            obj["size_kb"],
            obj["payload_type"]
        )
        pkt.packet_id = obj["packet_id"]
        pkt.timestamp = obj["timestamp"]
        return pkt
