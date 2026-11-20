# my_mini_ethereum

一个用于学习以太坊底层原理的迷你以太坊实现，纯 Python 手写。不追求生产可用，只追求一件事：**让每个核心机制都能跑起来、被测试验证、被亲手写过一遍**。

## 总览：一笔 ERC-20 transfer 的完整链路

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 钱包侧(发起方)                                                           │
│                                                                         │
│  私钥 ──sign──> (r,s,v) 签名                    transaction.py          │
│  keccak256("transfer(address,uint256)")[:4]     abi.py                 │
│      = 0xa9059cbb (函数选择器)                                           │
│  calldata = selector + pad32(to) + pad32(amount)                        │
└──────────────────────────┬──────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 出块(矿工侧)                                     block.py + merkle.py   │
│                                                                         │
│  交易列表 ──每笔 tx_hash──> 叶子 ──> Merkle 根 ──> 进区块头              │
│  区块头 = number + parent_hash + timestamp + difficulty                 │
│         + nonce + transactions_root                                     │
│  PoW: 暴力试 nonce,直到 keccak256(区块头) 前缀为 "0"(难度 1)            │
└──────────────────────────┬──────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 执行(每个节点重放)                      executor.py + evm.py + state.py │
│                                                                         │
│  1. recover(签名) -> sender 地址(交易本身不存 from)                      │
│  2. 校验 nonce / 余额 —— 无效交易拒收,不进块                             │
│  3. nonce+1,预扣 gas —— 从此刻起交易"已上链",成败都消耗                   │
│  4. snapshot 世界状态快照                                               │
│  5. 转账(先于 EVM) + 若目标是合约: EVM 执行                              │
│       SSTORE/SLOAD 直接读写 WorldState 中该账户的 storage(引用共享)      │
│  6. 成功: 退还剩余 gas                                                  │
│     revert: rollback 快照(状态回滚,nonce/gas 不回滚)                    │
└──────────────────────────┬──────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 世界状态                                     state.py + account.py     │
│                                                                         │
│  { 地址: Account{ nonce, balance, code, storage{槽位: 值} } }           │
│  storage_root = merkle(sorted keccak(槽位||值))   (账户级哈希承诺)       │
└─────────────────────────────────────────────────────────────────────────┘
```

## 每一环：实现了什么，用什么方案演示

### 1. Keccak256 + EIP-55（`keccak_util.py`）

- **实现**：`eth-hash` + `pycryptodome` 后端。以太坊用的是 NIST 标准化前的原始 Keccak(padding 0x01),不是 `hashlib.sha3_256`——这是最常见的坑
- **方案**：以 `keccak256(b"") = c5d2...470` 为哨兵值验证；EIP-55 实现与 `eth_utils` 官方实现逐字符对赌(含随机地址抽查)

### 2. 区块 + PoW（`block.py`）

- **实现**：定长大端字节拼接区块头(简化版 RLP),暴力试 nonce 直到哈希前缀达标
- **方案**：难度固定 1(平均 16 次尝试),能直观看到 PoW 的随机性(方差巨大)

### 3. Merkle 承诺（`merkle.py`）

- **实现**：二进制 Merkle 树(Bitcoin 式),奇数叶子自我配对,空列表哈希空串
- **方案**：区块的 `transactions_root` 由每笔交易的 `tx_hash()`(内容+签名一起哈希)算出;演示"篡改任何一笔交易的任何 1 bit → 根变 → PoW 失效"

### 4. 账户模型（`account.py`）

- **实现**：nonce/balance/code/storage 四字段;`is_contract` 仅凭 code 是否为空判断(与真实以太坊一致);`storage_root` 对已用槽位排序后 Merkle 化
- **方案**：教学版 storage 用 `{槽位int: 值int}`,展示 Solidity 变量到存储槽位的映射思想

### 5. 世界状态（`state.py`）

- **实现**：`{地址: Account}` 字典;`snapshot` 刻意不含 nonce(revert 语义),`rollback` 就地恢复并清理执行中新建的"幽灵账户"
- **方案**：这是 EVM 原子性的实现基础——revert 后要么全成功要么无事发生

### 6. 签名交易（`transaction.py`）

- **实现**：`signing_bytes()` 定义被保护字段;secp256k1 原语用 `eth-keys`,签名/恢复流程手写
- **方案**：以太坊验签不是"验证签名有效",而是**从 (r,s,v) 恢复出地址**再比对——交易里不存 from,不存公钥。测试覆盖防篡改(改 value → 恢复失败)与冒签(只能花自己的钱)

### 7. EVM 栈机（`evm.py`）

- **实现**：15 个 opcode(ADD/SUB/MUL/LT/GT/EQ/POP/MLOAD/MSTORE/SLOAD/SSTORE/CALLDATALOAD/PUSH1/RETURN/STOP);256-bit 字;1024 栈深保护;内存自动扩展;简化 gas(每指令 3,SSTORE 20000)
- **方案**：测试直接手写机器码(如 `60 02 60 03 01 ...` = 2+3),练"读 bytecode"的肌肉记忆

### 8. ABI 编解码（`abi.py`）

- **实现**：`encode/decode_transfer`:4 字节选择器 + 地址左补 12 字节零 + uint256
- **方案**：选择器动态由 keccak 算出(a9059cbb),不硬编码

### 9. 交易执行器（`executor.py`）—— 合龙

- **实现**：签名恢复 → 三层校验 → nonce/gas 先行消耗 → 快照 → 转账 → EVM 以**引用共享**方式直接读写世界状态中合约账户的 storage → 成功退还 gas / 失败回滚
- **方案**：三层错误模型各有测试:无效交易拒收(不进块)、revert 回滚状态但 nonce/gas 照扣、成功交易不受后续 revert 影响

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install "eth-hash[pycryptodome]" eth-utils eth-keys

python mine_test.py       # PoW 挖矿 + Merkle 根
python tx_test.py         # 签名 / 恢复 / 防篡改
python evm_test.py        # EVM opcode 执行
python erc20_test.py      # ABI calldata → EVM → 存储
python executor_test.py   # 全链路集成:快照保护下的真实状态读写
```

## 刻意的简化(TODO 方向)

- [ ] RLP 编码(当前用定长字节拼接替代)
- [ ] 状态 Merkle 化:state_root 进区块头
- [ ] 手写 secp256k1(当前签名原语用 eth-keys)
- [ ] 真实 gas 价目表(EIP-150 / EIP-1559)
- [ ] P2P 节点网络(多进程互相同步区块)
- [ ] 交易池(mem pool)与区块组装
