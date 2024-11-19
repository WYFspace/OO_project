import sys
import pickle
import copy
from lab01.board import Board


class Game:
    def __init__(self, board_size):
        self.board = Board(board_size)
        self.current_player = Board.BLACK
        self.move_history = []
        self.is_over = False

    def restart(self):
        self.board = Board(self.board.size)
        self.current_player = Board.BLACK
        self.move_history.clear()
        self.is_over = False

    def switch_player(self):
        self.current_player = Board.WHITE if self.current_player == Board.BLACK else Board.BLACK

    def play_move(self, x, y):
        self.board.place_stone(x, y, self.current_player)
        self.move_history.append((x, y, self.current_player))
        if self.check_win(x, y):
            self.is_over = True
            print(f"玩家 {self._player_repr(self.current_player)} 胜利！")
        else:
            self.switch_player()

    def undo_move(self):
        if not self.move_history:
            raise ValueError("没有棋子可悔")
        x, y, _ = self.move_history.pop()
        self.board.remove_stone(x, y)
        self.switch_player()

    def save_game(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load_game(filename):
        with open(filename, 'rb') as f:
            game = pickle.load(f)
        return game

    def check_win(self, x, y):
        # 子类实现具体的胜负判定
        pass

    def _player_repr(self, player):
        return '黑棋' if player == Board.BLACK else '白棋'

    def display(self):
        print(f"当前玩家: {self._player_repr(self.current_player)}")
        self.board.display()

class GomokuGame(Game):
    def check_win(self, x, y):
        directions = [(1,0), (0,1), (1,1), (1,-1)]
        for dx, dy in directions:
            count = 1
            count += self._count_stones(x, y, dx, dy)
            count += self._count_stones(x, y, -dx, -dy)
            if count >= 5:
                return True
        return False

    def _count_stones(self, x, y, dx, dy):
        count = 0
        player = self.current_player
        nx, ny = x + dx, y + dy
        while 0 <= nx < self.board.size and 0 <= ny < self.board.size and self.board.grid[ny][nx] == player:
            count += 1
            nx += dx
            ny += dy
        return count

class GoGame(Game):
    def __init__(self, board_size):
        super().__init__(board_size)
        self.pass_count = 0
        self.previous_boards = []
        self.captured_stones = {Board.BLACK: 0, Board.WHITE: 0}

    def play_move(self, x, y):
        if x is None and y is None:
            self.pass_count += 1
            if self.pass_count >= 2:
                self.is_over = True
                self.calculate_score()
            else:
                self.switch_player()
            return

        if not (0 <= x < self.board.size and 0 <= y < self.board.size):
            raise ValueError("落子位置超出棋盘范围")
        if not self.board.is_empty(x, y):
            raise ValueError("该位置已有棋子")

        # 创建棋盘副本以检查合法性
        temp_board = copy.deepcopy(self.board)
        temp_board.place_stone(x, y, self.current_player)

        # 检查是否有提子
        opponent = Board.WHITE if self.current_player == Board.BLACK else Board.BLACK
        captured = self._remove_dead_stones(temp_board, x, y, opponent)

        # 检查自己的棋子是否有气
        if not self._has_liberty(temp_board, x, y, self.current_player):
            if not captured:
                raise ValueError("不能自杀")

        # 检查是否形成劫
        if self._is_ko(temp_board):
            raise ValueError("不能下出与之前棋盘相同的局面（劫）")

        # 更新真实棋盘和状态
        self.board = temp_board
        self.move_history.append((x, y, self.current_player))
        self.previous_boards.append(self._board_snapshot())
        self.pass_count = 0
        self.switch_player()

    def _has_liberty(self, board, x, y, color):
        visited = set()
        return self._search_liberty(board, x, y, color, visited)

    def _search_liberty(self, board, x, y, color, visited):
        if (x, y) in visited:
            return False
        visited.add((x, y))

        for nx, ny in board.get_neighbors(x, y):
            if board.is_empty(nx, ny):
                return True
            elif board.get_color(nx, ny) == color:
                if self._search_liberty(board, nx, ny, color, visited):
                    return True
        return False

    def _remove_dead_stones(self, board, x, y, color):
        dead_stones = []
        for nx, ny in board.get_neighbors(x, y):
            if board.get_color(nx, ny) == color:
                if not self._has_liberty(board, nx, ny, color):
                    group = []
                    self._collect_group(board, nx, ny, color, group)
                    dead_stones.extend(group)
        for sx, sy in dead_stones:
            board.remove_stone(sx, sy)
            self.captured_stones[self.current_player] += 1
        return dead_stones

    def _collect_group(self, board, x, y, color, group):
        if (x, y) in group:
            return
        group.append((x, y))
        for nx, ny in board.get_neighbors(x, y):
            if board.get_color(nx, ny) == color:
                self._collect_group(board, nx, ny, color, group)

    def _is_ko(self, new_board):
        snapshot = self._board_snapshot(board=new_board)
        return snapshot in self.previous_boards

    def _board_snapshot(self, board=None):
        if board is None:
            board = self.board
        return tuple(tuple(row) for row in board.grid)

    def calculate_score(self):
        print("双方连续两次PASS，游戏结束。开始计算得分。")
        black_score, white_score = self._count_territory()
        black_score += self.captured_stones[Board.BLACK]
        white_score += self.captured_stones[Board.WHITE]
        print(f"黑棋得分（包含提子）：{black_score}")
        print(f"白棋得分（包含提子）：{white_score}")
        if black_score > white_score:
            print("黑棋胜利！")
        elif white_score > black_score:
            print("白棋胜利！")
        else:
            print("平局！")
        self.is_over = True

    def _count_territory(self):
        visited = set()
        black_territory = 0
        white_territory = 0

        for x in range(self.board.size):
            for y in range(self.board.size):
                if (x, y) in visited or not self.board.is_empty(x, y):
                    continue
                territory, owner = self._explore_territory(x, y, visited)
                if owner == Board.BLACK:
                    black_territory += territory
                elif owner == Board.WHITE:
                    white_territory += territory
        return black_territory, white_territory

    def _explore_territory(self, x, y, visited):
        queue = [(x, y)]
        territory = 0
        owner = None
        borders = set()
        while queue:
            cx, cy = queue.pop()
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))
            territory += 1
            for nx, ny in self.board.get_neighbors(cx, cy):
                if self.board.is_empty(nx, ny):
                    queue.append((nx, ny))
                else:
                    borders.add(self.board.get_color(nx, ny))
        if len(borders) == 1:
            owner = borders.pop()
        return territory, owner

    def undo_move(self):
        if not self.move_history:
            raise ValueError("没有棋子可悔")
        self.move_history.pop()
        if self.previous_boards:
            self.previous_boards.pop()
        self.board = Board(self.board.size)
        self.captured_stones = {Board.BLACK: 0, Board.WHITE: 0}
        for move in self.move_history:
            x, y, color = move
            self.board.place_stone(x, y, color)
        self.switch_player()
        self.pass_count = 0

    def display(self):
        print(f"当前玩家: {self._player_repr(self.current_player)}")
        print(f"黑棋提子数：{self.captured_stones[Board.BLACK]}，白棋提子数：{self.captured_stones[Board.WHITE]}")
        self.board.display()
