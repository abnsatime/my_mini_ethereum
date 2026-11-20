# my_eth/legacy_tx.py
"""EIP-155 legacy 交易:与 cast mktx --legacy 逐字节兼容"""

from eth_keys import keys
from my_eth.keccak_util import keccak256
from my_eth.rlp import rlp_encode


def int_to_min_bytes(v: int) -> bytes:
    """整数 -> 最小字节大端。0 -> 空串(RLP 规则)"""
    if v == 0:
        return b""
    return v.to_bytes((v.bit_length() + 7) // 8, "big")


class LegacyTx:
    """[nonce, gasPrice, gasLimit, to, value, data] + EIP-155 签名"""

    def __init__(self, nonce, gas_price, gas_limit, to, value, data, chain_id):
        self.nonce, self.gas_price, self.gas_limit = nonce, gas_price, gas_limit
        self.to, self.value, self.data, self.chain_id = to, value, data, chain_id

    def signing_payload(self) -> bytes:
        """EIP-155 签名载荷:[...6字段..., chainId, 0, 0]"""
        return rlp_encode([
            int_to_min_bytes(self.nonce),
            int_to_min_bytes(self.gas_price),
            int_to_min_bytes(self.gas_limit),
            bytes.fromhex(self.to[2:]),
            int_to_min_bytes(self.value),
            self.data,
            int_to_min_bytes(self.chain_id),
            b"", b"",
        ])

    def sign(self, privkey: bytes) -> bytes:
        """签名并返回完整 RLP 交易字节"""
        pk = keys.PrivateKey(privkey)
        sig = pk.sign_msg_hash(keccak256(self.signing_payload()))
        chain = self.chain_id
        v = 35 + 2 * chain + (sig.v if sig.v in (0, 1) else sig.v - 27)  # 兼容两种 v 约定
        return rlp_encode([
            int_to_min_bytes(self.nonce),
            int_to_min_bytes(self.gas_price),
            int_to_min_bytes(self.gas_limit),
            bytes.fromhex(self.to[2:]),
            int_to_min_bytes(self.value),
            self.data,
            int_to_min_bytes(v),
            sig.r.to_bytes(32, "big"),
            sig.s.to_bytes(32, "big"),
        ])
        