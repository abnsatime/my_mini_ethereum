# my_mini_ethereum

一个用于学习以太坊底层原理的迷你以太坊实现，纯 Python 手写。不追求生产可用，只追求一件事：**让每个核心机制都能跑起来、被测试验证、被亲手写过一遍**。

## 项目包含什么

| 模块 | 功能 | 对应真实以太坊的概念 |
|---|---|---|
| `my_eth/keccak_util.py` | keccak256 + EIP-55 校验和地址 | 密码学地基（注意：是 Keccak 不是 SHA3） |
| `my_eth/block.py` | 区块结构 + 工作量证明挖矿 | 链式哈希、PoW（难度 1） |
| `my_eth/merkle.py` | 二进制 Merkle 树 | transactions_root 对区块交易的承诺 |
| `my_eth/account.py` | 完整账户：nonce/balance/code/storage | EOA vs 合约账户、code_hash、storage_root |
| `my_eth/state.py` | 世界状态 {地址: 账户} + 快照回滚 | 全局状态、交易原子性（revert） |
| `my_eth/transaction.py` | 签名交易 + 公钥恢复 | secp256k1 签名、防篡改、防冒签 |
| `my_eth/evm.py` | 简化 EVM：栈机 + 15 个核心 opcode | ADD/SUB/MUL/LT/GT/EQ/POP/MLOAD/MSTORE/SLOAD/SSTORE/CALLDATALOAD/PUSH1/RETURN/STOP |
| `my_eth/abi.py` | ABI calldata 编码/解码 | 函数选择器、参数定宽编码 |

## 核心链路

一笔 ERC-20 `transfer` 在本项目中的完整生命周期：

```
私钥签名交易                          transaction.py
    ↓
ABI 编码 calldata (a9059cbb + 参数)    abi.py
    ↓
交易打包进区块, Merkle 根入块头         block.py + merkle.py
    ↓
PoW 挖矿 (难度 1)                      block.py
    ↓
EVM 栈机执行 bytecode                  evm.py
    ↓
世界状态被改写 (storage[to] = amount)  state.py + account.py
```

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install "eth-hash[pycryptodome]" eth-utils eth-keys

python mine_test.py       # PoW 挖矿 + Merkle 根
python tx_test.py         # 签名 / 恢复 / 防篡改
python evm_test.py        # EVM opcode 执行
python erc20_test.py      # ABI calldata → EVM → 状态 全链路
```

## 已验证的特性

- 空串 keccak 哨兵值与全网一致
- EIP-55 与 `eth_utils` 官方实现逐字符对赌通过（含随机地址抽查）
- 交易签名防篡改、冒签检测、nonce 防重放
- 篡改任何一笔交易 → transactions_root 改变 → PoW 失效
- EVM 栈下溢保护、gas 耗尽 revert、状态快照回滚
- `transfer(address,uint256)` 的 calldata 编码 → 解码 → 上机执行 → 存储断言全绿

## 刻意的简化（TODO 方向）

- [ ] RLP 编码（当前用定长字节拼接替代）
- [ ] 状态 Merkle 化：state_root 进区块头
- [ ] 手写 secp256k1（当前签名原语用 eth-keys）
- [ ] 真实 gas 价目表（EIP-150 / EIP-1559）
- [ ] P2P 节点网络（多进程互相同步区块）
