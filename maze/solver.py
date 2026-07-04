from collections import deque
import heapq


def bfs(maze, start, goal):
    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        (r, c), path = queue.popleft()

        if (r, c) == goal:
            return path

        for nr, nc in maze.get_path_neighbors(r, c):
            if (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append(((nr, nc), path + [(nr, nc)]))

    return None


def dfs(maze, start, goal):
    stack = [(start, [start])]
    visited = {start}

    while stack:
        (r, c), path = stack.pop()

        if (r, c) == goal:
            return path

        for nr, nc in maze.get_path_neighbors(r, c):
            if (nr, nc) not in visited:
                visited.add((nr, nc))
                stack.append(((nr, nc), path + [(nr, nc)]))

    return None


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(maze, start, goal):
    heap = [(heuristic(start, goal), 0, start, [start])]
    best_g = {start: 0}

    while heap:
        f, g, (r, c), path = heapq.heappop(heap)

        if (r, c) == goal:
            return path

        if g > best_g.get((r, c), float('inf')):
            continue

        for nr, nc in maze.get_path_neighbors(r, c):
            ng = g + 1
            if ng < best_g.get((nr, nc), float('inf')):
                best_g[(nr, nc)] = ng
                nf = ng + heuristic((nr, nc), goal)
                heapq.heappush(heap, (nf, ng, (nr, nc), path + [(nr, nc)]))

    return None


class HintEngine:
    def __init__(self, maze):
        self.maze = maze
        self.goal = maze.exit
        self._dist_to_exit = self._bfs_distances(self.goal)

    def _bfs_distances(self, source):
        dist = {source: 0}
        queue = deque([source])
        while queue:
            r, c = queue.popleft()
            for nr, nc in self.maze.get_path_neighbors(r, c):
                if (nr, nc) not in dist:
                    dist[(nr, nc)] = dist[(r, c)] + 1
                    queue.append((nr, nc))
        return dist

    def get_hint(self, pos):
        r, c = pos
        neighbors = self.maze.get_path_neighbors(r, c)

        dir_name = {(-1, 0): 'بالا', (1, 0): 'پایین', (0, -1): 'چپ', (0, 1): 'راست'}
        analysis = {}

        for nr, nc in neighbors:
            dr, dc = nr - r, nc - c
            name = dir_name.get((dr, dc), '?')
            dist = self._dist_to_exit.get((nr, nc), 9999)
            dead = self._count_dead_ends_reachable(nr, nc, pos)
            analysis[name] = {'dist': dist, 'dead_ends': dead}

        if not analysis:
            return {'message': 'هیچ مسیری نیست!', 'analysis': {}}

        best = min(analysis, key=lambda k: analysis[k]['dist'])
        best_dist = analysis[best]['dist']
        current_dist = self._dist_to_exit.get(pos, 9999)

        lines = []
        for name, info in analysis.items():
            if info['dist'] == 9999:
                lines.append(f"{name}: بن‌بست")
            elif info['dead_ends'] > 0:
                lines.append(f"{name}: {info['dead_ends']} بن‌بست در پیش")
            else:
                lines.append(f"{name}: {info['dist']} گام تا خروجی")

        return {
            'best_direction': best,
            'steps_to_exit': best_dist,
            'current_dist': current_dist,
            'analysis': analysis,
            'lines': lines,
            'message': f"بهترین مسیر: {best} ({best_dist} گام تا خروجی)"
        }

    def _count_dead_ends_reachable(self, start_r, start_c, came_from, depth=6):
        dead_ends = 0
        visited = {came_from, (start_r, start_c)}
        stack = [(start_r, start_c, 0)]

        while stack:
            r, c, d = stack.pop()
            if d > depth:
                continue
            nbrs = [
                (nr, nc) for nr, nc in self.maze.get_path_neighbors(r, c)
                if (nr, nc) not in visited
            ]
            if not nbrs and d > 0:
                dead_ends += 1
            for nr, nc in nbrs:
                visited.add((nr, nc))
                stack.append((nr, nc, d + 1))

        return dead_ends

    def is_crossroad(self, pos):
        return len(self.maze.get_path_neighbors(*pos)) > 2

    def get_optimal_path(self):
        return astar(self.maze, self.maze.start, self.maze.exit) or []
