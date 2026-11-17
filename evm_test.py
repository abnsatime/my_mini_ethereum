from my_eth.evm import EVM, EVMRevert

# 测试 1:     2 + 3 = 5  (PUSH1 2, PUSH1 3, ADD, PUSH1 0, MSTORE, PUSH1 32, PUSH1 0, RETURN)
code = bytes([0x60, 2, 0x60, 3, 0x01, 0x60, 0, 0x52, 0x60, 32, 0x60, 0, 0xF3])
out = EVM(code).execute()
assert int.from_bytes(out, "big") == 5
print("ADD ✅ 2+3 =", int.from_bytes(out, "big"))

# 测试 2: 存储读写 (slot0 = 42, 再读出来返回)
code = bytes([0x60, 42, 0x60, 0, 0x55,      # SSTORE slot0=42
              0x60, 0, 0x54,                 # SLOAD slot0
              0x60, 0, 0x52,                 # MSTORE mem[0]=42
              0x60, 32, 0x60, 0, 0xF3])      # RETURN mem[0:32]
storage = {}
out = EVM(code, storage=storage).execute()
assert int.from_bytes(out, "big") == 42 and storage[0] == 42
print("SSTORE/SLOAD ✅ storage =", storage)

# 测试 3: CALLDATALOAD 读参数 (calldata 前 32 字节是 7)
code = bytes([0x60, 0, 0x35,               # CALLDATALOAD offset=0
              0x60, 0, 0x52, 0x60, 32, 0x60, 0, 0xF3])
out = EVM(code, calldata=(7).to_bytes(32, "big")).execute()
assert int.from_bytes(out, "big") == 7
print("CALLDATALOAD ✅ 读到参数 7")


# 测试 4: 栈下溢触发 Revert
try:
    EVM(bytes([0x01])).execute()   # 空栈做 ADD
    print("❌ 应该报错")
except EVMRevert as e:
    print("Revert 保护 ✅:", e)