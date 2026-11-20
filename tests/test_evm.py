"""EVM 栈机:15 个 opcode 与 revert 保护"""

import pytest

from my_eth.evm import EVM, EVMRevert


def test_add():
    # PUSH1 2, PUSH1 3, ADD, MSTORE mem[0], RETURN mem[0:32]
    code = bytes([0x60, 2, 0x60, 3, 0x01, 0x60, 0, 0x52, 0x60, 32, 0x60, 0, 0xF3])
    out = EVM(code).execute()
    assert int.from_bytes(out, "big") == 5


def test_sub_underflow_wraps():
    # 黄皮书 SUB: a b -> a-b, a 先入栈。栈序: PUSH1 0, PUSH1 1 -> 0-1
    code = bytes([0x60, 0, 0x60, 1, 0x03, 0x60, 0, 0x52, 0x60, 32, 0x60, 0, 0xF3])
    out = EVM(code).execute()
    assert int.from_bytes(out, "big") == (1 << 256) - 1


def test_sub_order_yellow_paper():
    # PUSH1 5, PUSH1 3 -> 5-3 = 2 (不是 3-5)
    code = bytes([0x60, 5, 0x60, 3, 0x03, 0x60, 0, 0x52, 0x60, 32, 0x60, 0, 0xF3])
    out = EVM(code).execute()
    assert int.from_bytes(out, "big") == 2


def test_comparisons():
    base = [0x60, 0, 0x52, 0x60, 32, 0x60, 0, 0xF3]  # MSTORE + RETURN
    # 黄皮书 LT: a b -> a<b, a 先入栈。PUSH1 2, PUSH1 3 -> 2<3 = 1
    out = EVM(bytes([0x60, 2, 0x60, 3, 0x10] + base)).execute()
    assert int.from_bytes(out, "big") == 1
    # GT: 2>3 = 0
    out = EVM(bytes([0x60, 2, 0x60, 3, 0x11] + base)).execute()
    assert int.from_bytes(out, "big") == 0
    # GT: 3>2 = 1 (栈序调换验证方向性)
    out = EVM(bytes([0x60, 3, 0x60, 2, 0x11] + base)).execute()
    assert int.from_bytes(out, "big") == 1
    # EQ: 3==3 -> 1
    out = EVM(bytes([0x60, 3, 0x60, 3, 0x14] + base)).execute()
    assert int.from_bytes(out, "big") == 1


def test_sstore_sload_roundtrip():
    code = bytes([
        0x60, 42, 0x60, 0, 0x55,       # SSTORE slot0 = 42
        0x60, 0, 0x54,                 # SLOAD slot0
        0x60, 0, 0x52, 0x60, 32, 0x60, 0, 0xF3,
    ])
    storage = {}
    out = EVM(code, storage=storage).execute()
    assert int.from_bytes(out, "big") == 42
    assert storage[0] == 42


def test_sload_missing_slot_is_zero():
    code = bytes([0x60, 5, 0x54, 0x60, 0, 0x52, 0x60, 32, 0x60, 0, 0xF3])
    out = EVM(code, storage={}).execute()
    assert int.from_bytes(out, "big") == 0


def test_calldataload_pads_right():
    code = bytes([0x60, 0, 0x35, 0x60, 0, 0x52, 0x60, 32, 0x60, 0, 0xF3])
    out = EVM(code, calldata=(7).to_bytes(32, "big")).execute()
    assert int.from_bytes(out, "big") == 7
    # calldata 只有 1 字节,右侧补零
    out = EVM(code, calldata=b"\xff").execute()
    assert int.from_bytes(out, "big") == 0xFF00 << 248 - 248 or True  # 0xff000...
    assert int.from_bytes(out, "big") == 0xFF << 248


def test_stack_underflow_reverts():
    with pytest.raises(EVMRevert):
        EVM(bytes([0x01])).execute()  # 空栈 ADD


def test_unknown_opcode_reverts():
    with pytest.raises(EVMRevert):
        EVM(bytes([0xFE])).execute()


def test_out_of_gas_reverts():
    # 循环加法直到 100 万 gas 烧完 (334 万条指令足够)
    code = bytes([0x60, 1, 0x60, 1, 0x01, 0x50] * 200_000)
    with pytest.raises(EVMRevert):
        EVM(code).execute()
