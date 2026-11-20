from typing import Union

RLPItem = Union[bytes, list]

def rlp_encode(item: RLPItem) -> bytes:
    """递归编码： bytes 或 嵌套 list[bytes[list]]"""
    if isinstance(item, bytes):
        return _encode_bytes(item)
    if isinstance(item, list):
        payload = b"".join(rlp_encode(i) for i in item)
        return _length_prefix(payload, 0xc0)
    raise TypeError(f"RLP 只编码 bytes/list ，收到 {type(item)}")


def _encode_bytes(b: bytes) -> bytes:
    if len(b) == 1 and b[0] < 0x80:
        return b
    return _length_prefix(b, 0x80)

def _length_prefix(payload: bytes, offset: int) -> bytes:
    """ offset = 0x80 字节串 / 0xc0 列表"""
    if len(payload) <= 55:
        return bytes([offset + len(payload)]) + payload
    len_bytes = len(payload).to_bytes((len(payload).bit_length() + 7) // 8, "big")
    return bytes([offset + 55 + len(len_bytes)]) + len_bytes + payload