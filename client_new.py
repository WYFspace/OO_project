import random
import sys

from lab01.AccountManager import AccountManager
from lab01.game import *

class Client:
    def __init__(self):
        self.game = None
        self.show_prompt = True
        self.player_black = 0  # 0 for human, 1 for AI level 1, 2 for AI level 2
        self.player_white = 0  # 0 for human, 1 for AI level 1, 2 for AI level 2
        self.account_manager = AccountManager()
        self.user1 = None
        self.user2 = None

    def start(self):
        print("欢迎来到五子棋和围棋和黑白棋游戏！")
        while True:
            if self.show_prompt:
                self.display_prompt()
                self.show_prompt = False

            command = input("\n请输入指令：").strip()
            if not command:
                continue

            args = command.split()
            cmd = args[0].lower()

            try:
                self.handle_command(cmd, args)
            except Exception as e:
                print(f"发生错误：{e}")

    def _current_AI_player(self):
        return ((Board.BLACK == self.game.current_player and self.player_black > 0) or
                (Board.WHITE == self.game.current_player and self.player_white > 0))

    def display_prompt(self):
        print("\n可用指令：")
        print("1. start <game_type> <board_size> - 开始游戏，game_type为gomoku或go或reversi，board_size为8-19的整数")
        print("2. move <x> <y> - 在(x, y)位置落子")
        print("   pass - 不落子（仅围棋）")
        print("3. undo - 悔棋一步")
        print("4. resign - 投子认负")
        print("5. save <filename> - 保存当前局面")
        print("6. load <filename> - 读取局面")
        print("7. restart - 重新开始游戏")
        print("8. set <color> <level> - 设置玩家的颜色和难度，color为black或white，level为0-2")
        print("9. prompt - 显示指令提示")
        print("10. exit - 退出游戏")
        print("11. register - 注册")
        print("12. login <color> - 登录到指定颜色")
        print("13. replay <filename> - 回放指定文件")

    def handle_command(self, cmd, args):
        if cmd == 'start':
            self.start_game(args)
        elif cmd == 'move':
            self.move(args)
        elif cmd == 'pass':
            self.pass_turn()
        elif cmd == 'undo':
            self.undo()
        elif cmd == 'resign':
            self.resign()
        elif cmd == 'save':
            self.save(args)
        elif cmd == 'load':
            self.load(args)
        elif cmd == 'restart':
            self.restart()
        elif cmd == 'set':
            self.set_color_level(args)
        elif cmd == 'prompt':
            self.set_prompt(args)
        elif cmd == 'exit':
            print("感谢游玩，再见！")
            sys.exit()
        elif cmd == 'register':
            self.register()
        elif cmd == 'login':
            self.login(args)
        elif cmd == 'replay':
            self.replay(args)
        else:
            print("未知指令")
        while self.game and self._current_AI_player()  and not self.game.is_over:
            self.play_ai_turn()

    def start_game(self, args):
        if len(args) != 3:
            print("指令格式错误")
            return
        game_type = args[1]
        size = int(args[2])
        if not (8 <= size <= 19):
            print("棋盘大小必须在8到19之间")
            return
        if game_type == 'gomoku':
            self.game = GomokuGame(size)
        elif game_type == 'go':
            self.game = GoGame(size)
        elif game_type == 'reversi':
            self.game = Reversi(size)
        else:
            print("未知的游戏类型")
            return
        print(f"游戏开始！棋盘大小为{self.game.board.size}x{self.game.board.size}")
        self.game.display()

    def move(self, args):
        if not self.game or self.game.is_over:
            print("游戏未开始或已结束")
            return
        if len(args) == 3:
            x, y = int(args[1]), int(args[2])
            self.game.play_move(x, y)
            self.game.display()
        elif len(args) == 1 and isinstance(self.game, GoGame):
            self.game.play_move(None, None)
            print("玩家选择PASS")
            self.game.display()
        else:
            print("指令格式错误")
        if self.game.is_over:
            if isinstance(self.game, GoGame):
                if self.game.check_winner() == 1:
                    self.account_manager.update_stats(self.user1, True)
                    self.account_manager.update_stats(self.user1, False)
                elif self.game.check_winner() == 2:
                    self.account_manager.update_stats(self.user1, False)
                    self.account_manager.update_stats(self.user1, True)
            else:
                if self.game.current_player == Board.BLACK:
                    self.account_manager.update_stats(self.user1, True)
                    self.account_manager.update_stats(self.user1, False)
                else:
                    self.account_manager.update_stats(self.user1, False)
                    self.account_manager.update_stats(self.user1, True)

    def pass_turn(self):
        if not self.game or self.game.is_over:
            print("游戏未开始或已结束")
            return
        if isinstance(self.game, GoGame):
            self.game.play_move(None, None)
            print("玩家选择PASS")
            self.game.display()
        else:
            print("五子棋不支持PASS")

    def undo(self):
        if not self.game or self.game.is_over:
            print("游戏未开始或已结束")
            return
        self.game.undo_move()
        self.game.display()

    def resign(self):
        if not self.game or self.game.is_over:
            print("游戏未开始或已结束")
            return
        print(f"玩家 {self.game._player_repr(self.game.current_player)} 认负！")
        self.game.is_over = True

    def save(self, args):
        if len(args) != 2:
            print("指令格式错误")
            return
        filename = args[1]
        self.game.save_game(filename)
        print(f"游戏已保存至 {filename}")

    def load(self, args):
        if len(args) != 2:
            print("指令格式错误")
            return
        filename = args[1]
        self.game = Game.load_game(filename)
        print(f"已从 {filename} 加载游戏")
        self.game.display()

    def restart(self):
        if not self.game:
            print("游戏未开始")
            return
        self.player_white = 0
        self.player_black = 0
        self.game.restart()
        print("游戏已重新开始")
        self.game.display()

    def set_color_level(self, args):
        if not isinstance(self.game, Reversi):
            print("AI功能只支持黑白棋")
            return
        if len(args) != 3:
            print("指令格式错误")
            return
        color = args[1].lower()
        level = int(args[2])
        if level < 0 or level > 2:
            print("难度等级必须为 0、1 或 2")
            return
        if color == 'black':
            self.player_black = level
        elif color == 'white':
            self.player_white = level
        else:
            print("颜色必须为 black 或 white")
            return
        print(f"{color} 玩家已设置为等级 {level}")

    def play_ai_turn(self):
        if self.game.is_over:
            return

        # 只在对战模式下自动执行AI
        if self.game.current_player == Board.BLACK and self.player_black > 0:
            if self.player_black == 1:
                self.ai_move_level_1(Board.BLACK)
            elif self.player_black == 2:
                self.ai_move_level_2(Board.BLACK)
        elif self.game.current_player == Board.WHITE and self.player_white > 0:
            if self.player_white == 1:
                self.ai_move_level_1(Board.WHITE)
            elif self.player_white == 2:
                self.ai_move_level_2(Board.WHITE)

    def ai_move_level_1(self, color):
        # AI 随机选择合法位置
        valid_moves = self.get_valid_moves(color)
        if valid_moves:
            move = random.choice(valid_moves)
            # self.move(['move', move[0], move[1]])
            self.game.play_move(move[0], move[1])
            self.game.display()

    def ai_move_level_2(self, color):
        # AI 选择评分最高的位置
        best_move = None
        best_score = -float('inf')
        valid_moves = self.get_valid_moves(color)
        for move in valid_moves:
            score = self.evaluate_move(move[0], move[1], color)
            if score > best_score:
                best_score = score
                best_move = move
        if best_move:
            self.game.play_move(best_move[0], best_move[1])
            self.game.display()

    def evaluate_move(self, x, y, color):
        score = 0
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.game.board.size and 0 <= ny < self.game.board.size:
                if self.game.board.get_color(nx, ny) != color:
                    score += 1
        return score

    def get_valid_moves(self, color):
        valid_moves = []
        for x in range(self.game.board.size):
            for y in range(self.game.board.size):
                if self.game.board.is_empty(x, y) and self.game._is_valid_move(x, y, color):
                    valid_moves.append((x, y))
        return valid_moves

    def set_prompt(self, args):
        self.show_prompt = True

    def replay(self, args):
        curgame = self.game
        self.load(args[:1])
        print("replay game: [1: next step 2: prev step 3: exit]")
        history = self.game.move_history
        self.game.restart()
        i = 0
        max_step = len(history)
        while i < max_step:
            command = input("\n请输入指令：").strip()
            if len(command) != 1:
                print("invalid command")
                print("replay game: [1: next step 2: prev step 3: exit]")
            command = command[0].lower()
            if command == '1':
                self.move(history[i])
                i += 1
            elif command == '2':
                self.undo()
                if i > 0:
                    i -= 1
            elif command == '3':
                self.game = curgame
                return
            else:
                print("invalid command")
                print("replay game: [1: next step 2: prev step 3: exit]")

    def login(self, args):
        color = args[1].lower()
        if color != 'black' and color != 'white':
            print("invalid color")
            return
        username = input("请输入用户名: ").strip()
        password = input("请输入密码: ").strip()
        try:
            if color == 'black':
                self.user1 = self.account_manager.login(username, password)
            else:
                self.user2 = self.account_manager.login(username, password)
            print(f"欢迎回来，{username}！")
        except ValueError as e:
            print(e)
            return

    def register(self):
        username = input("请输入用户名: ").strip()
        password = input("请输入密码: ").strip()
        try:
            self.account_manager.register(username, password)
            print(f"注册成功，欢迎 {username}！")
        except ValueError as e:
            print(e)
            return


if __name__ == '__main__':
    client = Client()
    client.start()
