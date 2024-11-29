from peer import Peer, PeerState
from torrent_parser import TorrentParser
from tracker import Tracker
from typing import List



class PeerManager(object):
    def __init__(self, torrent: TorrentParser, tracker: Tracker, id: str):
        self.id = id
        self.torrent = torrent
        self.peers: List[Peer] = []
        self.generate_peers(tracker.peers)

    def generate_peers(self, peers):
        peer_list = []
        for peer in peers:
            ip = peer.split(':')[0]
            port = int(peer.split(':')[1])
            peer_list.append(Peer(ip, port, self.torrent.num_pieces, self.torrent.info_hash, self.id))
        self.peers = peer_list

    def connect_all_peers(self):
        for peer in self.peers:
            if not peer.healthy:
                peer.connect()

    def get_fitst_peer_has_piece(self, piece_index):
        for peer in self.peers:
            if peer.has_piece(piece_index) and peer.state == PeerState.Free:
                return peer
        return None