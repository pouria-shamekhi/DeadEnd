# Dead End

A maze game developed in **Python** and **PyQt5** as a university project. The project was implemented in two stages: a standalone maze generator and a complete GUI-based game.

## Features

* Random maze generation using the **Recursive Backtracking** algorithm
* User-configurable maze size (**5–30**)
* Maze representation using both a **2D matrix** and an **adjacency-list graph**
* Pathfinding algorithms: **BFS**, **DFS**, and **A***
* Intelligent hint system at intersections (**3 hints per game**)
* Keyboard controls with **Undo** support
* Win and lose conditions
* **Fog of War** mode
* Live timer and game statistics
* Game records stored in an **SQLite** database

## Project Structure

```text
maze_game/
├── main.py
├── build_exe.bat
├── requirements.txt
├── maze/
│   ├── generator.py
│   └── solver.py
├── game/
│   ├── player.py
│   └── database.py
└── ui/
    └── gui.py

tier1/  # Standalone terminal version of Stage 1
├── generator.py
├── solver.py
└── main.py
```

The `tier1` folder contains an independent implementation of the maze generator that runs entirely in the terminal without PyQt5 or game logic.

## Installation

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
python main.py
```

## Build Executable (Windows)

Simply run:

```cmd
build_exe.bat
```

## Controls

* **W/A/S/D** or **Arrow Keys** – Move
* **Z** – Undo
* **H** or **Space** – Request a hint
* **F** – Toggle Fog of War
* **Esc** – Return to the main menu
