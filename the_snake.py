from random import choice
from typing import Optional, Union

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Все возможные ячейки для игрового поля
ALL_CELLS = set(
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Словарь для функции управления поворотом при нажатии клавиши:
TURNS = {
    (LEFT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_UP): UP,
    (RIGHT, pg.K_DOWN): DOWN,
    (UP, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_LEFT): LEFT,
    (DOWN, pg.K_RIGHT): RIGHT,
}

BOARD_BACKGROUND_COLOR = (180, 180, 180)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = "red"
FAKE_MEAL_COLOR = "yellow"
STONE_COLOR = "blue"
SNAKE_COLOR = "green"

# Скорость движения змейки:
SPEED = 7

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
screen.fill(BOARD_BACKGROUND_COLOR)

# Заголовок окна игрового поля:
pg.display.set_caption("Змейка. Для выхода нажми esc. Рекордная длина - 1")

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Абстрактный класс игрового объекта."""

    def __init__(self, body_color: Optional[Union[str, tuple[int]]] = None):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw(self):
        """Абстрактный метод для отрисовки игровых объектов."""
        raise NotImplementedError(
            f"класс {type(self).__name__} должен реализовывать метод "
            "draw(), проверьте его наличие"
        )

    def draw_cell(self, position, body_color=None) -> None:
        """Отрисовка объекта на игровом поле."""
        if not body_color:
            body_color = self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, body_color, rect)
        if body_color != BOARD_BACKGROUND_COLOR:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Cоздает игровой объект змейки."""

    def __init__(self, color: Optional[Union[str, tuple[int]]] = SNAKE_COLOR):
        super().__init__(color)
        self.reset()

    def add_tale(self):
        """Увеличивает длину змейки на 1 при съедании яблока."""
        self.length += 1
        self.positions.append(self.last)

    def draw(self):
        """Отрисовывает змейку на игровом поле
        и затирает хвост при перемещении.
        """
        # Отрисовка головы змейки
        self.draw_cell(self.get_head_position())
        # Затирание последнего сегмента
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)

    def get_head_position(self) -> tuple[int]:
        """Получаем координаты головы змейки."""
        return self.positions[0]

    def move(self):
        """Перемещаем змейку на 1 ход вперед."""
        width, height = self.get_head_position()
        dir_width, dir_height = self.direction

        self.positions.insert(
            0,
            (
                (width + dir_width * GRID_SIZE) % SCREEN_WIDTH,
                (height + dir_height * GRID_SIZE) % SCREEN_HEIGHT,
            ),
        )
        # Сохраняем хвост, чтобы затереть его
        self.last = self.positions.pop()

    def lose_tail(self):
        """Уменьшаем длину змейки на 1 при съедании неправильной еды."""
        self.length -= 1
        self.last = self.positions.pop()

    def reset(self):
        """Сбрасываем игру в начало при столкновении змейки с собой."""
        self.length = 1
        self.direction = RIGHT
        self.positions = [self.position]

    def update_direction(self, next_direction: tuple[int, int]):
        """Метод обновления направления после нажатия на кнопку."""
        self.direction = next_direction


class Apple(GameObject):
    """Создает игровой объект с одной ячейкой."""

    def __init__(
        self,
        color: Optional[Union[str, tuple[int]]] = APPLE_COLOR,
        occupied_positions: list[tuple[int, int]] = [],
    ):
        super().__init__(color)
        self.randomize_position(occupied_positions)

    def draw(self):
        """Отрисовывает игровой объект на игровом поле."""
        self.draw_cell(self.position)

    def randomize_position(
        self, occupied_positions: list[tuple[int, int]] = []
    ) -> None:
        """Генерит рандомную координату расположения игрового объекта."""
        self.draw_cell(self.position, BOARD_BACKGROUND_COLOR)
        self.position = choice(list(ALL_CELLS))
        while self.position in occupied_positions:
            self.position = choice(list(ALL_CELLS))


def handle_keys(snake: Snake) -> None:
    """Обрабатывает нажатие клавиш пользователя."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            snake.update_direction(
                TURNS.get((snake.direction, event.key), snake.direction)
            )
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit


def check_position(snake_instance, apple_instance,
                   fake_meal_instance, stone_instance):
    """Проверяем позиции игровых объектов на занятость"""
    apple_instance.randomize_position(
        occupied_positions=snake_instance.positions
        + [stone_instance.position, fake_meal_instance.position]
    )

    stone_instance.randomize_position(
        occupied_positions=snake_instance.positions
        + [apple_instance.position, fake_meal_instance.position]
    )
    fake_meal_instance.randomize_position(
        occupied_positions=snake_instance.positions
        + [apple_instance.position, stone_instance.position]
    )


def main():
    """Основная логика игры 'змейка'."""
    # Инициализация pygame:
    pg.init()

    # Инициализация игровых объектов
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)
    fake_meal = Apple(
        FAKE_MEAL_COLOR, occupied_positions=snake.positions + [apple.position]
    )
    stone = Apple(
        STONE_COLOR,
        occupied_positions=snake.positions
        + [apple.position, fake_meal.position],
    )
    max_length = 1

    while True:
        clock.tick(SPEED)

        # Получение команды от пользователя
        handle_keys(snake)
        # Передвижение змейки на 1 ячейку
        snake.move()

        # При съедании яблока змейка отращивает хвост и генерится новое яблоко
        if snake.get_head_position() == apple.position:
            snake.add_tale()
            # Координаты нового яблока не должны
            # совпадать с координатами других объектов
            check_position(snake, apple, fake_meal, stone)

        # При столкновении с собой или камнем
        # сбрасываем змейку к дефолтным параметрам
        elif (
            snake.get_head_position() in snake.positions[4:]
            or snake.get_head_position() == stone.position
        ):
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()
            check_position(snake, apple, fake_meal, stone)

        # При съедании фэйковой еды змейка
        # сбрасывает хвост и генерится новая еда
        elif snake.get_head_position() == fake_meal.position:
            if snake.length == 1:
                snake.reset()
            else:
                snake.draw()
                snake.lose_tail()
            check_position(snake, apple, fake_meal, stone)

        if snake.length > max_length:
            max_length = snake.length
            pg.display.set_caption(
                "Змейка. Для выхода нажми esc. "
                f"Рекордная длина - {max_length}"
            )

        # Отрисовка игровых объектов
        snake.draw()
        apple.draw()
        fake_meal.draw()
        stone.draw()
        pg.display.update()


if __name__ == "__main__":
    main()
