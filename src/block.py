from enum import Enum

BLOCK_SIZE = 16*1024

class BlockState(Enum):
    UNFINISHED = 0
    PENDING = 1
    FINISHED = 2

class Block():
    def __init__(self, piece_index: int, offset: int, length: int):
        self.block_size = BLOCK_SIZE
        self.state = BlockState.UNFINISHED

        self.piece_index = piece_index
        self.offset = offset
        self.length = length