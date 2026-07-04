import sys
from generator import MazeGenerator, WALL, PATH, START, EXIT
from solver import bfs, dfs, astar, HintEngine

CHARS = {
    WALL:  "██",
    PATH:  "  ",
    START: "▸ ",
    EXIT:  "★ ",
}


def print_maze(maze):
    for row in maze.matrix:
        line = "".join(CHARS.get(cell, "  ") for cell in row)
        print(line)


def main():
    size = 10
    if len(sys.argv) > 1:
        try:
            size = max(3, min(30, int(sys.argv[1])))
        except ValueError:
            pass

    maze = MazeGenerator(size)

    print(f"اندازه هزارتو: {size}")
    print(f"ابعاد ماتریس: {maze.rows} x {maze.cols}")
    print(f"نقطه شروع: {maze.start}")
    print(f"نقطه پایان: {maze.exit}")
    print()
    print_maze(maze)
    print()

    path_bfs = bfs(maze, maze.start, maze.exit)
    path_dfs = dfs(maze, maze.start, maze.exit)
    path_astar = astar(maze, maze.start, maze.exit)

    print(f"طول مسیر BFS:   {len(path_bfs) if path_bfs else 'یافت نشد'}")
    print(f"طول مسیر DFS:   {len(path_dfs) if path_dfs else 'یافت نشد'}")
    print(f"طول مسیر A*:    {len(path_astar) if path_astar else 'یافت نشد'}")
    print()

    engine = HintEngine(maze)
    hint = engine.get_hint(maze.start)
    print("راهنمای نقطه شروع:")
    for line in hint.get("lines", []):
        print(f"  - {line}")


if __name__ == "__main__":
    main()
