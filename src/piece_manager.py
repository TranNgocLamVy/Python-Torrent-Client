from torrent_parser import TorrentParser
from piece import Piece, PieceState
from pydispatch import dispatcher
from ttkbootstrap import Progressbar
from threading import Lock, Thread

lock = Lock()
class PieceManager(Thread):
    def __init__(self, torrent: TorrentParser, progress: Progressbar, id: str):
        super().__init__()
        self.daemon = True
        self.id = id
        self.torrent = torrent
        self.progress = progress
        self.num_pieces = int(torrent.num_pieces)
        self.complete_pieces = 0
        self.pieces = []
        dispatcher.connect(self.receive_piece_data, signal = f"PiecesManager.Piece {self.id}", sender = dispatcher.Any)
        self.start()

    def generate_pieces(self):
        self.complete_pieces = 0
        self.progress["value"] = 0
        self.progress.update_idletasks()
        pieces = []
        last_piece = self.torrent.num_pieces - 1
        for index in range(self.num_pieces):
            if index == last_piece:
                piece_length = self.torrent.torrent_length - (self.torrent.num_pieces - 1) * self.torrent.piece_length
                pieces.append(Piece(index, piece_length, self.torrent.piece_hashes_in_hex[index]))
            else:
                pieces.append(Piece(index, self.torrent.piece_length, self.torrent.piece_hashes_in_hex[index]))
        self.pieces = pieces

    @property
    def is_complete(self):
        return self.complete_pieces == self.num_pieces
    
    def get_unfinished_piece(self):
        for index in range(self.num_pieces):
            piece: Piece = self.pieces[index]
            if piece.state == PieceState.UNFINISHED:
                return index
        return -1

    def receive_piece_data(self, sender):
        global lock
        with lock:
            piece_index = sender.get("piece_index")
            piece_data = sender.get("piece_data")
            peer = sender.get("peer")
            piece_offset = piece_index * self.torrent.piece_length
            print(f"Receiving piece {piece_index} data from {peer}")

            if self.pieces[piece_index].state != PieceState.PENDING:
                return

            piece: Piece = self.pieces[piece_index]

            try:
                f = open(self.torrent.root_name, 'r+b')
            except IOError:
                f = open(self.torrent.root_name, 'wb')
            
            f.seek(piece_offset)
            f.write(piece_data)
            f.close()
            print("Writing piece", piece_index, "to disk")

            piece.state = PieceState.FINISHED
            self.complete_pieces += 1
            self.progress["value"] = (self.complete_pieces / self.num_pieces) * 100
            self.progress.update_idletasks()  