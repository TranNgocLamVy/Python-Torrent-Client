import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from threading import Thread

from torrent_parser import TorrentParser
from tracker import Tracker
from piece_manager import PieceManager
from peer_manager import PeerManager
 
class TorrentClient:
    def __init__(self, container, file_name, id: str):
        self.container = container
        self.id = id
        self.torrent = TorrentParser(file_name, self.id)
        self.tracker = Tracker(self.torrent, self.id)
        self.init_gui()
        self.piece_manager = PieceManager(self.torrent, self.progress, self.id)
        self.peer_manager = PeerManager(self.torrent, self.tracker, self.id)


    def run(self):
        thread = Thread(target=self.download_torrent_file, daemon=True)
        thread.start()


    def init_gui(self):
        self.frame = ttk.Labelframe(self.container, text=self.torrent.root_name, bootstyle="primary")

        delete_button = ttk.Button(self.frame, text="Delete", command=self.delete_torrent, bootstyle="danger-outline")

        download_button = ttk.Button(self.frame, text="Download", command=self.run, bootstyle="primary-outline")

        self.progress = ttk.Progressbar(self.frame, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(padx=10, pady=10, side=LEFT)

        self.frame.pack(fill="x", side=TOP)
        delete_button.pack(padx=10, pady=10, side=RIGHT)
        download_button.pack(padx=10, pady=10, side=RIGHT)

        
    def download_torrent_file(self):
        self.piece_manager.generate_pieces()
        self.peer_manager.connect_all_peers()

        print("Downloading...")
        thread_list = []
        while not self.piece_manager.is_complete:
            piece_index = self.piece_manager.get_unfinished_piece()
            if piece_index == -1:
                continue
            peer = self.peer_manager.get_fitst_peer_has_piece(piece_index)
            if not peer:
                continue
            thread = peer.download_piece(self.piece_manager.pieces[piece_index])
            thread_list.append(thread)
        
        for thread in thread_list:
            thread.join()
        print("Downloaded successfully")

    def delete_torrent(self):
        self.frame.destroy()
        del self
        