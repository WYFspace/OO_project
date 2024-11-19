class Board:
    EMPTY = 0
    BLACK = 1
    WHITE = 2

    def __init__(self, size):
        if not (8 <= size <= 19):
            raise ValueError("棋盘大小必须在8到19之间")
        self.size = size
        self.grid = [[self.EMPTY for _ in range(size)] for _ in range(size)]

    def place_stone(self, x, y, color):
        if not (0 <= x < self.size and 0 <= y < self.size):
            raise ValueError("落子位置超出棋盘范围")
        if self.grid[y][x] != self.EMPTY:
            raise ValueError("该位置已有棋子")
        self.grid[y][x] = color

    def remove_stone(self, x, y):
        self.grid[y][x] = self.EMPTY

    def is_empty(self, x, y):
        return self.grid[y][x] == self.EMPTY

    def get_color(self, x, y):
        return self.grid[y][x]

    def get_neighbors(self, x, y):
        neighbors = []
        if x > 0:
            neighbors.append((x - 1, y))
        if x < self.size - 1:
            neighbors.append((x + 1, y))
        if y > 0:
            neighbors.append((x, y - 1))
        if y < self.size - 1:
            neighbors.append((x, y + 1))
        return neighbors

    def display(self):
        print("  " + " ".join([f"{i:2}" for i in range(self.size)]))
        for y in range(self.size):
            row = [self._stone_repr(self.grid[y][x]) for x in range(self.size)]
            print(f"{y:2} " + "  ".join(row))

    def _stone_repr(self, stone):
        if stone == self.EMPTY:
            return '·'
        elif stone == self.BLACK:
            return '○'
        elif stone == self.WHITE:
            return '●'