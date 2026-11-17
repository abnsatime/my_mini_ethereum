"""极简ABI： transfer(address, uint256) 的 calldata编码 + 解码"""

from my_eth.keccak_util import keccak256

SELECTOR_TRANSFER = keccak256(b"transfer(address,uint256)")[:4]

def encode_transfer(to: str, amount: int) -> bytes:
    """编码calldata： selector + pad32(to) + pad32(amount)"""
    addr20 = bytes.fromhex(to.lower().replace("0x", ""))
    return(
        SELECTOR_TRANSFER
        + (0).to_bytes(12, "big") + addr20   # 地址左补12 字节零 = 24 hex 0 
        + amount.to_bytes(32, "big")
    )

    
def decode_transfer(calldata: bytes) -> tuple[str, int]:
    """解码： 验证 selector , 拿到 to, amount 参数"""
    assert len(calldata) == 68, f"长度应为 68，实际{len(calldata)}"
    assert calldata[:4] == SELECTOR_TRANSFER, f"selector不符 {calldata[:4].hex()}"
    to = "0x" + calldata[4+12:4+32].hex()
    amount = int.from_bytes(calldata[36:68], "big")
    return to, amount