import random
from collections import defaultdict

WALL   = 1
PATH   = 0
START  = 2
EXIT   = 3
PLAYER = 4
TRAIL  = 5
HINT   = 6


class MazeGraph:
    def __init__(self):
        self.adj = defaultdict(list)

    def add_edge(self, u, v):
        self.adj[u].append(v)
        self.adj[v].append(u)

    def neighbors(self, node):
        return self.adj[node]


class MazeGenerator:
    def __init__(self, size):
        self.size = max(3, size)
        self.rows = 2 * self.size + 1
        self.cols = 2 * self.size + 1
        self.matrix = [[WALL] * self.cols for _ in range(self.rows)]
        self.graph = MazeGraph()
        self.start = (1, 0)
        self.exit = (self.rows - 2, self.cols - 1)

        self._generate()
        self._set_start_exit()

    def _generate(self):
        visited = [[False] * self.size for _ in range(self.size)]
        stack = []

        sr, sc = 0, 0
        visited[sr][sc] = True
        stack.append((sr, sc))

        while stack:
            r, c = stack[-1]
            mr, mc = 2 * r + 1, 2 * c + 1
            self.matrix[mr][mc] = PATH

            neighbors = self._unvisited_neighbors(r, c, visited)
            if neighbors:
                nr, nc = random.choice(neighbors)
                visited[nr][nc] = True

                wall_r = mr + (nr - r)
                wall_c = mc + (nc - c)
                self.matrix[wall_r][wall_c] = PATH

                self.graph.add_edge((mr, mc), (2 * nr + 1, 2 * nc + 1))

                stack.append((nr, nc))
            else:
                stack.pop()

    def _unvisited_neighbors(self, r, c, visited):
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        result = []
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.size and 0 <= nc < self.size and not visited[nr][nc]:
                result.append((nr, nc))
        return result

    def _set_start_exit(self):
        self.matrix[1][0] = PATH
        self.matrix[1][1] = PATH
        self.start = (1, 0)

        last_r = self.rows - 2
        last_c = self.cols - 1
        self.matrix[last_r][last_c] = PATH
        self.matrix[last_r][last_c - 1] = PATH
        self.exit = (last_r, last_c)

        self.matrix[self.start[0]][self.start[1]] = START
        self.matrix[self.exit[0]][self.exit[1]] = EXIT

    def is_walkable(self, r, c):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return self.matrix[r][c] != WALL
        return False

    def get_matrix_copy(self):
        return [row[:] for row in self.matrix]

    def get_path_neighbors(self, r, c):
        result = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if self.is_walkable(nr, nc):
                result.append((nr, nc))
        return result
