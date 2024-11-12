import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QRectF, QTimer

CELL_SIZE = 20  # Բջիջի չափս
GRID_SIZE = 21  # Ցանցի չափս
ANIMATION_STEP = 2  #Քայլի չափս

class Labirint(QMainWindow):
    def __init__(self):
        super().__init__()

        # Պատուհան
        self.setWindowTitle("ԼԱԲԻՐԻՆՏ")
        self.setFixedSize(GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE)

        # Լաբիրինտի չափսեր և
        self.labirint = self.generate_labirint(GRID_SIZE, GRID_SIZE)
        self.player_pos = [1, 1]  # Սկզբնական կորդինատ
        self.exit_pos = [GRID_SIZE - 2, GRID_SIZE - 2]  # Վերջի կոորդինատ

        # Ճանապարհ
        self.path = self.find_path(self.player_pos, self.exit_pos)
        self.current_step = 0
        self.progress_in_cell = 0

        # Խաղացողի կոորդինատը
        self.current_pos = [self.player_pos[0] * CELL_SIZE, self.player_pos[1] * CELL_SIZE]

        # Քայլի սահունություն
        self.timer = QTimer()
        self.timer.timeout.connect(self.move_player)
        self.timer.start(30)  # 30 մվ

    def generate_labirint(self, width, height):

        maze = [[1 for _ in range(width)] for _ in range(height)]

        def dfs(x, y):
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 1 <= nx < width - 1 and 1 <= ny < height - 1 and maze[ny][nx] == 1:
                    maze[y + dy // 2][x + dx // 2] = 0
                    maze[ny][nx] = 0
                    dfs(nx, ny)

        maze[1][1] = 0
        dfs(1, 1)

        for _ in range(int(width * height * 0.1)):
            x, y = random.randint(1, width - 2), random.randint(1, height - 2)
            if maze[y][x] == 1:
                maze[y][x] = 0

        return maze

    def find_path(self, start, end):
        # Ճանապարհի որոնում
        queue = [(start, [start])]
        visited = set()

        while queue:
            (x, y), path = queue.pop(0)
            if (x, y) == tuple(end):
                return path

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in visited:
                    if self.labirint[ny][nx] == 0:
                        queue.append(((nx, ny), path + [(nx, ny)]))
                        visited.add((nx, ny))
        return []

    def move_player(self):
        if self.current_step < len(self.path) - 1:
            start_x, start_y = self.path[self.current_step]
            target_x, target_y = self.path[self.current_step + 1]

            direction_x = (target_x - start_x) * ANIMATION_STEP
            direction_y = (target_y - start_y) * ANIMATION_STEP
            self.current_pos[0] += direction_x
            self.current_pos[1] += direction_y

            distance_x = abs(self.current_pos[0] - target_x * CELL_SIZE)
            distance_y = abs(self.current_pos[1] - target_y * CELL_SIZE)

            if distance_x < ANIMATION_STEP and distance_y < ANIMATION_STEP:
                self.current_pos = [target_x * CELL_SIZE, target_y * CELL_SIZE]
                self.current_step += 1

            self.update()
        else:
            print("Player has reached the exit!")
            self.timer.stop()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)

        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = QRectF(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if self.labirint[y][x] == 1:
                    qp.fillRect(rect, QColor(50, 50, 50))  # Պատեր
                else:
                    qp.fillRect(rect, QColor(240, 240, 240))  # Դատարկ վանդակներ
                pen = QPen(Qt.GlobalColor.black)
                pen.setWidth(1)
                qp.setPen(pen)
                qp.drawRect(rect)

        #Խաղացող
        player_rect = QRectF(
            self.current_pos[0] + CELL_SIZE * 0.1,
            self.current_pos[1] + CELL_SIZE * 0.1,
            CELL_SIZE * 0.8, CELL_SIZE * 0.8
        )
        qp.setBrush(QColor(0, 255, 0))
        qp.drawEllipse(player_rect)

        # Ավարտ
        exit_rect = QRectF(
            self.exit_pos[0] * CELL_SIZE,
            self.exit_pos[1] * CELL_SIZE,
            CELL_SIZE, CELL_SIZE
        )
        qp.setBrush(QColor(255, 0, 0))
        qp.drawRect(exit_rect)

        qp.end()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = Labirint()
    game.show()
    sys.exit(app.exec())