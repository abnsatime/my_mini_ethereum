"""交易结构 + 签名 / 恢复"""

from eth_keys import keys
from eth_keys.exceptions import BadSignature
from my_eth.keccak_util import keccak256

class Transaction:
    def __init__(self, nonce: int, to: str, value :int, data: bytes = b"", gas_limit: int =21000):
        self.nonce = nonce
        self.to = to  # 0x.....
        self.value = value  #wei
        self.data = data   # 给合约的calldata
        self.gas_limit = gas_limit
        
    def signing_bytes(self) -> bytes:
        """参与签名的部分： 不可篡改内容"""
        to_bytes20 = bytes.fromhex(self.to[2:]) # 去掉 0x
        return (
            self.nonce.to_bytes(8, 'big')
            + to_bytes20
            + self.value.to_bytes(32, 'big')
            + self.data
            + self.gas_limit.to_bytes(8, 'big')
        )

    def sign(self, private_key_bytes: bytes) -> "SignedTransaction":
        """用私钥签名 -> 返回 SignedTransaction"""
        pk = keys.PrivateKey(private_key_bytes)
        sig = pk.sign_msg_hash(keccak256(self.signing_bytes()))
        return SignedTransaction(self, sig.r, sig.s, sig.v)

    def recover_from(self, r: int, s: int, v: int) -> str:
        """从签名恢复出发送者地址"""
        sig = keys.Signature(vrs=(v, r, s))
        pub = sig.recover_public_key_from_msg_hash(keccak256(self.signing_bytes()))
        return pub.to_checksum_address()


class SignedTransaction:
    def __init__(self, tx: Transaction, r: int, s: int, v: int):
        self.tx = tx
        self.r = r
        self.s = s
        self.v = v
        self.sender = tx.recover_from(r, s, v)

    def verify(self, claimed_sender: str) -> bool:
        return self.sender.lower() == claimed_sender.lower()


    def tx_hash(self) -> bytes:
        """交易哈希 = keccak256(签名前的 bytes + r + s + v)"""
        return keccak256(
            self.tx.signing_bytes()
            + self.r.to_bytes(32, 'big')
            + self.s.to_bytes(32, 'big')
            + self.v.to_bytes(1, 'big')
        )