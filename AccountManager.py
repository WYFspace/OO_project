import json
import os

class AccountManager:
    def __init__(self, filename='accounts.json'):
        self.filename = filename
        self.accounts = self.load_accounts()

    def load_accounts(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}

    def save_accounts(self):
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.accounts, file, indent=4)

    def register(self, username, password):
        if username in self.accounts:
            raise ValueError("用户名已存在")
        self.accounts[username] = {'password': password, 'games': 0, 'wins': 0}
        self.save_accounts()

    def login(self, username, password):
        if username not in self.accounts:
            raise ValueError("用户名不存在")
        if self.accounts[username]['password'] != password:
            raise ValueError("密码错误")
        return self.accounts[username]

    def update_stats(self, username, win=True):
        if username not in self.accounts:
            raise ValueError("用户不存在")
        self.accounts[username]['games'] += 1
        if win:
            self.accounts[username]['wins'] += 1
        self.save_accounts()
