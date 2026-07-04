import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QScrollArea, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPalette, QLinearGradient

from maze.generator import MazeGenerator, WALL, PATH, START, EXIT, PLAYER, TRAIL
from maze.solver import HintEngine
from game.player import Player
from game.database import (
    init_db, get_or_create_player, save_record,
    get_records, get_best, get_all_players
)

init_db()

C = {
    "bg":          "#0a0a0f",
    "bg2":         "#13131c",
    "bg3":         "#191926",
    "bg4":         "#1f1f30",
    "border":      "#2e2e44",
    "border2":     "#21212f",
    "text":        "#9494c0",
    "text_dim":    "#56567a",
    "text_bright": "#e4e4f7",
    "accent":      "#5b7fd4",
    "accent2":     "#33437a",
    "accent_glow": "#7a9bf0",
    "green":       "#3ddc97",
    "green_dim":   "#1d4a37",
    "green_glow":  "#5eedb0",
    "orange":      "#f0a040",
    "orange_dim":  "#3a2a10",
    "red":         "#ef5876",
    "red_dim":     "#3a1622",
    "purple":      "#a47ee8",
    "wall":        "#1a1a28",
    "wall_top":    "#2c2c42",
    "path":        "#0d0d16",
    "trail":       "#0d2018",
    "player":      "#0c2a1f",
    "start_c":     "#0c1a36",
    "exit_c":      "#2a1c08",
    "fog":         "#050508",
}

FONT_FAMILY = "'Segoe UI', 'SF Pro Display', 'Vazirmatn', Arial, sans-serif"

BASE_STYLE = f"""
QWidget {{
    background-color: {C['bg']};
    color: {C['text']};
    font-family: {FONT_FAMILY};
}}
QLabel {{ background: transparent; color: {C['text']}; }}
QPushButton {{
    background-color: {C['bg3']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {C['bg4']};
    border-color: {C['accent']};
    color: {C['text_bright']};
}}
QPushButton:pressed {{ background-color: {C['accent2']}; }}
QLineEdit {{
    background-color: {C['bg2']};
    color: {C['text_bright']};
    border: 1.5px solid {C['border']};
    border-radius: 8px;
    padding: 9px 14px;
    font-size: 14px;
    selection-background-color: {C['accent2']};
}}
QLineEdit:focus {{ border-color: {C['accent']}; }}
QFrame {{ background: transparent; }}
QTableWidget {{
    background: {C['bg2']};
    border: 1px solid {C['border2']};
    border-radius: 8px;
    gridline-color: {C['border2']};
    color: {C['text']};
    font-size: 12px;
}}
QTableWidget::item {{
    padding: 6px;
}}
QTableWidget::item:selected {{
    background: {C['accent2']};
    color: {C['text_bright']};
}}
QHeaderView::section {{
    background: {C['bg3']};
    color: {C['text_dim']};
    border: none;
    border-bottom: 1.5px solid {C['border']};
    padding: 8px;
    font-size: 11px;
    font-weight: 600;
}}
QScrollBar:vertical {{
    background: {C['bg2']};
    width: 9px;
    border-radius: 4px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {C['border']};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{ background: {C['accent']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: {C['bg2']};
    height: 9px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {C['border']};
    border-radius: 4px;
    min-width: 24px;
}}
"""

FOG_RADIUS = 4


def make_label(text="", size=12, color=None, bold=False, align=Qt.AlignLeft, spacing=None):
    lbl = QLabel(text)
    f = QFont()
    f.setPointSize(size)
    f.setBold(bold)
    lbl.setFont(f)
    lbl.setAlignment(align)
    style = ""
    if color:
        style += f"color: {color}; "
    style += "background: transparent;"
    if spacing:
        style += f" letter-spacing: {spacing}px;"
    lbl.setStyleSheet(style)
    return lbl


def h_line(color=None):
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    c = color or C['border2']
    f.setStyleSheet(f"color: {c}; background: {c}; max-height: 1px;")
    f.setFixedHeight(1)
    return f


def btn_style(bg, border, color, hover, radius=10):
    return f"""
        QPushButton {{
            background:{bg}; border:1.5px solid {border};
            border-radius:{radius}px; color:{color};
            font-size:13px; font-weight:600; padding:11px;
        }}
        QPushButton:hover {{ background:{hover}; }}
        QPushButton:pressed {{ padding-top: 12px; padding-bottom: 10px; }}
    """


def card_style(bg=None, border=None, radius=14):
    bg = bg or C['bg2']
    border = border or C['border']
    return f"background:{bg}; border:1px solid {border}; border-radius:{radius}px;"


def soft_shadow(widget, blur=28, color="#000000", alpha=140, y=6):
    eff = QGraphicsDropShadowEffect(widget)
    eff.setBlurRadius(blur)
    qc = QColor(color)
    qc.setAlpha(alpha)
    eff.setColor(qc)
    eff.setOffset(0, y)
    widget.setGraphicsEffect(eff)


def fmt_time(secs):
    return f"{secs//60:02d}:{secs%60:02d}"


class MazeWidget(QWidget):
    CELL = 19

    def __init__(self, maze, player, parent=None):
        super().__init__(parent)
        self.maze = maze
        self.player = player
        self.fog_enabled = True
        self.setFixedSize(maze.cols * self.CELL, maze.rows * self.CELL)
        self.setFocusPolicy(Qt.NoFocus)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)
        matrix = self.maze.get_matrix_copy()
        trail = self.player.get_trail()
        pr, pc = self.player.pos

        for r, c in trail:
            if matrix[r][c] not in (START, EXIT):
                matrix[r][c] = TRAIL
        matrix[pr][pc] = PLAYER

        cell = self.CELL

        for r, row in enumerate(matrix):
            for c, val in enumerate(row):
                x, y = c * cell, r * cell

                if self.fog_enabled:
                    dist = abs(r - pr) + abs(c - pc)
                    if dist > FOG_RADIUS:
                        p.fillRect(x, y, cell, cell, QColor(C['fog']))
                        continue
                    if dist >= FOG_RADIUS - 1:
                        self._draw_cell(p, x, y, cell, val)
                        fade = QColor(C['fog'])
                        fade.setAlpha(120 if dist == FOG_RADIUS - 1 else 190)
                        p.fillRect(x, y, cell, cell, fade)
                        continue

                self._draw_cell(p, x, y, cell, val)

        p.setPen(QPen(QColor(C['border']), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRect(0, 0, self.width()-1, self.height()-1)
        p.end()

    def _draw_cell(self, p, x, y, cell, val):
        if val == WALL:
            grad = QLinearGradient(x, y, x, y + cell)
            grad.setColorAt(0, QColor(C['wall_top']))
            grad.setColorAt(1, QColor(C['wall']))
            p.fillRect(x, y, cell, cell, QBrush(grad))
        elif val == PATH:
            p.fillRect(x, y, cell, cell, QColor(C['path']))
        elif val == TRAIL:
            p.fillRect(x, y, cell, cell, QColor(C['trail']))
            p.setBrush(QBrush(QColor(C['green'])))
            p.setPen(Qt.NoPen)
            p.setOpacity(0.55)
            cx, cy = x + cell // 2, y + cell // 2
            p.drawEllipse(cx - 2, cy - 2, 4, 4)
            p.setOpacity(1.0)
        elif val == START:
            p.fillRect(x, y, cell, cell, QColor(C['start_c']))
            p.setPen(QPen(QColor(C['accent_glow']), 1))
            p.setFont(QFont("Arial", 9, QFont.Bold))
            p.drawText(x, y, cell, cell, Qt.AlignCenter, "▸")
        elif val == EXIT:
            glow = QColor(C['orange'])
            glow.setAlpha(45)
            p.fillRect(x - 2, y - 2, cell + 4, cell + 4, glow)
            p.fillRect(x, y, cell, cell, QColor(C['exit_c']))
            p.setPen(QPen(QColor(C['orange']), 1))
            p.setFont(QFont("Arial", 9, QFont.Bold))
            p.drawText(x, y, cell, cell, Qt.AlignCenter, "★")
        elif val == PLAYER:
            p.fillRect(x, y, cell, cell, QColor(C['player']))
            glow = QColor(C['green_glow'])
            glow.setAlpha(60)
            p.setBrush(QBrush(glow))
            p.setPen(Qt.NoPen)
            p.drawEllipse(x + 1, y + 1, cell - 2, cell - 2)
            p.setBrush(QBrush(QColor(C['green'])))
            p.setPen(QPen(QColor(C['green_glow']), 1))
            m = 5
            p.drawEllipse(x + m, y + m, cell - 2 * m, cell - 2 * m)

    def refresh(self):
        self.update()


class StatsPanel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(216)
        self.setStyleSheet(f"background:{C['bg2']}; border-left:1px solid {C['border2']};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 22, 18, 18)
        layout.setSpacing(4)

        layout.addWidget(make_label("گام‌ها", 9, C['text_dim'], bold=True, spacing=1))
        self.lbl_steps = make_label("000", 26, C['text_bright'], bold=True)
        layout.addWidget(self.lbl_steps)
        layout.addSpacing(10)

        layout.addWidget(make_label("زمان", 9, C['text_dim'], bold=True, spacing=1))
        self.lbl_time = make_label("00:00", 18, C['orange'], bold=True)
        layout.addWidget(self.lbl_time)
        layout.addSpacing(10)

        layout.addWidget(make_label("بازگشت", 9, C['text_dim'], bold=True, spacing=1))
        self.lbl_undos = make_label("0 بار", 14, C['text'])
        layout.addWidget(self.lbl_undos)

        layout.addSpacing(14)
        layout.addWidget(h_line())
        layout.addSpacing(14)

        layout.addWidget(make_label("راهنماهای باقی‌مانده", 9, C['text_dim'], bold=True, spacing=1))
        self.lbl_hints = make_label("◈  ◈  ◈", 15, C['green'])
        layout.addWidget(self.lbl_hints)
        layout.addSpacing(10)

        hint_frame = QFrame()
        hint_frame.setStyleSheet(
            f"QFrame {{ background:{C['green_dim']}; border:1px solid #225a44; border-radius:10px; }}"
        )
        hfl = QVBoxLayout(hint_frame)
        hfl.setContentsMargins(12, 11, 12, 11)
        hfl.setSpacing(5)
        hfl.addWidget(make_label("◈  راهنما", 9, "#5eedb0", bold=True, spacing=1))
        self.hint_text = QLabel("H را بفشار تا\nراهنما بگیری...")
        self.hint_text.setWordWrap(True)
        self.hint_text.setStyleSheet("color:#7af0c0; background:transparent; font-size:10px; line-height:1.5;")
        hfl.addWidget(self.hint_text)
        layout.addWidget(hint_frame)

        layout.addSpacing(14)
        self.fog_btn = QPushButton("🌫  مه جنگ: روشن")
        self.fog_btn.setFixedHeight(36)
        self.fog_btn.setStyleSheet(btn_style("#0e1c30", "#234a72", "#7fb4e8", "#15263e"))
        layout.addWidget(self.fog_btn)

        layout.addStretch()
        layout.addWidget(h_line())
        layout.addSpacing(12)

        self.btn_new = QPushButton("↺   بازی جدید")
        self.btn_new.setFixedHeight(40)
        self.btn_new.setStyleSheet(btn_style("#0d2018", C['green_dim'], C['green'], "#123628"))
        layout.addWidget(self.btn_new)
        layout.addSpacing(6)

        self.btn_records = QPushButton("📊   رکوردها")
        self.btn_records.setFixedHeight(40)
        self.btn_records.setStyleSheet(btn_style("#15152a", "#2e2e54", "#8d8df0", "#1d1d3a"))
        layout.addWidget(self.btn_records)
        layout.addSpacing(6)

        self.btn_quit = QPushButton("✕   خروج")
        self.btn_quit.setFixedHeight(40)
        self.btn_quit.setStyleSheet(btn_style(C['red_dim'], "#5a2030", C['red'], "#451c28"))
        layout.addWidget(self.btn_quit)

    def update_stats(self, stats, elapsed=0):
        self.lbl_steps.setText(str(stats.steps).zfill(3))
        self.lbl_undos.setText(f"{stats.undos} بار")
        self.lbl_time.setText(fmt_time(elapsed))
        r = stats.hints_remaining
        self.lbl_hints.setText("◈  " * r + "·  " * (3 - r))

    def set_hint(self, text):
        self.hint_text.setText(text)

    def set_fog_label(self, on):
        self.fog_btn.setText("🌫  مه جنگ: روشن" if on else "👁  مه جنگ: خاموش")


class StatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(38)
        self.setStyleSheet(f"background:{C['bg2']}; border-top:1px solid {C['border2']};")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 18, 0)
        self.msg = make_label("▸ در هزارتو قدم بزن...", 10, C['text_dim'])
        layout.addWidget(self.msg)
        layout.addStretch()
        layout.addWidget(make_label("W/A/S/D حرکت  ·  Z برگشت  ·  H راهنما  ·  F مه", 9, C['text_dim']))

    def set_message(self, text, color=None):
        self.msg.setText(text)
        c = color or C['text_dim']
        self.msg.setStyleSheet(f"color:{c}; background:transparent;")


class EndOverlay(QWidget):
    restart_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, won, stats, elapsed, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:rgba(8,8,14,225);")

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)

        box = QWidget()
        box.setFixedWidth(380)
        box.setStyleSheet(card_style(C['bg2'], C['border'], 18))
        soft_shadow(box, blur=40, alpha=180, y=10)
        layout = QVBoxLayout(box)
        layout.setSpacing(11)
        layout.setContentsMargins(40, 40, 40, 38)

        if won:
            layout.addWidget(make_label("★", 50, C['orange'], bold=True, align=Qt.AlignCenter))
            layout.addWidget(make_label("تبریک!", 24, C['green'], bold=True, align=Qt.AlignCenter, spacing=1))
            layout.addWidget(make_label("Congratulations", 11, C['text_dim'], align=Qt.AlignCenter))
        else:
            layout.addWidget(make_label("✗", 50, C['red'], bold=True, align=Qt.AlignCenter))
            layout.addWidget(make_label("Game Over", 24, C['red'], bold=True, align=Qt.AlignCenter, spacing=1))
            layout.addWidget(make_label("به بن‌بست رسیدی", 11, C['text_dim'], align=Qt.AlignCenter))

        layout.addSpacing(6)
        layout.addWidget(h_line())
        layout.addSpacing(6)

        for label, value in [
            ("گام‌ها", str(stats.steps)),
            ("زمان", fmt_time(elapsed)),
            ("بازگشت", f"{stats.undos} بار"),
            ("راهنما", f"{stats.hints_used} بار"),
        ]:
            row = QHBoxLayout()
            row.addWidget(make_label(label, 11, C['text_dim']))
            row.addStretch()
            row.addWidget(make_label(value, 12, C['text_bright'], bold=True))
            layout.addLayout(row)

        layout.addSpacing(6)
        layout.addWidget(h_line())
        layout.addSpacing(8)

        b_r = QPushButton("↺   بازی مجدد")
        b_r.setFixedHeight(44)
        b_r.setStyleSheet(btn_style("#0d2018", C['green_dim'], C['green'], "#123628"))
        b_r.clicked.connect(self.restart_requested.emit)
        layout.addWidget(b_r)

        b_q = QPushButton("✕   خروج")
        b_q.setFixedHeight(44)
        b_q.setStyleSheet(btn_style(C['red_dim'], "#5a2030", C['red'], "#451c28"))
        b_q.clicked.connect(self.quit_requested.emit)
        layout.addWidget(b_q)

        outer.addWidget(box, alignment=Qt.AlignCenter)


class RecordsPage(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{C['bg']};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 26, 32, 26)
        layout.setSpacing(14)

        hdr = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.addWidget(make_label("رکوردهای بازی", 18, C['text_bright'], bold=True, spacing=1))
        title_box.addWidget(make_label("تاریخچه‌ی کامل بازی‌های ثبت‌شده", 10, C['text_dim']))
        hdr.addLayout(title_box)
        hdr.addStretch()
        btn_back = QPushButton("←   بازگشت")
        btn_back.setFixedSize(120, 38)
        btn_back.setStyleSheet(btn_style(C['bg3'], C['border'], C['text'], C['bg4']))
        btn_back.clicked.connect(self.back_requested.emit)
        hdr.addWidget(btn_back)
        layout.addLayout(hdr)
        layout.addWidget(h_line())

        frow_card = QWidget()
        frow_card.setStyleSheet(card_style(C['bg2'], C['border2'], 12))
        frow = QHBoxLayout(frow_card)
        frow.setContentsMargins(16, 12, 16, 12)
        frow.addWidget(make_label("نام کاربر", 11, C['text_dim'], bold=True))
        self.name_filter = QLineEdit()
        self.name_filter.setPlaceholderText("نام خود را وارد کن...")
        self.name_filter.setFixedWidth(220)
        self.name_filter.returnPressed.connect(self.load)
        frow.addWidget(self.name_filter)
        btn_load = QPushButton("نمایش")
        btn_load.setFixedSize(90, 36)
        btn_load.setStyleSheet(btn_style(C['accent2'], C['accent'], "#a8c4f5", "#3d4f93"))
        btn_load.clicked.connect(self.load)
        frow.addWidget(btn_load)
        frow.addStretch()
        layout.addWidget(frow_card)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "تاریخ", "اندازه", "گام‌ها", "زمان", "بازگشت", "راهنما", "نتیجه"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(
            self.table.styleSheet() + f"alternate-background-color: {C['bg3']};"
        )
        layout.addWidget(self.table)

        self.info_label = make_label("", 10, C['text_dim'])
        layout.addWidget(self.info_label)

    def load(self):
        name = self.name_filter.text().strip()
        if not name:
            self.info_label.setText("نام کاربر را وارد کن.")
            return

        player_id = get_or_create_player(name)
        records = get_records(player_id)

        self.table.setRowCount(0)
        for rec in records:
            row = self.table.rowCount()
            self.table.insertRow(row)
            won = rec['won'] == 1
            cells = [
                rec['played_at'],
                str(rec['maze_size']),
                str(rec['steps']),
                fmt_time(rec['duration']),
                str(rec['undos']),
                str(rec['hints_used']),
                "✓ برد" if won else "✗ باخت",
            ]
            for col, val in enumerate(cells):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                if col == 6:
                    item.setForeground(QColor(C['green'] if won else C['red']))
                self.table.setItem(row, col, item)

        total = len(records)
        wins = sum(1 for r in records if r['won'])
        self.info_label.setText(
            f"مجموع بازی‌ها: {total}   ·   برد: {wins}   ·   باخت: {total - wins}"
        )


class StartPage(QWidget):
    start_requested = pyqtSignal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{C['bg']};")
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)

        box = QWidget()
        box.setFixedWidth(440)
        box.setStyleSheet(card_style(C['bg2'], C['border'], 20))
        soft_shadow(box, blur=44, alpha=160, y=10)
        layout = QVBoxLayout(box)
        layout.setSpacing(6)
        layout.setContentsMargins(44, 42, 44, 42)

        icon = make_label("⬡", 38, C['accent_glow'], bold=True, align=Qt.AlignCenter)
        layout.addWidget(icon)
        title = make_label("DEAD END", 28, C['text_bright'], bold=True, align=Qt.AlignCenter, spacing=4)
        layout.addWidget(title)
        layout.addSpacing(2)
        layout.addWidget(make_label("راهی برای فرار از این هزارتو پیدا کن", 11, C['text_dim'], align=Qt.AlignCenter))

        layout.addSpacing(20)
        layout.addWidget(h_line())
        layout.addSpacing(20)

        layout.addWidget(make_label("نام کاربری", 11, C['text_dim'], bold=True))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("مثلاً: Ali")
        self.name_input.setFixedHeight(40)
        layout.addWidget(self.name_input)
        layout.addSpacing(14)

        layout.addWidget(make_label("اندازه هزارتو  (۵ تا ۳۰)", 11, C['text_dim'], bold=True))
        self.size_input = QLineEdit("12")
        self.size_input.setPlaceholderText("مثلاً: 12")
        self.size_input.setFixedHeight(40)
        self.size_input.returnPressed.connect(self._start)
        layout.addWidget(self.size_input)

        layout.addSpacing(22)

        btn = QPushButton("▸   شروع بازی")
        btn.setFixedHeight(48)
        btn.setStyleSheet(btn_style(C['accent2'], C['accent'], "#bcd2f8", "#3d4f93", radius=12))
        btn.clicked.connect(self._start)
        layout.addWidget(btn)

        layout.addSpacing(18)
        layout.addWidget(make_label(
            "W/A/S/D حرکت  ·  Z برگشت  ·  H راهنما  ·  F مه",
            9, C['text_dim'], align=Qt.AlignCenter
        ))

        outer.addWidget(box, alignment=Qt.AlignCenter)

    def _start(self):
        try:
            size = max(5, min(30, int(self.size_input.text())))
        except ValueError:
            size = 12
        name = self.name_input.text().strip() or "ناشناس"
        self.start_requested.emit(size, name)


class GamePage(QWidget):
    back_to_menu = pyqtSignal()

    def __init__(self, maze, player, hint_engine, maze_size, player_name, parent=None):
        super().__init__(parent)
        self.maze = maze
        self.player = player
        self.hint_engine = hint_engine
        self.maze_size = maze_size
        self.player_name = player_name
        self._overlay = None
        self._elapsed = 0

        self._build()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

        self.setFocusPolicy(Qt.StrongFocus)

    def _build(self):
        main = QVBoxLayout(self)
        main.setSpacing(0)
        main.setContentsMargins(0, 0, 0, 0)

        header = QWidget()
        header.setFixedHeight(48)
        header.setStyleSheet(f"background:{C['bg3']}; border-bottom:1px solid {C['border2']};")
        hbox = QHBoxLayout(header)
        hbox.setContentsMargins(20, 0, 20, 0)
        title = make_label("⬡", 14, C['accent_glow'], bold=True)
        hbox.addWidget(title)
        hbox.addWidget(make_label(
            f"DEAD END   ·   اندازه {self.maze_size}   ·   {self.player_name}",
            11, C['text'], bold=True, spacing=1
        ))
        hbox.addStretch()
        self.header_pos = make_label("", 10, C['text_dim'])
        hbox.addWidget(self.header_pos)
        main.addWidget(header)

        content = QHBoxLayout()
        content.setSpacing(0)
        content.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setStyleSheet(f"background:{C['bg']}; border:none;")
        scroll.setWidgetResizable(False)
        scroll.setAlignment(Qt.AlignCenter)
        self.maze_widget = MazeWidget(self.maze, self.player)
        scroll.setWidget(self.maze_widget)
        content.addWidget(scroll, stretch=1)

        self.stats = StatsPanel()
        self.stats.btn_new.clicked.connect(self._go_menu)
        self.stats.btn_quit.clicked.connect(QApplication.quit)
        self.stats.btn_records.clicked.connect(self._go_records)
        self.stats.fog_btn.clicked.connect(self._toggle_fog)
        content.addWidget(self.stats)

        main.addLayout(content, stretch=1)

        self.status_bar = StatusBar()
        main.addWidget(self.status_bar)

    def _tick(self):
        self._elapsed += 1
        self.stats.update_stats(self.player.stats, self._elapsed)

    def keyPressEvent(self, event):
        move_map = {
            Qt.Key_W: 'w', Qt.Key_Up: 'w',
            Qt.Key_S: 's', Qt.Key_Down: 's',
            Qt.Key_A: 'a', Qt.Key_Left: 'a',
            Qt.Key_D: 'd', Qt.Key_Right: 'd',
        }
        k = event.key()
        if k in move_map:
            self._do_move(move_map[k])
        elif k == Qt.Key_Z:
            self._do_undo()
        elif k in (Qt.Key_H, Qt.Key_Space):
            self._do_hint()
        elif k == Qt.Key_F:
            self._toggle_fog()
        elif k == Qt.Key_Escape:
            self._go_menu()
        else:
            super().keyPressEvent(event)

    def _do_move(self, d):
        if self.player.move(d):
            self._refresh()
            if self.player.reached_exit:
                self._end_game(True)
            elif self.player.hit_dead_end:
                self.status_bar.set_message("✗  بن‌بست! Z بزن تا برگردی.", C['red'])
        else:
            self.status_bar.set_message("█  دیوار!", C['text_dim'])

    def _do_undo(self):
        if self.player.undo():
            self._refresh()
            self.status_bar.set_message("↩  یک قدم به عقب برگشتی.", C['text'])
        else:
            self.status_bar.set_message("تاریخچه‌ای نیست.")

    def _do_hint(self):
        if not self.player.use_hint():
            self.status_bar.set_message("◈  راهنماها تموم شدن!", C['red'])
            return
        hint = self.hint_engine.get_hint(self.player.pos)
        lines = hint.get('lines', [])
        self.stats.set_hint("\n".join(lines[:4]) if lines else hint.get('message', '...'))
        self.stats.update_stats(self.player.stats, self._elapsed)
        self.status_bar.set_message(f"◈  {hint.get('best_direction', '?')} بهترین مسیر", C['green'])

    def _toggle_fog(self):
        self.maze_widget.fog_enabled = not self.maze_widget.fog_enabled
        self.stats.set_fog_label(self.maze_widget.fog_enabled)
        self.maze_widget.refresh()

    def _refresh(self):
        self.maze_widget.refresh()
        self.stats.update_stats(self.player.stats, self._elapsed)
        r, c = self.player.pos
        self.header_pos.setText(f"({r},{c})")
        dirs = self.player.available_directions()
        fa = {'w': 'بالا', 's': 'پایین', 'a': 'چپ', 'd': 'راست'}
        self.status_bar.set_message("▸  " + "   ".join(fa[d] for d in dirs) if dirs else "▸  بن‌بست!")

    def _end_game(self, won):
        self._timer.stop()
        s = self.player.stats

        pid = get_or_create_player(self.player_name)
        save_record(pid, self.maze_size, s.steps, s.undos, s.hints_used, self._elapsed, won)

        overlay = EndOverlay(won, s, self._elapsed, self)
        overlay.setGeometry(self.rect())
        overlay.show()
        overlay.restart_requested.connect(self._go_menu)
        overlay.quit_requested.connect(QApplication.quit)
        self._overlay = overlay

    def _go_menu(self):
        self._timer.stop()
        self.back_to_menu.emit()

    def _go_records(self):
        self._timer.stop()
        win = self.window()
        win.records_page.name_filter.setText(self.player_name)
        win.records_page.load()
        win.stack.setCurrentIndex(1)

    def resizeEvent(self, e):
        if self._overlay:
            self._overlay.setGeometry(self.rect())
        super().resizeEvent(e)

    def showEvent(self, e):
        self.setFocus()
        super().showEvent(e)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("⬡ DEAD END — بازی هزارتو")
        self.setMinimumSize(760, 600)
        self.resize(1020, 740)
        self.setStyleSheet(BASE_STYLE)
        self._dark_titlebar()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.start_page = StartPage()
        self.start_page.start_requested.connect(self.start_game)
        self.stack.addWidget(self.start_page)

        self.records_page = RecordsPage()
        self.records_page.back_requested.connect(lambda: self.stack.setCurrentIndex(0))
        self.stack.addWidget(self.records_page)

    def _dark_titlebar(self):
        try:
            from ctypes import windll, c_int, byref, sizeof
            windll.dwmapi.DwmSetWindowAttribute(
                int(self.winId()), 20, byref(c_int(1)), sizeof(c_int)
            )
        except Exception:
            pass

    def start_game(self, size, player_name):
        maze = MazeGenerator(size)
        player = Player(maze)
        hint_engine = HintEngine(maze)

        while self.stack.count() > 2:
            w = self.stack.widget(2)
            self.stack.removeWidget(w)
            w.deleteLater()

        game = GamePage(maze, player, hint_engine, size, player_name)
        game.back_to_menu.connect(lambda: self.stack.setCurrentIndex(0))
        self.stack.addWidget(game)
        self.stack.setCurrentIndex(2)
        game.setFocus()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    p = QPalette()
    p.setColor(QPalette.Window, QColor(C['bg']))
    p.setColor(QPalette.WindowText, QColor(C['text']))
    p.setColor(QPalette.Base, QColor(C['bg2']))
    p.setColor(QPalette.AlternateBase, QColor(C['bg3']))
    p.setColor(QPalette.Button, QColor(C['bg3']))
    p.setColor(QPalette.ButtonText, QColor(C['text']))
    p.setColor(QPalette.Highlight, QColor(C['accent']))
    p.setColor(QPalette.HighlightedText, QColor(C['text_bright']))
    app.setPalette(p)
    MainWindow().show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
