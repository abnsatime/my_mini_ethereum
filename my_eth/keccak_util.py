
"""keccak256 工具：整个以太坊的密码学地基"""

from eth_hash.auto import keccak as _keccak


def keccak256(data: bytes) -> bytes:
    """对任意 bytes 做 keccak256，返回 32 字节"""
    return _keccak(data)

def to_checksum_address(addr: str) -> str:
    """EIP-55 混合大小写校验地址"""
    addr = addr.lower().replace("0x", "")
    h = keccak256(addr.encode()).hex()      # 注意:对 ASCII 字符串哈希,不是字节!
    out = "0x"
    for ch, hh in zip(addr, h):
        out += ch.upper() if int(hh, 16) >= 8 else ch
    return out