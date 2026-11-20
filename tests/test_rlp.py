from my_eth.rlp import rlp_encode
from my_eth.legacy_tx import LegacyTx

GROUND_TRUTH = "0xf86b80843b9aca0082520894bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb865af3107a400080820a96a05a46c2115afd89ff8899440ca82598886949f24bc3ee435af68f2d622554388ca0700604a2f2e25cdafea380b685a45587a46b1dc1e369dcafad938ce39270f1bc"
PRIVKEY = b"\x00" * 31 + b"\x01"


def test_rlp_basics():
    assert rlp_encode(b"") == b"\x80"
    assert rlp_encode(b"\x00") == b"\x00"
    assert rlp_encode(b"\x7f") == b"\x7f"
    assert rlp_encode(b"\x80") == b"\x81\x80"
    assert rlp_encode(b"dog") == b"\x83dog"
    assert rlp_encode([b"cat", b"dog"]) == b"\xc8\x83cat\x83dog"
    # 长字节串(>55)
    long = b"\x01" * 60
    assert rlp_encode(long) == b"\xb8\x3c" + long
    # 长列表
    long_list = [b"\x01" * 60, b"\x02" * 60]
    payload = b"\xb8\x3c" + b"\x01" * 60 + b"\xb8\x3c" + b"\x02" * 60
    assert rlp_encode(long_list) == b"\xf8\x7c" + payload


def test_legacy_tx_matches_cast():
    tx = LegacyTx(nonce=0, gas_price=1_000_000_000, gas_limit=21000,
                  to="0xBBbbbbBBbbbBBBBbbBBbBbbbBBBbBBbbBbBbbBBb",
                  value=100000000000000, data=b"", chain_id=1337)
    raw = "0x" + tx.sign(PRIVKEY).hex()
    assert raw == GROUND_TRUTH