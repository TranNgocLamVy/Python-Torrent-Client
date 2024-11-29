class MessageIDs:
    CHOKE = 0
    UNCHOKE = 1
    INTEREDSTED = 2
    NOT_INTERESTED = 3
    HAVE = 4
    BITFIELD = 5
    REQUEST = 6
    PIECE = 7
    CANCEL = 8
    PORT = 9

class Message:
    def create_request(self):
        raise NotImplementedError()

    @classmethod
    def parse_response(cls, response: bytes):
        raise NotImplementedError()
    
class HandShake(Message):
    def __init__(self, info_hash: bytes, peer_id: bytes):
        self.info_hash = info_hash
        self.peer_id = peer_id
    
    def create_request(self):
        request = bytearray()
        request.extend([19])
        request.extend('BitTorrent protocol'.encode())
        for _ in range(8):
            request.extend([0])
        request.extend(self.info_hash)
        request.extend(self.peer_id)
        return request
    
class InterestedMessage(Message):
    def __ini__(self):
        pass

    def create_request(self):
        request = bytearray()
        request.extend(b'\x00\x00\x00\x01\x02')
        return request

class RequestBlock(Message):
    def __init__(self, index: int, offset: int, length: int):
        self.index = index
        self.offset = offset
        self.length = length
    
    def create_request(self):
        request = bytearray()
        request.extend(b'\x00\x00\x00\x0d\x06')
        request.extend(self.index.to_bytes(4, byteorder='big'))
        request.extend(self.offset.to_bytes(4, byteorder='big'))
        request.extend(self.length.to_bytes(4, byteorder='big'))
        return request
    
class HaveMessage(Message):
    def __init__(self, piece_index: int):
        self.piece_index = piece_index
    
    def create_request(self):
        request = bytearray()
        request.extend(b'\x00\x00\x00\x05\x04')
        request.extend(self.piece_index.to_bytes(4, byteorder='big'))
        return request
    
    