"""账户模型： 世界状态 = {地址 : {nonce, balance}}"""

import os
from my_eth.keccak_util import keccak256
from my_eth.merkle import merkle_root

class Account:
    def __init__(self, nonce:int = 0, balance: int = 0, code: bytes = b"", storage: dict | None = None):
        self.nonce = nonce    # 已发出的交易计数
        self.balance = balance  # 单位 wei ， 1 ETH = 10^18 wei
        self.code = code      # 合约字节码;  EOA账户为空
        self.storage = storage if storage is not None else {}  # 合约存储 槽位 int: 值int

    @property
    def is_contract(self) -> bool:
        """看code是否为空， 空则是普通账户，非空则是合约账户"""
        return len(self.code) > 0

    @property
    def code_hash(self) -> bytes:
        return keccak256(self.code)

    @property
    def storage_root(self) -> bytes:
        """所有已用槽位（排序保证确定性）   ->    merkle根"""
        leaves = [
            keccak256(slot.to_bytes(32, "big")) + value.to_bytes(32, 'big')
            for slot, value in sorted(self.storage.items())
        ]
        return merkle_root(leaves)

    
    def to_checksum(self, addr: str) -> str:
        """EIP-55 混合大小写校验地址"""
        addr = addr.lower().replace("0x", "")
        h = keccak256(addr.encode()).hex()

        out = "0x"
        for ch, hh in zip(addr, h):
            out += ch.upper() if int(hh, 16) >= 8 else ch
            # 对地址的小写 hex 做 keccak，哈希的第 i 个 hex 位如果 ≥ 8，地址第 i 个字符就大写。
        return out



def new_address() -> tuple[str, bytes]:
    """生成一个新地址（简化版： 私钥-> keccak -> 后20字节）   返回 （十六进制地址，伪私钥）"""
    fake_private_key = os.urandom(32)
    pubkey_hash = keccak256(fake_private_key)
    addr = "0x" + pubkey_hash[-20:].hex()
    return addr, fake_private_key