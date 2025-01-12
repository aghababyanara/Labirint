import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QRectF, QTimer


class Labirint(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LABIRINT")
        self.showFullScreen()

        screen = QApplication.primaryScreen()
        self.screen_size = screen.size()

        self.cell_size = 15
        self.grid_width = self.screen_size.width() // self.cell_size
        self.grid_height = self.screen_size.height() // self.cell_size

        self.grid_width -= self.grid_width % 2
        self.grid_height -= self.grid_height % 2

        self.layout = QVBoxLayout()
        self.reset_button = QPushButton("START AGAIN")
        self.reset_button.setStyleSheet("background-color: #4CAF50;")
        self.reset_button.clicked.connect(self.reset_game)
        self.reset_button.setVisible(False)
        self.layout.addWidget(self.reset_button)

        container = QWidget()
        container.setLayout(self.layout)
        self.setMenuWidget(container)

        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)

        self.elapsed_time = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.move_player)
        self.slowdown_timer = 0
        self.timer.start(30)


        self.initial_speed = 0.5
        self.speed_multiplier = self.initial_speed
        self.slowdown_rate = 0.98
        self.reset_game()

    def reset_game(self):
        self.player_pos = [1, 1]
        self.labirint = self.generate_labirint(self.grid_width, self.grid_height)

        self.exit_pos = self.find_valid_exit_position()
        self.path = self.find_path(self.player_pos, self.exit_pos)
        self.current_step = 0
        self.current_pos = [self.player_pos[0] * self.cell_size, self.player_pos[1] * self.cell_size]
        self.cacti = self.place_cacti()
        self.slowdown_timer = 0
        self.speed_multiplier = self.initial_speed
        self.timer.start(30)
        self.reset_button.setVisible(False)

    def update_time(self):
        self.elapsed_time += 1
        self.update()

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
        return maze

    def find_valid_exit_position(self):
        while True:
            exit_x = random.randint(1, self.grid_width - 2)
            exit_y = random.randint(1, self.grid_height - 2)
            if self.labirint[exit_y][exit_x] == 0:
                path = self.find_path(self.player_pos, [exit_x, exit_y])
                if path:
                    return [exit_x, exit_y]

    def find_path(self, start, end):
        queue = [(start, [start])]
        visited = set()

        while queue:
            (x, y), path = queue.pop(0)
            if (x, y) == tuple(end):
                return path

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height and (nx, ny) not in visited:
                    if self.labirint[ny][nx] == 0:
                        queue.append(((nx, ny), path + [(nx, ny)]))
                        visited.add((nx, ny))
        return []

    def place_cacti(self):
        cacti = []
        num_cacti = int(self.grid_width * self.grid_height * 0.05)

        path_length = len(self.path)
        cacti_on_path = min(num_cacti // 10, path_length // 10)
        path_indices = random.sample(range(1, path_length - 1), cacti_on_path)

        for index in path_indices:
            x, y = self.path[index]
            cacti.append((x, y))
            self.labirint[y][x] = 2

        while len(cacti) < num_cacti:
            x, y = random.randint(1, self.grid_width - 2), random.randint(1, self.grid_height - 2)
            if self.labirint[y][x] == 0 and (x, y) not in self.path and (x, y) != tuple(self.player_pos) and (x, y) != tuple(self.exit_pos):
                cacti.append((x, y))
                self.labirint[y][x] = 2

        return cacti

    def move_player(self):
        if self.slowdown_timer > 0:
            self.slowdown_timer -= 1
            self.speed_multiplier = min(self.initial_speed, self.speed_multiplier * 1.03)
            return

        if self.current_step < len(self.path) - 1:
            target_x, target_y = self.path[self.current_step + 1]

            if (target_x, target_y) in self.cacti:
                print("MEET CACTI")
                self.slowdown_timer = 30
                self.speed_multiplier = 0.65

            direction_x = (target_x * self.cell_size - self.current_pos[0]) * self.speed_multiplier
            direction_y = (target_y * self.cell_size - self.current_pos[1]) * self.speed_multiplier

            self.current_pos[0] += direction_x
            self.current_pos[1] += direction_y

            distance_x = abs(self.current_pos[0] - target_x * self.cell_size)
            distance_y = abs(self.current_pos[1] - target_y * self.cell_size)

            if distance_x < 2 and distance_y < 2:
                self.current_pos = [target_x * self.cell_size, target_y * self.cell_size]
                self.current_step += 1

            self.update()
        else:
            print("LABIRINT IS SOLVED")
            self.timer.stop()
            self.reset_button.setVisible(True)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                rect = QRectF(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                if self.labirint[y][x] == 1:
                    qp.fillRect(rect, QColor(50, 50, 50))
                elif self.labirint[y][x] == 2:
                    qp.fillRect(rect, QColor(0, 128, 0))
                else:
                    qp.fillRect(rect, QColor(240, 240, 240))
                qp.setPen(QPen(Qt.GlobalColor.black))
                qp.drawRect(rect)

        player_rect = QRectF(
            self.current_pos[0] + self.cell_size * 0.1,
            self.current_pos[1] + self.cell_size * 0.1,
            self.cell_size * 0.8,
            self.cell_size * 0.8
        )
        qp.setBrush(QColor(0, 255, 0))
        qp.drawEllipse(player_rect)

        exit_rect = QRectF(
            self.exit_pos[0] * self.cell_size,
            self.exit_pos[1] * self.cell_size,
            self.cell_size,
            self.cell_size
        )
        qp.setBrush(QColor(255, 0, 0))
        qp.drawRect(exit_rect)

        font = qp.font()
        font.setPointSize(20)
        qp.setFont(font)
        qp.setPen(QPen(Qt.GlobalColor.red))
        qp.drawText(10, 30, f"Time: {self.elapsed_time} sec")

        qp.end()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = Labirint()
    game.show()
    sys.exit(app.exec())
