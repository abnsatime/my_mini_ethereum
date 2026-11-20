"""keccak256 + EIP-55 校验和地址"""

import os

from eth_utils import to_checksum_address as official

from my_eth.keccak_util import keccak256, to_checksum_address

SENTINEL = bytes.fromhex(
    "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"
)


def test_keccak_empty_sentinel():
    assert keccak256(b"") == SENTINEL


def test_keccak_known_vector():
    # 与 eth_utils 官方实现对赌(不再手打"公认值"——历史证明手打的会错)
    from eth_utils import keccak as official_keccak
    assert keccak256(b"abc") == official_keccak(b"abc")
    assert keccak256(b"abc").hex().startswith("4e03657a")  # 运行时产出的锚点


def test_eip55_matches_official():
    raw = "0xfb6916095ca1df60bb79ce92c3f02527d4bbf2b4"
    assert to_checksum_address(raw) == official(raw)


def test_eip55_random_addresses():
    for _ in range(5):
        raw = "0x" + os.urandom(20).hex()
        assert to_checksum_address(raw) == official(raw)
