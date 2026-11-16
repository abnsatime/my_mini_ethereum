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
        """ 拍下当前世界状态的快照 (EVM 回滚失败调用)"""
        return {a: (acct.code, acct.balanace, dict(acct.storage)) for a, acct in self.accounts.items()}

    def rollback(self, snapshot: dict) -> None:
        """回滚到快照"""
        self.accounts = {
            a: Account(code=n, balance=b, storage=dict(s)) for a, (n, b, s) in snapshot.items()
            }