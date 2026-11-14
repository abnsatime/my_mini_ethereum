"""账户模型： 世界状态 = {地址 : {nonce, balance}}"""

import os
from my_eth.keccak_util import keccak256

class Account:
    def __init__(self, nonce:int = 0, balance: int = 0):
        self.nonce = nonce    # 已发出的交易计数
        self.balance = balance  # 单位 wei ， 1 ETH = 10^18 wei


def new_address() -> tuple[str, bytes]:
    """生成一个新地址（简化版： 私钥-> keccak -> 后20字节）   返回 （十六进制地址，伪私钥）"""
    fake_private_key = os.urandom(32)
    pubkey_hash = keccak256(fake_private_key)
    addr = "0x" + pubkey_hash[-20:].hex()
    return addr, fake_private_key