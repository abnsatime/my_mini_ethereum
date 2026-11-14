
"""keccak256 工具：整个以太坊的密码学地基"""

from eth_hash.auto import keccak as _keccak


def keccak256(data: bytes) -> bytes:
    """对任意 bytes 做 keccak256，返回 32 字节"""
    return _keccak(data)

