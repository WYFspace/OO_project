import random
from lab01.board import Board
from lab01.game import Reversi as ReversiGame

class ReversiAI:
    def __init__(self, game):
        self.game = game

    def choose_move(self):
        valid_moves = self.game.get_valid_moves()
        if not valid_moves:
            return None, None
        return random.choice(valid_moves)


class ReversiClient:
    def __init__(self):
        self.game = ReversiGame()
        self.black_ai = ReversiAI(self.game)
        self.white_ai = ReversiAI(self.game)
        self.current_ai = None

    def start(self, player_type_black="human", player_type_white="ai"):
        print("欢迎来到黑白棋游戏！")
        self.display_prompt()
        while not self.game.is_over:
            self.game.display()
            if (self.game.current_player == Board.BLACK and player_type_black == "ai") or (
                self.game.current_player == Board.WHITE and player_type_white == "ai"):
                x, y = self.black_ai.choose_move() if self.game.current_player == Board.BLACK else self.white_ai.choose_move()
                if x is not None and y is not None:
                    print(f"AI在({x}, {y})落子。")
                    self.game.play_move(x, y)
                else:
                    print(f"{self.game._player_repr(self.game.current_player)}无合法棋步，被迫PASS。")
                    self.game.switch_player()
            else:
                move = input("请输入您的落子位置(x y)：").strip()
                if move.lower() == "exit":
                    print("退出游戏。")
                    break
                try:
                    x, y = map(int, move.split())
                    self.game.play_move(x, y)
                except Exception as e:
                    print(f"输入错误: {e}")

    def display_prompt(self):
        print("输入'x y'表示在(x, y)位置落子，输入'exit'退出游戏。")


if __name__ == '__main__':
    client = ReversiClient()
    client.start()
