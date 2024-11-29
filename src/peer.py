import socket
import bitstring
from pydispatch import dispatcher

from message import MessageIDs, HandShake, RequestBlock, InterestedMessage
from piece import Piece, PieceState
from block import BlockState

class Peer(object):
    def __init__(self, ip: str, port: int, number_of_pieces: int, info_hash: bytes):
        self.ip = ip
        self.port = port

        self.has_handshaked = False
        self.healthy = False
        self.read_buffer = b''

        self.number_of_pieces = number_of_pieces
        self.info_hash = info_hash
        self.bit_field = bitstring.BitArray(number_of_pieces)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.peer_id = '00112233445566778899'

    def connect(self):
        handshake = HandShake(self.info_hash, self.peer_id.encode())
        interested_message = InterestedMessage()
        try:
            self.socket.connect((self.ip, self.port))
            self.socket.sendall(handshake.create_request())
            self.socket.recv(68)
            self.bit_field = self.wait_for_bitfield()
            self.socket.sendall(interested_message.create_request())
            self.wait_for_unchoke()

            self.healthy = True
            self.has_handshaked = True
            print("Connected success to peer (ip: %s - port: %s), bitfield: %s" % (self.ip, self.port, self.bit_field))
            return True
        except Exception as exception:
            print("Failed to connect to peer (ip: %s - port: %s - %s)" % (self.ip, self.port, exception.__str__()))
            return False
        
    def has_piece(self, piece_index):
        if not self.healthy:
            return False
        return self.bit_field[piece_index]

    def wait_for_peer_response(self, message_id):
        reciveved_id, data = self.recieve_data()
        while message_id != reciveved_id:
            reciveved_id, data = self.recieve_data()
        return data
    
    def wait_for_unchoke(self):
        return self.wait_for_peer_response(MessageIDs.UNCHOKE)
    
    def wait_for_bitfield(self):
        response = self.wait_for_peer_response(MessageIDs.BITFIELD)
        return ''.join(f'{byte:08b}' for byte in response)
    
    def recieve_data(self):
        length = b''
        while not length or not int.from_bytes(length, 'big'):
            length = self.socket.recv(4)
        
        length = int.from_bytes(length, 'big')
        data = self.socket.recv(length)
        while len(data) < length:
            data += self.socket.recv(length)

        message_id = int.from_bytes(data[:1], 'big')
        data = data[1:]

        return message_id, data

    def download_block(self, piece_index, offset, block_length):
        request_block = RequestBlock(piece_index, offset, block_length)
        try:
            self.socket.sendall(request_block.create_request())
            self.socket.settimeout(1)
            _, recieved_block_content = self.recieve_data()
        except Exception as exception:
            print("Failed to send block request (piece_index: %d - offset: %d - block_length: %d - %s)" % (piece_index, offset, block_length, exception.__str__()))
            return None
        return recieved_block_content[8:]
    
    def download_piece(self, piece: Piece):        
        piece.state = PieceState.PENDING

        piece_data = bytearray()
        print("Downloading piece %d" % piece.piece_index)

        max_retry = 5

        while not piece.is_completed():
            block = piece.get_unfinished_block()
            if not block:
                break
            block_data = self.download_block(block.piece_index, block.offset, block.length)
            if not block_data:
                if max_retry == 0:
                    print("Failed to download block")
                    self.healthy = False
                    piece.state = PieceState.UNFINISHED
                    return False
                
                print("Retry to download block")
                max_retry -= 1
                continue
            piece_data.extend(block_data)
            block.state = BlockState.FINISHED

        print("Downloading piece %d" % piece.piece_index + " done")


        sender = {
            "piece_index": piece.piece_index,
            "piece_data": piece_data
        }
        dispatcher.send(signal = "PiecesManager.Piece", sender = sender)
        return True

