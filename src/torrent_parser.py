import bencodepy
import binascii
import hashlib

class TorrentParser(object):
    def __init__(self, file_name: str):
        with open(file_name, 'rb') as f:
            read_data = f.read()
            self.torrent_info_dict = bencodepy.decode(read_data)
            
            self.announce = self.torrent_info_dict.get(b'announce')
            self.announce_list = self.torrent_info_dict.get(b'announce-list')
            self.piece_length = self.torrent_info_dict.get(b'info').get(b'piece length')
            self.torrent_length = self.torrent_info_dict.get(b'info').get(b'length')
            self.root_name = self.torrent_info_dict.get(b'info').get(b'name')
            
            torrent_info = self.torrent_info_dict.get(b'info')
            
            pieces = torrent_info.get(b'pieces')
            piece_hashes = [pieces[i:i+20] for i in range(0, len(pieces), 20)]
            self.piece_hashes_in_hex = [binascii.hexlify(piece).decode() for piece in piece_hashes]
            self.num_pieces = len(self.piece_hashes_in_hex)

            start_index = read_data.index(b'4:info') + 6
            end_index = start_index + len(bencodepy.encode(torrent_info))
            self.raw_info_dict = read_data[start_index:end_index]

            print("Announce: ", self.announce)
            print("Announce list: ", self.announce_list)
            print("Piece length: ", self.piece_length)
            print("Total length: ", self.torrent_length)
            print("Root name: ", self.root_name)

    @property
    def get_tracker_urls(self):
        if self.announce_list:
            return self.announce_list
        return [[self.announce]]


    @property
    def info_hash(self):
        return hashlib.sha1(self.raw_info_dict).digest()
    
class SingleFileTorrentParser(TorrentParser):
    def __init__(self, file_name: str):
        with open(file_name, 'rb') as f:
            read_data = f.read()
            self.torrent_info_dict = bencodepy.decode(read_data)
            
            self.announce = self.torrent_info_dict.get(b'announce')
            self.announce_list = self.torrent_info_dict.get(b'announce-list')
            self.piece_length = self.torrent_info_dict.get(b'info').get(b'piece length')
            self.torrent_length = self.torrent_info_dict.get(b'info').get(b'length')
            self.root_name = self.torrent_info_dict.get(b'info').get(b'name')
            
            torrent_info = self.torrent_info_dict.get(b'info')
            
            pieces = torrent_info.get(b'pieces')
            piece_hashes = [pieces[i:i+20] for i in range(0, len(pieces), 20)]
            self.piece_hashes_in_hex = [binascii.hexlify(piece).decode() for piece in piece_hashes]
            self.num_pieces = len(self.piece_hashes_in_hex)

            start_index = read_data.index(b'4:info') + 6
            end_index = start_index + len(bencodepy.encode(torrent_info))
            self.raw_info_dict = read_data[start_index:end_index]

            print("Announce: ", self.announce)
            print("Announce list: ", self.announce_list)
            print("Piece length: ", self.piece_length)
            print("Total length: ", self.torrent_length)
            print("Root name: ", self.root_name)

    @property
    def get_tracker_urls(self):
        if self.announce_list:
            return self.announce_list
        return [[self.announce]]
    
    @property
    def info_hash(self):
        return hashlib.sha1(self.raw_info_dict).digest()
    

class MultiFileTorrentParser(TorrentParser):
    def __init__(self, file_name: str):
        with open(file_name, 'rb') as f:
            read_data = f.read()
            self.torrent_info_dict = bencodepy.decode(read_data)
            
            self.announce = self.torrent_info_dict.get(b'announce')
            self.announce_list = self.torrent_info_dict.get(b'announce-list')
            self.piece_length = self.torrent_info_dict.get(b'info').get(b'piece length')
            self.torrent_length = self.torrent_info_dict.get(b'info').get(b'length')
            self.root_name = self.torrent_info_dict.get(b'info').get(b'name')
            
            torrent_info = self.torrent_info_dict.get(b'info')
            
            pieces = torrent_info.get(b'pieces')
            piece_hashes = [pieces[i:i+20] for i in range(0, len(pieces), 20)]
            self.piece_hashes_in_hex = [binascii.hexlify(piece).decode() for piece in piece_hashes]
            self.num_pieces = len(self.piece_hashes_in_hex)

            start_index = read_data.index(b'4:info') + 6
            end_index = start_index + len(bencodepy.encode(torrent_info))
            self.raw_info_dict = read_data[start_index:end_index]

            print("Announce: ", self.announce)
            print("Announce list: ", self.announce_list)
            print("Piece length: ", self.piece_length)
            print("Total length: ", self.torrent_length)
            print("Root name: ", self.root_name)

    @property
    def get_tracker_urls(self):
        if self.announce_list:
            return self.announce_list
        return [[self.announce]]
    
    @property
    def info_hash(self):
        return hashlib.sha1(self.raw_info_dict).digest()
    
class TorrentParserFactory(object):
    @staticmethod
    def create_torrent_parser(file_name: str):
        with open(file_name, 'rb') as f:
            read_data = f.read()
            torrent_info_dict = bencodepy.decode(read_data)
            if b'files' in torrent_info_dict[b'info']:
                return MultiFileTorrentParser(file_name)
            return SingleFileTorrentParser(file_name)