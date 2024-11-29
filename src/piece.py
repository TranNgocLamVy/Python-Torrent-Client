from enum import Enum
from typing import List
from block import Block, BlockState, BLOCK_SIZE
import math
import hashlib

class PieceState(Enum):
    UNFINISHED = 0
    PENDING = 1
    FINISHED = 2

class Piece(object):
    def __init__(self, piece_index: int, piece_length: int, piece_hash: str):
        self.block_size = BLOCK_SIZE
        self.state = PieceState.UNFINISHED

        self.piece_index = piece_index
        self.piece_length = piece_length
        self.piece_hash = piece_hash
        
        self.num_blocks = math.ceil(piece_length / BLOCK_SIZE)
        self.completed_blocks = 0
        self.blocks: List[Block] = self.generate_blocks()

    def generate_blocks(self):
        blocks: List[Block] = []
        for block_index in range(self.num_blocks):
            offset = self.block_size * block_index
            if block_index == self.num_blocks - 1:  # This is the last block
                block_length = self.piece_length - self.block_size * (self.num_blocks - 1)
            else:
                block_length = self.block_size
            blocks.append(Block(self.piece_index, offset, block_length))
        return blocks
    
    def is_completed(self):
        return self.completed_blocks == self.num_blocks
    
    def update_block(self, block_index):
        block: Block = self.blocks[block_index]
        block.state = BlockState.FINISHED
        self.completed_blocks += 1
            
    def get_unfinished_block(self):
        for block in self.blocks:
            if block.state == BlockState.UNFINISHED:
                return block
        return None
    
    def check_piece_hash(self, piece_data: bytes):
        sha1 = hashlib.sha1()
        sha1.update(piece_data)
        calculated_hash = sha1.hexdigest()
        return calculated_hash == self.piece_hash
    
    def reset_piece(self):
        self.state = PieceState.UNFINISHED
        self.completed_blocks = 0
        for block in self.blocks:
            block.state = BlockState.UNFINISHED
        