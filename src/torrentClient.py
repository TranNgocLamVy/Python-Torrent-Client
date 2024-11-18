import hashlib
import bencodepy
import binascii
import requests
import struct
import math
import socket
from bcoding import bdecode

class MessageIDs:
    UNCHOKE = 1
    INTEREDSTED = 2
    BITFIELD = 5
    REQUEST = 6
    PIECE = 7

class TorrentClient:
    def __init__(self, filename):
        with open(filename, 'rb') as f:
            read_data = f.read()
            self.torrent_info_dict = bencodepy.decode(read_data)
            self.tracker_url = self.torrent_info_dict.get(b'announce')
            self.piece_length = self.torrent_info_dict.get(b'info').get(b'piece length')
            self.torrent_length = self.torrent_info_dict.get(b'info').get(b'length')
            
            torrent_info = self.torrent_info_dict.get(b'info')
            
            pieces = torrent_info.get(b'pieces')
            piece_hashes = [pieces[i:i+20] for i in range(0, len(pieces), 20)]
            self.piece_hashes_in_hex = [binascii.hexlify(piece).decode() for piece in piece_hashes]
            self.num_pieces = len(self.piece_hashes_in_hex)

            start_index = read_data.index(b'4:info') + 6
            end_index = start_index + len(bencodepy.encode(torrent_info))
            self.raw_info_dict = read_data[start_index:end_index]
        
    def get_peer_from_tracker(self):
        peer_id = '00112233445566778897' # random value of peer_id
        
        uploaded = 0
        downloaded = 0
        parsed_info_hash = hashlib.sha1(self.raw_info_dict).digest()
        
        params = {
            'info_hash': parsed_info_hash,
            'peer_id': peer_id,
            'port': 6881, # default port for torrent
            'uploaded': uploaded,
            'downloaded': downloaded,
            'left': self.torrent_length,
            'compact': 1
        }
        
        raw_resp = requests.get(url=self.tracker_url, params=params, timeout=10)
        raw_resp.raise_for_status()
        list_peers = bdecode(raw_resp.content)
        peers = []
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
        return peers
    
    def recieve_data(self, socket):
        length = b''
        while not length or not int.from_bytes(length, 'big'):
            length = socket.recv(4)
        
        length = int.from_bytes(length, 'big')
        data = socket.recv(length)
        while len(data) < length:
            data += socket.recv(length)
        message_id = int.from_bytes(data[:1], 'big')
        payload = data[1:]
        return message_id, payload
        
    def wait_for_peer_messag(self, socket, message_id):
        reciveved_id, data = self.recieve_data(socket)
        while message_id != reciveved_id:
            reciveved_id, data = self.recieve_data(socket)
        
        return data
    
    def wait_for_unchoke(self, socket):
        return self.wait_for_peer_messag(socket, MessageIDs.UNCHOKE)
    
    def wait_for_bitfield(self, socket):
        return self.wait_for_peer_messag(socket, MessageIDs.BITFIELD)
    
    def get_block(self, socket, index, begin, block_length):
        request_message = b'\x00\x00\x00\x0d\x06'
        request_message += index.to_bytes(4, byteorder='big')
        request_message += begin.to_bytes(4, byteorder='big')
        request_message += block_length.to_bytes(4, byteorder='big')
        socket.sendall(request_message)
        messageid, recieved_block_content = self.recieve_data(socket)
        return recieved_block_content[8:]
    
    def send_interested_message(self, socket):
        request_message = b'\x00\x00\x00\x01\x02'
        socket.sendall(request_message)
        
    def download_piece(self, peer_ip_and_port: str, piece_index: int, output_file: str):
        
        ip, port = peer_ip_and_port.split(':')
        block_length = 16*1024
        bit_protocol_req = bytearray()
        bit_protocol_req.extend([19])
        bit_protocol_req.extend('BitTorrent protocol'.encode())
        for _ in range(8):
            bit_protocol_req.extend([0])
        
        bit_protocol_req.extend(hashlib.sha1(self.raw_info_dict).digest())
        bit_protocol_req.extend('00112233445566778899'.encode())
        piece_data = bytearray()
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((ip, int(port)))
            sock.sendall(bit_protocol_req)
            sock.recv(68) # Handshake 
            
            self.wait_for_bitfield(sock)
            self.send_interested_message(sock)
            self.wait_for_unchoke(sock)
            
            if piece_index == self.num_pieces - 1:
                piece_length = ( self.torrent_length % self.piece_length ) or self.piece_length
            else:
                piece_length = self.piece_length
            
            number_of_blocks = math.ceil(piece_length / block_length)
            for block_index in range(number_of_blocks):
                if block_index == number_of_blocks - 1:  # This is the last block
                    offset = piece_length - min(block_length, piece_length - block_length * block_index)
                else:
                    offset = block_length * block_index
                bl = min(block_length, piece_length - offset)
                block_data = self.get_block(sock, piece_index, offset, bl)
                piece_data.extend(block_data)
            
            # Send have message
            have_message = b'\x00\x00\x00\x05\x04'
            have_message += piece_index.to_bytes(4, byteorder='big')
            sock.sendall(have_message)
        with open(output_file, 'wb') as f:
            f.write(piece_data)
        return piece_data
        
    def download_torrent_file(self, output_file: str):
        peer_ips = self.get_peer_from_tracker()
        peer_ip = peer_ips[0]
        torrent = bytearray()
        for piece_index in range(self.num_pieces):
            torrent.extend(self.download_piece(peer_ip, piece_index, output_file))
        with open(output_file, 'wb') as f:
            f.write(torrent)