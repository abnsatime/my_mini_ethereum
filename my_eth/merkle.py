"""通过merkle树实现 区块根哈希，验证区块不可篡改合法性"""
from my_eth.keccak_util import keccak256

def merkle_root(leaves: list[bytes]) -> bytes:
    """叶子是每笔交易的哈希； 返回根。  空列表 直接返回 -> keccak256(b'')"""
    if not leaves:
        return keccak256(b'')  # 空 trie 则返回固定 transcation_root
    level = list(leaves)  # 防止污染原列表
    while len(level) > 1:
        if len(level) % 2 ==1:   # 如果是奇数个节点，需要让最后一个自我配对
            level.append(level[-1])
        level = [
            keccak256(level[i] + level[i+1])
            for i in range(0, len(level), 2)
        ]
    return level[0]
