from torrent_parser import TorrentParser
import requests
import struct
import socket
from bcoding import bdecode

class Tracker(object):
    def __init__ (self, torrent: TorrentParser, id: str):
        self.id = id
        self.torrent = torrent
        self.peers = self.get_peers()

    def get_peers(self):
        params = {
            'info_hash': self.torrent.info_hash,
            'peer_id': '00112233445566778897',
            'port': 6881, # default port for torrent
            'uploaded': 0,
            'downloaded': 0,
            'left': self.torrent.torrent_length,
            'compact': 1
        }
        
        tracker_urls = self.torrent.get_tracker_urls
        peers = []
        for tracker_url in tracker_urls:
            if(tracker_url[0].startswith(b'udp')):
                continue
            raw_resp = requests.get(url=tracker_url[0], params=params, timeout=10)
            raw_resp.raise_for_status()
            list_peers = bdecode(raw_resp.content)
            offset = 0
            if not type(list_peers.get("peers")) == list:
                for _ in range(len(list_peers.get("peers"))//6):
                    ip = struct.unpack_from("!i", list_peers.get("peers"), offset)[0]
                    ip = socket.inet_ntoa(struct.pack("!i", ip))
                    offset += 4
                    port = struct.unpack_from("!H",list_peers.get("peers"), offset)[0]
                    offset += 2
                    peers.append(f'{ip}:{port}')
            else:
                for p in list_peers.get("peers"):
                    peers.append(f'{p['ip']}:{p['port']}')
        return list(set(peers))