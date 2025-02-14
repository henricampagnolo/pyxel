import pyxel
import time

TRANSPARENT_COLOR = 2
SCROLL_BORDER_X = 80
TILE_BLANK = (0, 0)
TILE_FLOOR = (1, 0)
TILE_SPAWN1 = (0, 1)
TILE_SPAWN2 = (1, 1)
TILE_SPAWN3 = (2, 1)
WALL_TILE_X = 4

m = 0
scroll_x = 0
player = None
enemies = []
item = []
weapons = []
projectiles = []
character = 0
items = 0
rot = 0


def get_tile(tile_x, tile_y):
    return pyxel.tilemap(0).pget(tile_x, tile_y)


def detect_collision(x, y, dy):
    x1 = x // 8
    y1 = y // 8
    x2 = (x + 8 - 1) // 8
    y2 = (y + 8 - 1) // 8
    for yi in range(y1, y2 + 1):
        for xi in range(x1, x2 + 1):
            if get_tile(xi, yi)[0] >= WALL_TILE_X:
                return True
    if dy > 0 and y % 8 == 1:
        for xi in range(x1, x2 + 1):
            if get_tile(xi, y1 + 1) == TILE_FLOOR:
                return True
    return False


def detect_collision2(x, y, dy):
    x1 = x // 8
    y1 = y // 8
    x2 = (x + 8 - 1) // 8
    y2 = (y + 8 - 1) // 8
    for yi in range(y1, y2 + 1):
        for xi in range(x1, x2 + 1):
            if get_tile(xi, yi)[0] >= WALL_TILE_X:
                return True
    return False


def push_back(x, y, dx, dy):
    abs_dx = abs(dx)
    abs_dy = abs(dy)
    if abs_dx > abs_dy:
        sign = 1 if dx > 0 else -1
        for _ in range(abs_dx):
            if detect_collision(x + sign, y, dy):
                break
            x += sign
        sign = 1 if dy > 0 else -1
        for _ in range(abs_dy):
            if detect_collision(x, y + sign, dy):
                break
            y += sign
    else:
        sign = 1 if dy > 0 else -1
        for _ in range(abs_dy):
            if detect_collision(x, y + sign, dy):
                break
            y += sign
        sign = 1 if dx > 0 else -1
        for _ in range(abs_dx):
            if detect_collision(x + sign, y, dy):
                break
            x += sign
    return x, y, dx, dy


def push_back2(x, y, dx, dy):
    abs_dx = abs(dx)
    abs_dy = abs(dy)
    if abs_dx > abs_dy:
        sign = 1 if dx > 0 else -1
        for _ in range(abs_dx):
            if detect_collision2(x + sign, y, dy):
                break
            x += sign
        sign = 1 if dy > 0 else -1
        for _ in range(abs_dy):
            if detect_collision2(x, y + sign, dy):
                break
            y += sign
    else:
        sign = 1 if dy > 0 else -1
        for _ in range(abs_dy):
            if detect_collision2(x, y + sign, dy):
                break
            y += sign
        sign = 1 if dx > 0 else -1
        for _ in range(abs_dx):
            if detect_collision2(x + sign, y, dy):
                break
            x += sign
    return x, y, dx, dy


def is_wall(x, y):
    tile = get_tile(x // 8, y // 8)
    return tile == TILE_FLOOR or tile[0] >= WALL_TILE_X


class Projectile:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.is_alive = True

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        u = pyxel.frame_count // 2 % 2 * 8 + 16
        pyxel.blt(self.x, self.y, 0, u, 128 + character * 8, 8, 8, TRANSPARENT_COLOR)


class ThrowingItem:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_alive = True

    def update(self):
        pass

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 0, 128 + character * 8, 8, 8, TRANSPARENT_COLOR)

    def delete(self):
        pyxel.tilemap(0).pset(self.x, self.y, TILE_BLANK)


def spawn_item(left_x, right_x):
    left_x = pyxel.ceil(left_x / 8)
    right_x = pyxel.floor(right_x / 8)
    for x in range(left_x, right_x + 1):
        for y in range(16):
            tile = get_tile(x, y)
            if tile == (1, 16):
                item.append(ThrowingItem(x * 8, y * 8))


def spawn_enemy(left_x, right_x):
    left_x = pyxel.ceil(left_x / 8)
    right_x = pyxel.floor(right_x / 8)
    for x in range(left_x, right_x + 1):
        for y in range(16):
            tile = get_tile(x, y)
            if tile == TILE_SPAWN1:
                enemies.append(Enemy1(x * 8, y * 8))
            elif tile == TILE_SPAWN2:
                enemies.append(Enemy2(x * 8, y * 8))
            elif tile == TILE_SPAWN3:
                enemies.append(Enemy3(x * 8, y * 8))
            elif tile == (0, 13):
                enemies.append(KillTiles(x * 8, y * 8 - 4))


class KillTiles:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_alive = True

    def update(self):
        pass

    def draw(self):
        pyxel.blt(self.x, self.y + 4, 0, 0, 104, 8, 8, TRANSPARENT_COLOR)


def cleanup_list(list):
    i = 0
    while i < len(list):
        elem = list[i]
        if elem.is_alive:
            i += 1
        else:
            list.pop(i)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.direction = 1
        self.is_falling = False

    def update(self):
        global scroll_x
        last_y = self.y

        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.dx = -2
            self.direction = -1
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.dx = 2
            self.direction = 1
        self.dy = min(self.dy + 1, 3)
        if pyxel.btnp(pyxel.KEY_SPACE) and (get_tile(self.x // 8, self.y // 8 + 1)[0] > 3 or get_tile(self.x // 8, self.y // 8 + 1) == TILE_FLOOR):
            self.dy = -8
        self.x, self.y, self.dx, self.dy = push_back(self.x, self.y, self.dx, self.dy)
        if self.x < scroll_x:
            self.x = scroll_x
        if self.y < 0:
            self.y = 0
        self.dx = int(self.dx * 0.8)
        self.is_falling = self.y > last_y

        if self.x > scroll_x + SCROLL_BORDER_X:
            last_scroll_x = scroll_x
            scroll_x = min(self.x - SCROLL_BORDER_X, 240 * 8)
            spawn_enemy(last_scroll_x + 128, scroll_x + 127)
            spawn_item(last_scroll_x + 128, scroll_x + 127)
        if self.y >= pyxel.height:
            game_over()

    def draw(self):
        u = (2 if self.is_falling else pyxel.frame_count // 3 % 2) * 8
        w = 8 if self.direction > 0 else -8
        pyxel.blt(self.x, self.y, 0, u, 16 + character * 13 * 8, w, 8, TRANSPARENT_COLOR)

    def throw(self):
        projectiles.append(Projectile(self.x, self.y, 5 * self.direction, 0))


class Enemy1:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.time = 40
        self.direction = -1
        self.is_alive = True

    def update(self):
        self.time += 1
        if self.time > 80:
            self.dy -= 12
            self.time = 0
        self.dy = min(self.dy + 1, 3)
        self.x, self.y, self.dx, self.dy = push_back2(self.x, self.y, self.dx, self.dy)

    def draw(self):
        u = pyxel.frame_count // 4 % 2 * 8
        w = 8 if self.direction > 0 else -8
        pyxel.blt(self.x, self.y, 0, u, 24, w, 8, TRANSPARENT_COLOR)


class Enemy2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.direction = -1
        self.is_alive = True

    def update(self):
        self.dx = self.direction
        self.dy = min(self.dy + 1, 3)
        if is_wall(self.x, self.y + 8) or is_wall(self.x + 7, self.y + 8):
            if self.direction < 0 and (
                is_wall(self.x - 1, self.y + 4) or not is_wall(self.x - 1, self.y + 8)
            ):
                self.direction = 1
            elif self.direction > 0 and (
                is_wall(self.x + 8, self.y + 4) or not is_wall(self.x + 7, self.y + 8)
            ):
                self.direction = -1
        self.x, self.y, self.dx, self.dy = push_back(self.x, self.y, self.dx, self.dy)

    def draw(self):
        u = pyxel.frame_count // 4 % 2 * 8 + 16
        w = 8 if self.direction > 0 else -8
        pyxel.blt(self.x, self.y, 0, u, 24, w, 8, TRANSPARENT_COLOR)


class Enemy3:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.time_to_fire = 0
        self.is_alive = True

    def update(self):
        self.time_to_fire -= 1
        if self.time_to_fire <= 0:
            dx = player.x - self.x
            dy = player.y - self.y
            sq_dist = dx * dx + dy * dy
            if sq_dist < 60**2:
                dist = pyxel.sqrt(sq_dist)
                enemies.append(Enemy3Bullet(self.x, self.y, dx / dist, dy / dist))
                self.time_to_fire = 60

    def draw(self):
        u = pyxel.frame_count // 8 % 2 * 8
        pyxel.blt(self.x, self.y, 0, u, 32, 8, 8, TRANSPARENT_COLOR)


class Enemy3Bullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.is_alive = True

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        u = pyxel.frame_count // 6 % 4 * 8
        pyxel.blt(self.x, self.y, 0, u, 56, 8, 8, TRANSPARENT_COLOR)


class App:
    def __init__(self):
        pyxel.init(128, 128, title="Pyxel Platformer", fps=30)
        pyxel.load("assets.pyxres")

        # Variables

        # Change enemy spawn tiles invisible
        pyxel.image(0).rect(0, 8, 24, 8, TRANSPARENT_COLOR)

        global player
        player = Player(0, 0)
        spawn_enemy(0, 127)
        spawn_item(0, 127)
        pyxel.playm(0, loop=True)
        pyxel.run(self.update, self.draw)

    def update(self):
        global items
        global character

        if pyxel.btnp(pyxel.KEY_S):
            global character
            if character == 0:
                character = 1
            else:
                character = 0

        if pyxel.btnp(pyxel.KEY_E) and items > 0:
            player.throw()
            items -= 1

        player.update()

        for enemy in enemies:
            if abs(player.x - enemy.x) < 6 and abs(player.y - enemy.y) < 6:
                game_over()
                return
            enemy.update()
            if enemy.x < scroll_x - 8 or enemy.x > scroll_x + 160 or enemy.y > 160:
                enemy.is_alive = False
        for thing in item:
            if abs(player.x - thing.x) < 6 and abs(player.y - thing.y) < 6:
                thing.is_alive = False
                items += 1
                thing.delete()
            if thing.x < scroll_x - 8 or thing.x > scroll_x + 160 or thing.y > 160:
                thing.is_alive = False
                thing.delete()
        for proj in projectiles:
            proj.update()
            for enemy in enemies:
                if abs(enemy.x - proj.x) < 6 and abs(enemy.y - proj.y) < 6:
                    enemy.is_alive = False
            if proj.x < scroll_x - 8 or proj.x > scroll_x + 160 or proj.y > 160:
                proj.is_alive = False
        cleanup_list(projectiles)
        cleanup_list(enemies)
        cleanup_list(item)
        if rot == 1:
            game_win()

    def draw(self):
        global character, rot
        pyxel.cls(0)

        # Draw level
        pyxel.camera()
        pyxel.bltm(0, 0, 0, (scroll_x // 4) % 128, 128, 128, 128)
        pyxel.bltm(0, 0, 0, scroll_x, 256, 128, 128, TRANSPARENT_COLOR)
        pyxel.bltm(0, 0, 0, scroll_x, 0, 128, 128, TRANSPARENT_COLOR)

        # Draw characters
        pyxel.camera(scroll_x, 0)
        player.draw()
        for enemy in enemies:
            enemy.draw()
        for thing in item:
            thing.draw()
        for proj in projectiles:
            proj.draw()
        pyxel.rect(scroll_x, 1 - character, 36, 8 + 2 * character, 7)
        pyxel.blt(scroll_x + 1, character, 0, 0, 128 + character * 8, 8, 8, TRANSPARENT_COLOR)
        pyxel.text(scroll_x+ 12, 3, str(items) + " AMMO", 0)

        if get_tile(player.x // 8, player.y // 8) == (0, 18) or get_tile(player.x // 8, player.y // 8) == (1, 18):
            pyxel.bltm(scroll_x, 0, 0, 0, 384, 128, 128, TRANSPARENT_COLOR)
            rot = 1


def game_win():
    pyxel.stop()
    pyxel.play(3, 8)
    time.sleep(4)
    pyxel.quit()


def game_over():
    pyxel.stop()
    pyxel.play(3, 10)
    global scroll_x, enemies, items
    scroll_x = 0
    player.x = 0
    player.y = 0
    player.dx = 0
    player.dy = 0
    items = 0
    enemies = []
    spawn_enemy(0, 127)
    spawn_item(0, 127)
    pyxel.playm(0, loop=True)


App()

