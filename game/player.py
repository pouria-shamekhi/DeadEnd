from dataclasses import dataclass


@dataclass
class GameStats:
    steps: int = 0
    undos: int = 0
    hints_used: int = 0
    hints_remaining: int = 3


class Player:
    MAX_HINTS = 3

    DIRECTIONS = {
        'w': (-1,  0),
        's': ( 1,  0),
        'a': ( 0, -1),
        'd': ( 0,  1),
    }

    def __init__(self, maze):
        self.maze = maze
        self.pos = maze.start
        self._history = []
        self._trail = set()
        self.stats = GameStats(hints_remaining=self.MAX_HINTS)
        self.reached_exit = False
        self.hit_dead_end = False

    def move(self, direction):
        if direction not in self.DIRECTIONS:
            return False

        dr, dc = self.DIRECTIONS[direction]
        r, c = self.pos
        nr, nc = r + dr, c + dc

        if not self.maze.is_walkable(nr, nc):
            return False

        self._history.append(self.pos)
        self._trail.add(self.pos)
        self.pos = (nr, nc)
        self.stats.steps += 1

        if self.pos == self.maze.exit:
            self.reached_exit = True
        elif self._is_dead_end():
            self.hit_dead_end = True

        return True

    def undo(self):
        if not self._history:
            return False

        self._trail.discard(self.pos)
        self.pos = self._history.pop()
        self.stats.undos += 1
        self.hit_dead_end = False
        return True

    def _is_dead_end(self):
        r, c = self.pos
        if self.pos == self.maze.exit:
            return False
        neighbors = self.maze.get_path_neighbors(r, c)
        return len(neighbors) == 1

    def use_hint(self):
        if self.stats.hints_remaining <= 0:
            return False
        self.stats.hints_remaining -= 1
        self.stats.hints_used += 1
        return True

    def is_at_crossroad(self):
        return len(self.maze.get_path_neighbors(*self.pos)) > 2

    def get_trail(self):
        return self._trail.copy()

    def can_move(self, direction):
        if direction not in self.DIRECTIONS:
            return False
        dr, dc = self.DIRECTIONS[direction]
        r, c = self.pos
        return self.maze.is_walkable(r + dr, c + dc)

    def available_directions(self):
        return [d for d in self.DIRECTIONS if self.can_move(d)]
