from torrent_parser import TorrentParser
from piece import Piece, PieceState
from pydispatch import dispatcher

class PieceManager(object):
    def __init__(self, torrent: TorrentParser):
        self.torrent = torrent
        self.num_pieces = int(torrent.num_pieces)
        self.complete_pieces = 0
        self.pieces = self.generate_pieces()

        dispatcher.connect(self.receive_piece_data, signal = "PiecesManager.Piece", sender = dispatcher.Any)


    def generate_pieces(self):
        pieces = []
        last_piece = self.torrent.num_pieces - 1
        for index in range(self.num_pieces):
            start = index * 20
            end = start + 20
            if index == last_piece:
                piece_length = self.torrent.torrent_length - (self.torrent.num_pieces - 1) * self.torrent.piece_length
                pieces.append(Piece(index, piece_length, self.torrent.piece_hashes_in_hex[start:end]))
            else:
                pieces.append(Piece(index, self.torrent.piece_length, self.torrent.piece_hashes_in_hex[start:end]))
        return pieces

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
        piece_index = sender.get("piece_index")
        piece_offset = piece_index * self.torrent.piece_length
        piece_data = sender.get("piece_data")

        piece: Piece = self.pieces[piece_index]

        if not piece or piece.state == PieceState.FINISHED:
            return

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