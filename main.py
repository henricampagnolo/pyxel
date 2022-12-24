# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import pyxel
import enum
import time
import random
import collections


# Snake Direction labels
class Direction(enum.Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3


# game state labels
class GameState(enum.Enum):
    RUNNING = 0
    GAME_OVER = 1


# level class handled drawing the level (walls)
class Level:
    def __init__(self, x, y):
        self.tm = 0
        self.u = x
        self.v = y
        self.w = 192
        self.h = 128

    def draw(self):
        pyxel.bltm(0, 0, self.tm, self.u, self.v, self.w, self.h, 0)


# Apple class handle drawing the apple somewhere
# Checking if snake eat apple
class Apple:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8

    def draw(self):
        # where to draw on screen x and y; which sprite map, where on sprite map x and y, width and height
        pyxel.blt(self.x, self.y, 0, 16, 0, self.w, self.h, 0)

    def intersects(self, u, v, w, h):
        is_intersected = False
        if (
            u + w > self.x
            and self.x + self.w > u
            and v + h > self.y
            and self.y + self.h > v
        ):
            is_intersected = True
        return is_intersected

    def move(self, new_x, new_y):
        self.x = new_x
        self.y = new_y


# draw snake head
# detection
class SnakeSection:
    def __init__(self, x, y, is_head=False):
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8
        self.is_head = is_head

    def draw(self, direction):
        width = self.w
        height = self.h
        sprite_x = 0
        sprite_y = 0
        # if this is the head section we have to change and flip the sprite
        if self.is_head:
            if direction == Direction.RIGHT:
                sprite_x = 8
                sprite_y = 0
            if direction == Direction.LEFT:
                sprite_x = 8
                sprite_y = 0
                width = width*-1
            if direction == Direction.DOWN:
                sprite_x = 0
                sprite_y = 8
            if direction == Direction.UP:
                sprite_x = 0
                sprite_y = 8
                height = height*-1
        pyxel.blt(self.x, self.y, 0, sprite_x, sprite_y, width, height, 0)

    def intersects(self, u, v, w, h):
        is_intersected = False
        if (
            u + w > self.x
            and self.x + self.w > u
            and v + h > self.y
            and self.y + self.h > v
        ):
            is_intersected = True
        return is_intersected


# helper function for calculating the start x value for centered text
def center_text(text, page_width, char_width=pyxel.FONT_WIDTH):
    text_width = len(text) * char_width
    return (page_width - text_width) / 2


# helper function for calculating the start x value for right aligned text
def right_text(text, page_width, char_width=pyxel.FONT_WIDTH):
    text_width = len(text) * char_width
    return page_width - (text_width + char_width)


# draw hud
class Hud:
    def __init__(self):
        self.title_text = "Snake"
        self.title_text_x = center_text(self.title_text, 192)
        self.score_text = str(0)
        self.score_text_x = right_text(self.score_text, 192)
        self.level_text = "Level 0"
        self.level_text_x = 10
        self.apples_text = "Apples "
        self.apples_text_x = len(self.level_text) * pyxel.FONT_WIDTH + self.level_text_x + 5

    def draw_title(self):
        pyxel.rect(self.title_text_x - 1, 0, len(self.title_text) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.title_text_x, 1, self.title_text, 12)

    def draw_score(self, score):
        self.score_text = str(score)
        self.score_text_x = right_text(self.score_text, 192)
        pyxel.rect(self.score_text_x - 1, 0, len(self.score_text) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.score_text_x, 1, self.score_text, 3)

    def draw_level(self, level):
        pass
        

class App:
    def __init__(self):
        pyxel.init(192, 128, fps=60)
        pyxel.load("PYXEL_RESOURCE_FILE.pyxres")
        self.current_game_state = GameState.RUNNING
        self.level1 = Level(0, 0)
        self.level2 = Level(192, 0)
        self.hud = Hud()
        self.apple = Apple(64, 32)
        self.snake = []
        self.snake.append(SnakeSection(32, 64, is_head=True))
        self.snake.append(SnakeSection(24, 64))
        self.snake.append(SnakeSection(16, 64))
        self.snake_direction = Direction.RIGHT
        self.sections_to_add = 0
        self.speed = 5
        self.time_last_frame = time.time()
        self.dt = 0
        self.time_since_last_move = 0
        self.input_queue = collections.deque()
        pyxel.run(self.update, self.draw)

    def start_new_game(self):
        self.current_game_state = GameState.RUNNING
        self.snake.clear()
        # Add starting snake pieces
        self.snake.append(SnakeSection(32, 64, is_head=True))
        self.snake.append(SnakeSection(24, 64))
        self.snake.append(SnakeSection(16, 64))
        self.snake_direction = Direction.RIGHT
        self.sections_to_add = 0
        self.speed = 5
        self.time_last_frame = time.time()
        self.dt = 0
        self.time_since_last_move = 0
        self.input_queue.clear()
        self.apple = Apple(64, 32)

    def update(self):
        time_this_frame = time.time()
        self.dt = time_this_frame - self.time_last_frame
        self.time_last_frame = time_this_frame
        self.time_since_last_move += self.dt
        self.check_input()
        if self.current_game_state == GameState.RUNNING:
            if self.time_since_last_move >= 1 / self.speed:
                self.time_since_last_move = 0
                self.move_snake()
                self.check_collisions()

    def draw(self):
        pyxel.cls(0)
        self.level2.draw()
        self.level1.draw()
        self.apple.draw()
        for i in self.snake:
            i.draw(self.snake_direction)
        pyxel.text(10, 114, str(self.current_game_state), 2)
        self.hud.draw_title()

    def check_collisions(self):
        # Apple
        if self.apple.intersects(self.snake[0].x, self.snake[0].y, self.snake[0].w, self.snake[0].h):
            self.speed += (self.speed * 0.1)
            self.sections_to_add += 1
            self.move_apple()
        # Snake
        for i in self.snake:
            if i == self.snake[0]:
                continue
            if i.intersects(self.snake[0].x, self.snake[0].y, self.snake[0].w, self.snake[0].h):
                self.current_game_state = GameState.GAME_OVER
        # Wall
        if (
            pyxel.tilemap(0).pget(self.snake[0].x / 8, self.snake[0].y / 8)[0] == 3
            or pyxel.tilemap(0).pget(self.snake[0].x / 8, self.snake[0].y / 8)[0] == 4
        ):
            self.current_game_state = GameState.GAME_OVER

    def move_apple(self):
        # select new random location for apple
        good_position = False
        while not good_position:
            # where start, where end, interval
            new_x = random.randrange(8, 184, 8)
            new_y = random.randrange(8, 120, 8)
            good_position = True
            # check snake
            for i in self.snake:
                if (
                    new_x + 8 > i.x
                    and i.x + i.w > new_x
                    and new_y + 8 > i.y
                    and i.y + i.h > new_y
                ):
                    good_position = False
                    break
            # check wall
            if good_position:
                self.apple.move(new_x, new_y)

    def move_snake(self):
        # do we need to change direction
        if len(self.input_queue):
            self.snake_direction = self.input_queue.popleft()
        # do we need to grow the snake
        if self.sections_to_add > 0:
            self.snake.append(SnakeSection(self.snake[-1].x, self.snake[-1].y))
            self.sections_to_add -= 1
        # move the head
        previous_location_x = self.snake[0].x
        previous_location_y = self.snake[0].y
        if self.snake_direction == Direction.RIGHT:
            self.snake[0].x += self.snake[0].w
        if self.snake_direction == Direction.LEFT:
            self.snake[0].x -= self.snake[0].w
        if self.snake_direction == Direction.DOWN:
            self.snake[0].y += self.snake[0].h
        if self.snake_direction == Direction.UP:
            self.snake[0].y -= self.snake[0].h
        # move the tail
        for i in self.snake:
            if i == self.snake[0]:
                continue
            current_location_x = i.x
            current_location_y = i.y
            i.x = previous_location_x
            i.y = previous_location_y
            previous_location_x = current_location_x
            previous_location_y = current_location_y

    def check_input(self):
        if self.current_game_state == GameState.GAME_OVER:
            if pyxel.btn(pyxel.KEY_SPACE):
                self.start_new_game()
        if pyxel.btn(pyxel.KEY_RIGHT):
            if len(self.input_queue) == 0:
                if self.snake_direction != Direction.LEFT and self.snake_direction != Direction.RIGHT:
                    self.input_queue.append(Direction.RIGHT)
            else:
                if self.input_queue[-1] != Direction.LEFT and self.input_queue[-1] != Direction.RIGHT:
                    self.input_queue.append(Direction.RIGHT)
        elif pyxel.btn(pyxel.KEY_LEFT):
            if len(self.input_queue) == 0:
                if self.snake_direction != Direction.RIGHT and self.snake_direction != Direction.LEFT:
                    self.input_queue.append(Direction.LEFT)
            else:
                if self.input_queue[-1] != Direction.RIGHT and self.input_queue[-1] != Direction.LEFT:
                    self.input_queue.append(Direction.LEFT)
        elif pyxel.btn(pyxel.KEY_DOWN):
            if len(self.input_queue) == 0:
                if self.snake_direction != Direction.UP and self.snake_direction != Direction.DOWN:
                    self.input_queue.append(Direction.DOWN)
            else:
                if self.input_queue[-1] != Direction.UP and self.input_queue[-1] != Direction.DOWN:
                    self.input_queue.append(Direction.DOWN)
        elif pyxel.btn(pyxel.KEY_UP):
            if len(self.input_queue) == 0:
                if self.snake_direction != Direction.DOWN and self.snake_direction != Direction.UP:
                    self.input_queue.append(Direction.UP)
            else:
                if self.input_queue[-1] != Direction.DOWN and self.input_queue[-1] != Direction.UP:
                    self.input_queue.append(Direction.UP)


# Start our program
App()
