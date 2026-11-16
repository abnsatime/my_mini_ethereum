"""区块结构 + 工作量证明 Pow"""

from typing import Any
from my_eth.keccak_util import keccak256
from my_eth.merkle import merkle_root

class Block:
    def __init__(self, number:int, parent_hash: bytes,
                transactions: list, transactions_root: bytes = b'',  difficulty : int = 1):
        self.number = number
        self.parent_hash = parent_hash
        self.timestamp = 0   # 挖矿时填
        self.transactions = transactions
        self.transactions_root = transactions_root
        self.difficulty = difficulty
        self.nonce = 0       # 挖矿时暴力试
        self.hash = None   # 挖出后才有

    def header_bytes(self) -> bytes:
        """把决定哈希的字段拼成 bytes（简化版 RLP） 含 transactions_root 根哈希 """
        return(
            self.number.to_bytes(8, 'big')
            + self.parent_hash
            + self.timestamp.to_bytes(8, 'big')
            + self.difficulty.to_bytes(8, 'big')
            + self.nonce.to_bytes(8, 'big')
            + self.transactions_root
        )

    def mine(self) -> None:
        """工作量证明： 暴力试Nonce ，直到哈希前 difficulty 个十六进制位为0"""
        import time
        self.transactions_root = merkle_root(
            [keccak256(t.tx_hash()) for t in self.transactions]
        )
        self.timestamp = int(time.time())
        target = "0" * self.difficulty
        while True:
            h = keccak256(self.header_bytes()).hex()
            if h.startswith(target):
                self.hash = bytes.fromhex(h)
                break
            self.nonce += 1
            
