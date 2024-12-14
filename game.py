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
        self.replay_steps = []

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

    def replay_game(self):
        for x, y, player in self.move_history:
            self.board.place_stone(x, y, player)
            self.display()

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
        self.is_over = True
        if black_score > white_score:
            print("黑棋胜利！")
            return 1
        elif white_score > black_score:
            print("白棋胜利！")
            return 2
        else:
            print("平局！")
            return 3

    def check_winner(self):
        over = self.is_over
        res = self.calculate_score()
        self.is_over = over
        return res

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

class Reversi(Game):
    def __init__(self, board_size=8):
        if board_size != 8:
            print("黑白棋棋盘大小只能为8*8")
            board_size = 8
        super().__init__(board_size)
        self._initialize_board()

    def _initialize_board(self):
        mid = self.board.size // 2
        self.board.grid[mid - 1][mid - 1] = Board.WHITE
        self.board.grid[mid][mid] = Board.WHITE
        self.board.grid[mid - 1][mid] = Board.BLACK
        self.board.grid[mid][mid - 1] = Board.BLACK

    def play_move(self, x, y):
        if not self._is_valid_move(x, y, self.current_player):
            raise ValueError("无效的落子位置")

        self._place_and_flip(x, y, self.current_player)
        self.move_history.append((x, y, self.current_player))

        if not self._has_valid_moves(self._opponent_color(self.current_player)):
            if not self._has_valid_moves(self.current_player):
                self.is_over = True
                self._determine_winner()
            else:
                print(f"玩家 {self._player_repr(self.current_player)} 没有合法棋步，轮空！")
        else:
            self.switch_player()

    def _is_valid_move(self, x, y, color):
        if not (0 <= x < self.board.size and 0 <= y < self.board.size) or not self.board.is_empty(x, y):
            return False

        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            if self._can_capture_in_direction(x, y, dx, dy, color):
                return True
        return False

    def _can_capture_in_direction(self, x, y, dx, dy, color):
        x, y = x + dx, y + dy
        captured = False
        while 0 <= x < self.board.size and 0 <= y < self.board.size:
            if self.board.get_color(x, y) == self._opponent_color(color):
                captured = True
            elif self.board.get_color(x, y) == color:
                return captured
            else:
                break
            x, y = x + dx, y + dy
        return False

    def _place_and_flip(self, x, y, color):
        self.board.place_stone(x, y, color)
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            if self._can_capture_in_direction(x, y, dx, dy, color):
                self._flip_in_direction(x, y, dx, dy, color)

    def _flip_in_direction(self, x, y, dx, dy, color):
        x, y = x + dx, y + dy
        while 0 <= x < self.board.size and 0 <= y < self.board.size:
            if self.board.get_color(x, y) == self._opponent_color(color):
                self.board.grid[y][x] = color
            elif self.board.get_color(x, y) == color:
                break
            x, y = x + dx, y + dy

    def _opponent_color(self, color):
        return Board.BLACK if color == Board.WHITE else Board.WHITE

    def _has_valid_moves(self, color):
        for x in range(self.board.size):
            for y in range(self.board.size):
                if self._is_valid_move(x, y, color):
                    return True
        return False

    def _determine_winner(self):
        black_count = sum(row.count(Board.BLACK) for row in self.board.grid)
        white_count = sum(row.count(Board.WHITE) for row in self.board.grid)
        if black_count > white_count:
            print("黑棋胜利！")
        elif white_count > black_count:
            print("白棋胜利！")
        else:
            print("平局！")

    def undo_move(self):
        if not self.move_history:
            raise ValueError("没有棋子可悔")

        # 获取最近一步的棋局信息
        x, y, color = self.move_history.pop()

        # 撤回棋盘上的落子
        self.board.remove_stone(x, y)

        # 恢复被翻转的棋子
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            self._undo_flip_in_direction(x, y, dx, dy, color)

        # 切换回对方玩家
        self.switch_player()

    def _undo_flip_in_direction(self, x, y, dx, dy, color):
        # 先找出被翻转的棋子，然后恢复
        x, y = x + dx, y + dy
        while 0 <= x < self.board.size and 0 <= y < self.board.size:
            if self.board.get_color(x, y) == self._opponent_color(color):
                # 恢复为对方棋子
                self.board.grid[y][x] = self._opponent_color(color)
            elif self.board.get_color(x, y) == color:
                break
            x, y = x + dx, y + dy
