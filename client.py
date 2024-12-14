from lab01.game import *

class Client:
    def __init__(self):
        self.game = None
        self.show_prompt = True

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
        print("8. prompt - 显示指令提示")
        print("9. exit - 退出游戏")

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
        elif cmd == 'prompt':
            self.set_prompt(args)
        elif cmd == 'exit':
            print("感谢游玩，再见！")
            sys.exit()
        else:
            print("未知指令")

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
        self.game.restart()
        print("游戏已重新开始")
        self.game.display()

    def set_prompt(self, args):
        self.show_prompt = True


if __name__ == '__main__':
    client = Client()
    client.start()