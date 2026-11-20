"""ABI 编解码 + ERC-20 calldata 上机执行"""

from my_eth.abi import SELECTOR_TRANSFER, decode_transfer, encode_transfer
from my_eth.evm import EVM


def test_selector_is_a9059cbb():
    assert SELECTOR_TRANSFER.hex() == "a9059cbb"


def test_encode_decode_roundtrip():
    bob = "0x" + "bb" * 20
    cd = encode_transfer(bob, 500)
    assert len(cd) == 68
    assert cd.hex().startswith("a9059cbb")
    to, amount = decode_transfer(cd)
    assert to == bob
    assert amount == 500


def test_address_left_padded():
    cd = encode_transfer("0x" + "01" + "bb" * 19, 1)
    assert cd[4:16] == b"\x00" * 12          # 左补 12 字节零
    assert cd[16:36].hex() == "01" + "bb" * 19


def test_erc20_executes_on_evm(erc20_code):
    cd = encode_transfer("0x" + "bb" * 20, 500)
    storage = {}
    ret = EVM(erc20_code, calldata=cd, storage=storage).execute()
    assert int.from_bytes(ret, "big") == 1
    slot = int.from_bytes(bytes.fromhex("bb" * 20), "big")
    assert storage[slot] == 500
