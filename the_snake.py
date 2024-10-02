# from abc import ABC, abstractmethod
from random import randrange
from typing import Type

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption("Змейка")

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:  # (ABC)
    """Абстрактный класс игрового объекта."""

    def __init__(self, body_color=None):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    # @abstractmethod
    def draw(self):
        """Абстрактный метод для отрисовки игровых объектов."""
        pass


class Snake(GameObject):
    """Cоздает игровой объект змейки."""

    def __init__(self):
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        super().__init__(SNAKE_COLOR)
        self.positions = [self.position]

    def add_tale(self):
        """Увеличивает длину змейки на 1 при съедании яблока."""
        self.length += 1
        self.positions.append(self.last)

    def draw(self):
        """Отрисовывает змейку на игровом поле
        и затирает хвост при перемещении.
        """
        for position in self.positions[:-1]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.get_head_position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    @property
    def get_head_position(self):
        """Получаем координаты головы змейки."""
        return self.positions[0]

    def move(self):
        """Перемещаем змейку на 1 ход вперед."""
        new_width = (
            self.get_head_position[0] + self.direction[0] * GRID_SIZE
        ) % SCREEN_WIDTH

        new_height = (
            self.get_head_position[1] + self.direction[1] * GRID_SIZE
        ) % SCREEN_HEIGHT

        self.positions.insert(0, (new_width, new_height))
        self.last = self.positions.pop()

    def reset(self):
        """Сбрасываем игру в начало при столкновении змейки с собой."""
        pass

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


class Apple(GameObject):
    """Создает игровой объект яблока."""

    def __init__(self):
        super().__init__(APPLE_COLOR)
        self.randomize_position()

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self):
        """Генерит рандомную координату расположения яблока."""
        self.position = (
            randrange(0, SCREEN_WIDTH, GRID_SIZE),
            randrange(0, SCREEN_HEIGHT, GRID_SIZE),
        )


def handle_keys(game_object: Type[Snake]) -> None:
    """Функция обработки действий пользователя."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основная логика игры 'змейка'."""
    # Инициализация PyGame:
    pygame.init()
    # Тут нужно создать экземпляры классов.
    snake = Snake()
    apple = Apple()

    while True:
        clock.tick(SPEED)

        # Тут опишите основную логику игры.
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        if snake.get_head_position == apple.position:
            snake.add_tale()
            apple.randomize_position()
        if snake.get_head_position in snake.positions[1:]:
            snake.reset()
        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == "__main__":
    main()
