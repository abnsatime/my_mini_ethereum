"""世界状态：所有账户的当前余额和 nonce"""

from my_eth.account import Account

class WorldState:
    def __init__(self):
        self.accounts: dict[str, Account] = {}

    def get_or_create(self, addr: str) -> Account:
        if addr not in self.accounts:
            self.accounts[addr] = Account()
        return self.accounts[addr]

    def apply_transfer(self, sender: str, to: str, amount: int, tx_nonce: int) -> None:
        """执行一笔转账的核心状态转移"""
        sender_account = self.get_or_create(sender)
        if tx_nonce != sender_account.nonce:
            raise ValueError(f"nonce 不符: 交易={tx_nonce}, 账户={sender_account.nonce}")
        if sender_account.balance < amount:
            raise ValueError("余额不足")
        
        sender_account.balance -= amount
        sender_account.nonce += 1
        self.get_or_create(to).balance += amount


    def deploy_contract(self, addr: str, code: bytes) -> None:
        """在dadr处 创建也给合约账户（简化：部署地址由外部指定）"""
        acct = self.get_or_create(addr)
        acct.code = code

    def snapshot(self) -> dict:
        """ 快照:刻意不含 nonce(revert 不回滚 nonce —— 真实以太坊语义)"""
        return {a: (acct.code, acct.balance, dict(acct.storage)) for a, acct in self.accounts.items()}

    def rollback(self, snap: dict) -> None:
        """就地恢复 code/balance/storage;    但 nonce 保留当前值"""
        for addr in list(self.accounts):
            if addr not in snap:
                del self.accounts[addr]
        for addr, (code, balance, storage) in snap.items():
            acct = self.accounts[addr]
            acct.code = code
            acct.balance = balance
            acct.storage = dict(storage)