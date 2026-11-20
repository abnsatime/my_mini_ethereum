"""简化EVM栈机 + 15个核心 opcnode"""

MASK = ( 1 << 256) - 1 # 256-bit 掩码， 所有算术模 2^256

STOP, ADD, MUL, SUB = 0x00, 0x01, 0x02, 0x03
LT, GT, EQ           = 0x10, 0x11, 0x14
CALLDATALOAD         = 0x35
POP, MLOAD, MSTORE   = 0x50, 0x51, 0x52
SLOAD, SSTORE        = 0x54, 0x55
PUSH1                = 0x60
RETURN               = 0xf3

class EVMRevert(Exception):
    """交易失败 -> 状态回滚"""
    pass

class EVM:
    def __init__(self, code: bytes, calldata: bytes= b"", storage: dict | None = None):
        self.code = code
        self.calldata = calldata
        self.storage = storage if storage is not None else {}
        self.stack: list[int] = []   # evm中的栈， 用列表表示，先入后出
        self.memory = bytearray()   # evm 中的内存，自动拓展的bytes
        
        self.pc = 0  # 程序计数器
        self.gas = 1_000_000   # 简化，每条指令扣3 ， SSTORE 扣 20000

    # ----  栈的便捷方法 ----
    def pop(self) -> int:
        if not self.stack:
            raise EVMRevert("栈下溢")
        return self.stack.pop()
    
    def push(self, v: int) -> None:
        if len(self.stack) >= 1024:
            raise EVMRevert("栈下溢")
        self.stack.append(v & MASK)

    # ---- 内存读写： 不足自动补零扩展 ----

    def mem_read32(self, offset: int) -> int:
        need = offset + 32
        if len(self.memory) < need:
            self.memory.extend(b"\x00" * (need - len(self.memory)))
        return int.from_bytes(self.memory[offset:need], "big")

    def mem_write32(self, offset: int, value: int) -> None:
        need = offset + 32
        if len(self.memory) < need:
            self.memory.extend(b"\x00" * (need - len(self.memory)))
        self.memory[offset:need] = value.to_bytes(32, "big")

    
    def execute(self) -> bytes:
        while self.pc < len(self.code):
            op = self.code[self.pc]
            self.pc += 1
            self.gas -= 3
            if self.gas < 0:
                raise EVMRevert("out of gas")
            
            if op == STOP:
                return b""
            elif op == ADD:
                a, b = self.pop(), self.pop()
                self.push(a + b)          # push 里会 & MASK
            elif op == MUL:
                a, b = self.pop(), self.pop()
                self.push(a * b)
            elif op == SUB:
                b, a = self.pop(), self.pop()
                self.push(a - b)          # 负数 & MASK 就是模运算补码,正确!
            elif op == LT:
                b, a = self.pop(), self.pop()
                self.push(1 if a < b else 0)
            elif op == GT:
                b, a = self.pop(), self.pop()
                self.push(1 if a > b else 0)
            elif op == EQ:
                a, b = self.pop(), self.pop()
                self.push(1 if a == b else 0)
            elif op == POP:
                self.pop()
            elif op == MLOAD:
                offset = self.pop()
                self.push(self.mem_read32(offset))
            elif op == MSTORE:
                offset, value = self.pop(), self.pop()
                self.mem_write32(offset, value)
            elif op == SLOAD:
                slot = self.pop()
                self.push(self.storage.get(slot, 0))   # 未用槽位读出 0
            elif op == SSTORE:
                slot, value = self.pop(), self.pop()
                self.gas -= 20_000                     # 存储写入就是最贵
                self.storage[slot] = value
            elif op == CALLDATALOAD:
                offset = self.pop()
                chunk = self.calldata[offset:offset + 32]
                self.push(int.from_bytes(chunk.ljust(32, b"\x00"), "big"))  # 右补零
            elif op == PUSH1:
                if self.pc >= len(self.code):
                    raise EVMRevert("PUSH1 越界")
                self.push(self.code[self.pc])   # 只有它吃掉下一个字节
                self.pc += 1
            elif op == RETURN:
                offset, length = self.pop(), self.pop()
                need = offset + length
                if len(self.memory) < need:
                    self.memory.extend(b"\x00" * (need - len(self.memory)))
                return bytes(self.memory[offset:need])
            else:
                raise EVMRevert(f"未知 opcode 0x{op:02x}")

        return b"" 

