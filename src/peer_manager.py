from peer import Peer
from piece_manager import PieceManager
from torrent_parser import TorrentParser
from typing import List



class PeerManager(object):
    def __init__(self, torrent: TorrentParser, pieces_manager: PieceManager):
        self.torrent = torrent
        self.pieces_manager = pieces_manager
        self.pieces_by_peer = [[0, []] for _ in range(pieces_manager.num_pieces)]
        self.peers: List[Peer] = []

    def generate_peers(self, peers):
        for peer in peers:
            ip = peer.split(':')[0]
            port = int(peer.split(':')[1])
            self.peers.append(Peer(ip, port, self.torrent.num_pieces, self.torrent.info_hash))

    def connect_all_peers(self):
        for peer in self.peers:
            peer.connect()

    def get_fitst_peer_has_piece(self, piece_index):
        for peer in self.peers:
            if peer.has_piece(piece_index):
                print("Peer ip:%s - port:%s has piece: %s" % (peer.ip, peer.port, piece_index))
                return peer
        return None