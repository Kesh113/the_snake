# from abc import ABC, abstractmethod
from random import randrange
from typing import Optional, Tuple

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
APPLE_COLOR = "red"

# Цвет неправильного корма
FAKE_MEAL_COLOR = "yellow"

# Цвет камня
STONE_COLOR = "grey"

# Цвет змейки
SNAKE_COLOR = "green"

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption("Змейка")

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:  # (ABC)
    """Абстрактный класс игрового объекта."""

    def __init__(self, body_color: Optional[Tuple[int]] = None):
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
        for position in self.positions:
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
    def get_head_position(self) -> Tuple[int]:
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
        # Сохраняем хвост, чтобы затереть его
        self.last = self.positions.pop()

    def lose_tail(self):
        """Уменьшаем длину змейки на 1 при съедании неправильной еды."""
        if self.length > 1:
            self.length -= 1
            last = self.positions.pop()
            last_rect = pygame.Rect(last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
        else:
            self.reset()

    def reset(self):
        """Сбрасываем игру в начало при столкновении змейки с собой."""
        for position in self.positions:  # Затираем старую змейку
            last_rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

        self.__init__()  # Получаем змейку с дефолтными параметрами

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


class Apple(GameObject):
    """Создает игровой объект с одной ячейкой."""

    def __init__(self, color="black"):
        super().__init__(color)
        self.randomize_position()

    def draw(self):
        """Отрисовывает игровой объект на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self):
        """Генерит рандомную координату расположения игрового объекта."""
        self.position = (
            randrange(0, SCREEN_WIDTH, GRID_SIZE),
            randrange(0, SCREEN_HEIGHT, GRID_SIZE),
        )


def handle_keys(
    game_object: Snake,
) -> None:
    """Обрабатывает нажатие клавиш пользователя."""
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


def change_settings():
    """Создает экраны настроек скорости и цвета игровых объектов."""
    font = pygame.font.Font(None, 36)

    def get_change(text, setting):
        """Выводит экран и редактирует настройки."""
        # Описание курсора ввода текста
        show_cursor = True
        cursor_timer = 0
        cursor_blink_rate = 500  # миллисекунды

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                elif event.type == pygame.KEYDOWN:
                    # При нажатии Enter происходит передача введенных данных
                    if event.key == pygame.K_RETURN:
                        return setting

                    # При нажатии Backspace удаляется последний символ
                    elif event.key == pygame.K_BACKSPACE:
                        setting = setting[:-1]
                    else:
                        setting += event.unicode  # Добавляем введенный символ

            # Описываем периодичность мерцания курсора
            cursor_timer += pygame.time.get_ticks() % cursor_blink_rate
            if cursor_timer >= cursor_blink_rate:
                show_cursor = not show_cursor
                cursor_timer = 0

            # Очистка экрана
            screen.fill(BOARD_BACKGROUND_COLOR)

            # Отображаем текст на экране
            text_surface = font.render(text, True, "white")
            screen.blit(text_surface, (20, 20))
            text_surface_setting = font.render(setting, True, "white")
            screen.blit(text_surface_setting, (len(text) * 14, 20))

            # Отображение и размещение курсора
            if show_cursor:
                cursor_x = text_surface_setting.get_width()
                cursor_height = font.get_height()
                pygame.draw.rect(
                    screen,
                    "white",
                    (len(text) * 14 + cursor_x, GRID_SIZE, 2, cursor_height),
                )

            pygame.display.update()
            # Задаем скорость мерцания курсора
            clock.tick(6)

    return (
        int(get_change("Введите скорость змейки: ", str(SPEED))),
        get_change("Введите цвет яблока: ", APPLE_COLOR),
        get_change("Введите цвет змейки: ", SNAKE_COLOR),
        get_change("Введите цвет камня: ", STONE_COLOR),
        get_change("Введите цвет 'неправильной' еды: ", FAKE_MEAL_COLOR),
    )


def main():
    """Основная логика игры 'змейка'."""
    # Инициализация PyGame:
    pygame.init()

    # Настройка скорости и цвета игровых объектов
    global SPEED, APPLE_COLOR, SNAKE_COLOR, STONE_COLOR, FAKE_MEAL_COLOR
    settings = change_settings()
    SPEED, APPLE_COLOR, SNAKE_COLOR, STONE_COLOR, FAKE_MEAL_COLOR = settings

    # Инициализация игровых объектов
    snake = Snake()
    apple = Apple(APPLE_COLOR)
    fake_meal = Apple(FAKE_MEAL_COLOR)
    stone = Apple(STONE_COLOR)

    while True:
        clock.tick(SPEED)
        screen.fill(BOARD_BACKGROUND_COLOR)

        # Получение команды от пользователя
        handle_keys(snake)
        # Изменение направления движения змейки
        snake.update_direction()
        # Передвижение змейки на 1 ячейку
        snake.move()

        # При съедании яблока змейка отращивает хвост и генерится новое яблоко
        if snake.get_head_position == apple.position:
            snake.add_tale()
            # Координаты нового яблока не должны
            # совпадать с координатами других объектов
            while apple.position in (
                snake.positions + [stone.position] + [fake_meal.position]
            ):
                apple.randomize_position()

        # Сбрасываем змейку к дефолтным параметрам при столкновении с собой
        elif snake.get_head_position in snake.positions[1:]:
            snake.reset()

        # Сбрасываем змейку к дефолтным параметрам при столкновении с камнем
        elif snake.get_head_position == stone.position:
            snake.reset()
            # Координаты нового камня не должны
            # совпадать с координатами других объектов
            while stone.position in (
                snake.positions + [apple.position] + [fake_meal.position]
            ):
                stone.randomize_position()

        # При съедании фэйковой еды змейка
        # сбрасывает хвост и генерится новая еда
        elif snake.get_head_position == fake_meal.position:
            snake.lose_tail()
            # Координаты новой фэйковой еды не должны
            # совпадать с координатами других объектов
            while fake_meal.position in (
                snake.positions + [apple.position] + [stone.position]
            ):
                fake_meal.randomize_position()
        print(snake.positions)
        # Отрисовка игровых объектов
        snake.draw()
        apple.draw()
        fake_meal.draw()
        stone.draw()
        pygame.display.update()


if __name__ == "__main__":
    main()
