from torrent_parser import TorrentParser
from tracker import Tracker
from piece_manager import PieceManager
from peer_manager import PeerManager
 
class TorrentClient(object):
    def __init__(self, file_name):
        self.torrent = TorrentParser(file_name)
        self.tracker = Tracker(self.torrent)
        self.piece_manager = PieceManager(self.torrent)
        self.peer_manager = PeerManager(self.torrent, self.piece_manager)
        
    def download_torrent_file(self):
        self.peer_manager.generate_peers(self.tracker.peers)
        self.peer_manager.connect_all_peers()

        print("Downloading...")
        while not self.piece_manager.is_complete:
            piece_index = self.piece_manager.get_unfinished_piece()
            if piece_index == -1:
                break
            print("")
            print("--------------------")
            print("")
            print("Download piece ", piece_index)

            peer = self.peer_manager.get_fitst_peer_has_piece(piece_index)
            if not peer:
                break

            peer.download_piece(self.piece_manager.pieces[piece_index])
        
        print("Downloaded successfully")
        