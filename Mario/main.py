import pygame
from pygame import *

from blocks import Platform, PLATFORM_WIDTH, PLATFORM_HEIGHT, BlockDie, BlockTeleport, Princess, NextLevel
from monsters import *
from player import Player

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
DISPLAY = (WINDOW_WIDTH, WINDOW_HEIGHT)
BACKGROUND_COLOR = '#004400'

CURRENT_LEVEL = 1

FPS = 60
CLOCK = pygame.time.Clock()


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)


def camera_configure(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l + WINDOW_WIDTH / 2, -t + WINDOW_HEIGHT / 2  # Центрирование камеры относительно Марио

    l = min(0, l)  # Не движемся дальше левого края карты
    l = max(-(camera.width - WINDOW_WIDTH), l)  # Не движемся дальше правого края
    t = max(-(camera.height - WINDOW_HEIGHT), t)  # Не движемся дальше нижней части
    t = min(0, t)  # Не движемся дальше верхней части

    return Rect(l, t, w, h)


LEVELS = [[
    '-----------------------------------',
    '-                                 -',
    '-                                 -',
    '-          *           ---       N-',
    '-    --                         ---',
    '-                                 -',
    '-                *                -',
    '-             -----               -',
    '--                                -',
    '-                         -       -',
    '-       --                        -',
    '-                                 -',
    '-                 --------        -',
    '-                                 -',
    '-    -----                        -',
    '-                               ---',
    '-             --                  -',
    '-                       *         -',
    '-----------------------------------'
],
    [
        '-----------------------------------',
        '-                                 -',
        '-                                 -',
        '-          *           ---       P-',
        '-    --                         ---',
        '-                                 -',
        '-                *                -',
        '-             -----               -',
        '--                                -',
        '-                         -       -',
        '-       --                        -',
        '-                                 -',
        '-                 --------        -',
        '-                                 -',
        '-    -----                        -',
        '-                               ---',
        '-             --                  -',
        '-                       *         -',
        '-----------------------------------'
    ]
]


def run_game():
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY)
    pygame.display.set_caption('Mario')
    bg = Surface(DISPLAY)
    bg.fill(Color(BACKGROUND_COLOR))

    mario = Player(55, 55)
    left = False
    right = False
    up = False
    running = False

    entities = pygame.sprite.Group()
    animated_entities = pygame.sprite.Group()
    monsters = pygame.sprite.Group()
    platforms = list()

    def draw_platforms():
        """Отрисовка платформ"""
        entities.add(mario)

        def add_teleport(teleport):
            entities.add(teleport)
            platforms.append(teleport)
            animated_entities.add(teleport)

        def add_monster(monster):
            entities.add(monster)
            platforms.append(monster)
            monsters.add(monster)

        tp_1 = BlockTeleport(x=128, y=512, go_x=700, go_y=64)
        tp_2 = BlockTeleport(x=800, y=64, go_x=228, go_y=512)

        add_teleport(tp_1)
        add_teleport(tp_2)

        mn = Monster(200, 280, 2, 3, 150, 15)
        add_monster(mn)

        x, y = 0, 0
        for row in LEVELS[mario.current_level]:
            for symbol in row:
                if symbol == '-':
                    platform = Platform(x, y)
                    entities.add(platform)
                    platforms.append(platform)
                elif symbol == '*':
                    block_die = BlockDie(x, y)
                    entities.add(block_die)
                    platforms.append(block_die)
                elif symbol == 'N':
                    next_level_teleport = NextLevel(x, y)
                    entities.add(next_level_teleport)
                    platforms.append(next_level_teleport)
                    animated_entities.add(next_level_teleport)
                elif symbol == 'P':
                    princess = Princess(x, y)
                    entities.add(princess)
                    platforms.append(princess)
                    animated_entities.add(princess)

                x += PLATFORM_WIDTH
            x = 0
            y += PLATFORM_HEIGHT

    draw_platforms()
    total_level_width = len(LEVELS[mario.current_level][0]) * PLATFORM_WIDTH
    total_level_height = len(LEVELS[mario.current_level]) * PLATFORM_HEIGHT

    camera = Camera(camera_configure, total_level_width, total_level_height)

    while not mario.winner:
        if mario.current_level > 0 and mario.change_level:
            platforms.clear()
            entities.empty()
            animated_entities.empty()
            monsters.empty()
            draw_platforms()
            mario.change_level = False

        for event in pygame.event.get():
            if event.type == QUIT:
                raise SystemExit('QUIT')

            """Перемещение по Ох"""
            if event.type == KEYDOWN and event.key == K_LEFT:
                left = True
            elif event.type == KEYDOWN and event.key == K_RIGHT:
                right = True

            if event.type == KEYUP and event.key == K_LEFT:
                left = False
            elif event.type == KEYUP and event.key == K_RIGHT:
                right = False

            """Перемещение по Oy"""
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                up = True
            elif event.type == KEYUP and (event.key == K_SPACE or event.key == K_UP):
                up = False

            """Ускорение"""
            if event.type == KEYDOWN and event.key == K_LSHIFT:
                running = True
            elif event.type == KEYUP and event.key == K_LSHIFT:
                running = False

        screen.blit(bg, (0, 0))

        """Отрисовка персонажа"""
        camera.update(mario)
        mario.update(left, right, up, running, platforms)
        for ent in entities:
            screen.blit(ent.image, camera.apply(ent))

        CLOCK.tick(FPS)
        animated_entities.update()
        monsters.update(platforms)

        pygame.display.update()


if __name__ == '__main__':
    run_game()
